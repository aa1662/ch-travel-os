#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CH Travel OS 2.0 - 讀者點讚與私密留言後端服務 (Reader Feedback Service)
- 本機持久化 SQLite 儲存 (.local_data/reader_feedback.db)
- 冪等點讚與防重試重複留言
- 嚴格限定受許可之白名單文章 (Stable Article ID: <trip>:<entry_id>)
- 本機作者入口受 Session Token 保護，訪客無權存取私密留言與管理 API
- 留言純文字安全儲存，不紀錄個人敏感資料與裝置指紋
"""

import os
import re
import json
import time
import uuid
import hmac
import secrets
import sqlite3
import datetime
from contextlib import closing
from pathlib import Path

try:
    from .feedback_eligibility import feedback_eligible
except ImportError:
    from feedback_eligibility import feedback_eligible

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DATA_DIR = BASE_DIR / ".local_data"
DEFAULT_DB_PATH = DEFAULT_DATA_DIR / "reader_feedback.db"
DEFAULT_SECRET_PATH = DEFAULT_DATA_DIR / "author_secret.json"
DEFAULT_TRIPS_DIR = BASE_DIR / "trips"

class FeedbackConflictError(ValueError):
    pass


class ClosingConnection(sqlite3.Connection):
    def __exit__(self, *args):
        try:
            return super().__exit__(*args)
        finally:
            self.close()


class FeedbackService:
    def __init__(self, db_path=None, secret_path=None, trips_dir=None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.secret_path = Path(secret_path) if secret_path else DEFAULT_SECRET_PATH
        self.trips_dir = Path(trips_dir) if trips_dir else DEFAULT_TRIPS_DIR
        self._init_storage()
        self._migrate_inbox()

    def _migrate_inbox(self):
        """Add inbox state without changing reader records; backup uses SQLite's snapshot API."""
        with self._get_connection() as conn:
            version = conn.execute("PRAGMA user_version").fetchone()[0]
            if version > 1:
                raise RuntimeError("Unsupported feedback schema version")
            if version == 1:
                return
            backup_dir = self.db_path.parent / "backups"
            backup_dir.mkdir(exist_ok=True)
            backup = backup_dir / f"{self.db_path.stem}-before-inbox-{uuid.uuid4().hex}.db"
            with closing(sqlite3.connect(backup)) as target:
                conn.backup(target)
            conn.execute("BEGIN IMMEDIATE")
            columns = {row[1] for row in conn.execute("PRAGMA table_info(messages)")}
            additions = {
                "status": "TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','in_progress','done'))",
                "author_note": "TEXT NOT NULL DEFAULT ''",
                "version": "INTEGER NOT NULL DEFAULT 0",
            }
            for name, definition in additions.items():
                if name not in columns:
                    conn.execute(f"ALTER TABLE messages ADD COLUMN {name} {definition}")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_status_created ON messages(status, created_at DESC, id DESC)")
            conn.execute("PRAGMA user_version = 1")
            conn.commit()

    def _get_connection(self):
        conn = sqlite3.connect(str(self.db_path), timeout=10.0, check_same_thread=False, factory=ClosingConnection)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_storage(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.secret_path.parent.mkdir(parents=True, exist_ok=True)

        # 確保作者預設本機金鑰存在
        if not self.secret_path.exists():
            payload = {
                "passcode": secrets.token_urlsafe(32),
                "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "description": "CH Travel OS 本機作者管理入口憑證（僅供本機開發驗證，嚴禁進入 Git）"
            }
            self.secret_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 1. 讀者點讚資料表：以 (article_id, client_id) 為主鍵，冪等更新 active 狀態
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS likes (
                    article_id TEXT NOT NULL,
                    client_id TEXT NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY (article_id, client_id)
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_likes_article_active ON likes (article_id, active)")

            # 2. 讀者私密留言表：純文字儲存，client_submission_id 防重試重複寫入
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    article_id TEXT NOT NULL,
                    client_id TEXT NOT NULL,
                    client_submission_id TEXT NOT NULL,
                    nickname TEXT,
                    content TEXT NOT NULL,
                    is_read INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    UNIQUE (article_id, client_submission_id)
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_article_created ON messages (article_id, created_at DESC)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_is_read ON messages (article_id, is_read)")

            # 3. 基礎請求限流表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rate_limits (
                    client_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_rate_limits_lookup ON rate_limits (client_id, action, timestamp)")

            # 4. 作者受保護的管理 Session 表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS author_sessions (
                    token TEXT PRIMARY KEY,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL
                )
            """)
            conn.commit()

    # ==========================================
    # 文章資格白名單 (Article Eligibility SSoT)
    # ==========================================
    def get_eligible_articles(self):
        """
        動態掃描 trips/*/blog-migration.json，僅開放設定 feedback: true 的文章。
        固定 Article ID 規範：<trip_slug>:<entry_id>，絕不隨 URL 或標題更動。
        """
        eligible = {}
        if not self.trips_dir.exists():
            return eligible

        for trip_dir in sorted(self.trips_dir.iterdir()):
            if not trip_dir.is_dir():
                continue
            cfg_file = trip_dir / "blog-migration.json"
            if not cfg_file.exists():
                continue
            try:
                data = json.loads(cfg_file.read_text(encoding="utf-8"))
            except Exception:
                continue

            trip_slug = trip_dir.name
            dest_slug = data.get("dest", trip_slug)
            for entry in data.get("entries", []):
                if feedback_eligible(entry, trip_slug, dest_slug):
                    article_id = f"{trip_slug}:{entry['id']}"
                    eligible[article_id] = {
                        "article_id": article_id,
                        "trip": trip_slug,
                        "entry_id": entry["id"],
                        "title": entry.get("title", ""),
                        "output": entry.get("output", f"docs/{dest_slug}/blog/{entry['id']}.html"),
                        "dest": dest_slug,
                    }
        return eligible

    def is_eligible(self, article_id):
        return article_id in self.get_eligible_articles()

    # ==========================================
    # 限流檢查 (Rate Limiting)
    # ==========================================
    def check_rate_limit(self, client_id, action, limit=10, window=60):
        now = time.time()
        window_start = now - window
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM rate_limits WHERE timestamp < ?",
                (window_start - 300,)
            )
            cursor.execute(
                "SELECT COUNT(*) FROM rate_limits WHERE client_id = ? AND action = ? AND timestamp >= ?",
                (client_id, action, window_start)
            )
            count = cursor.fetchone()[0]
            if count >= limit:
                return False
            cursor.execute(
                "INSERT INTO rate_limits (client_id, action, timestamp) VALUES (?, ?, ?)",
                (client_id, action, now)
            )
            conn.commit()
            return True

    # ==========================================
    # 讀者端操作 (Reader APIs)
    # ==========================================
    def get_reader_status(self, article_id, client_id):
        """查詢讀者本人的點讚狀態（不對外洩露總讚數或他人私密留言）"""
        if not self.is_eligible(article_id):
            raise ValueError(f"未知或未開放回饋的文章: {article_id}")
        if not client_id or not isinstance(client_id, str) or len(client_id) > 64:
            raise ValueError("無效的讀者識別碼")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT active FROM likes WHERE article_id = ? AND client_id = ?",
                (article_id, client_id)
            )
            row = cursor.fetchone()
            liked = bool(row and row["active"] == 1)
            return {"success": True, "article_id": article_id, "liked": liked}

    def toggle_like(self, article_id, client_id, action):
        """
        冪等點讚/取消操作。
        重試或重複點擊同動作不會導致讚數重複增減。
        """
        if not self.is_eligible(article_id):
            raise ValueError(f"未知或未開放回饋的文章: {article_id}")
        if not client_id or not isinstance(client_id, str) or len(client_id) > 64:
            raise ValueError("無效的讀者識別碼")
        if action not in ("like", "unlike"):
            raise ValueError("無效的點讚動作 (需為 like 或 unlike)")

        if not self.check_rate_limit(client_id, "like", limit=30, window=60):
            raise PermissionError("請求過於頻繁，請稍後再試")

        active_val = 1 if action == "like" else 0
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO likes (article_id, client_id, active, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(article_id, client_id) DO UPDATE SET
                    active = excluded.active,
                    updated_at = excluded.updated_at
            """, (article_id, client_id, active_val, now_iso, now_iso))
            conn.commit()

        return {
            "success": True,
            "article_id": article_id,
            "liked": active_val == 1
        }

    def submit_message(self, article_id, client_id, client_submission_id, nickname, content):
        """
        送出私密留言：
        - 獨立於點讚（無需先按讚）
        - 暱稱選填（最多 40 字）
        - 不收 Email、不提供附件
        - 留言長度 1~1000 字，純空白不得送出
        - client_submission_id 確保重試不重複收件
        """
        if not self.is_eligible(article_id):
            raise ValueError(f"未知或未開放回饋的文章: {article_id}")
        if not client_id or not isinstance(client_id, str) or len(client_id) > 64:
            raise ValueError("無效的讀者識別碼")
        if not client_submission_id or not isinstance(client_submission_id, str) or len(client_submission_id) > 64:
            raise ValueError("無效的提交識別碼")

        if not self.check_rate_limit(client_id, "message", limit=10, window=60):
            raise PermissionError("留言發送過於頻繁，請稍後再試")

        # 暱稱驗證與清理
        clean_nickname = None
        if nickname is not None:
            clean_nickname = str(nickname).strip()
            if len(clean_nickname) > 40:
                raise ValueError("暱稱長度不得超過 40 個字元")
            if not clean_nickname:
                clean_nickname = None

        # 留言內容驗證（必填 1~1000 字）
        if not content or not isinstance(content, str):
            raise ValueError("請輸入留言內容")
        clean_content = content.strip()
        if len(clean_content) < 1:
            raise ValueError("留言內容不得為純空白")
        if len(clean_content) > 1000:
            raise ValueError("留言長度不得超過 1000 個字元")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 檢查重試防重複收件
            cursor.execute(
                "SELECT id, created_at FROM messages WHERE article_id = ? AND client_submission_id = ?",
                (article_id, client_submission_id)
            )
            existing = cursor.fetchone()
            if existing:
                return {
                    "success": True,
                    "message_id": existing["id"],
                    "created_at": existing["created_at"],
                    "duplicate_prevented": True
                }

            msg_id = f"msg_{uuid.uuid4().hex[:16]}"
            now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

            cursor.execute("""
                INSERT INTO messages (id, article_id, client_id, client_submission_id, nickname, content, is_read, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 0, ?)
            """, (msg_id, article_id, client_id, client_submission_id, clean_nickname, clean_content, now_iso))
            conn.commit()

        return {
            "success": True,
            "message_id": msg_id,
            "created_at": now_iso
        }

    # ==========================================
    # 作者管理端操作 (Author Management APIs)
    # ==========================================
    def get_author_passcode(self):
        try:
            data = json.loads(self.secret_path.read_text(encoding="utf-8"))
            value = data.get("passcode")
            if not isinstance(value, str) or not value:
                raise RuntimeError("Author credential unavailable")
            return value
        except Exception:
            raise RuntimeError("Author credential unavailable") from None

    def author_login(self, passcode):
        """以本機 Passcode 驗證作者身分並頒發短期 Session Token"""
        if not self.check_rate_limit("author-login", "login", limit=10, window=60):
            raise PermissionError("登入嘗試過於頻繁，請稍後再試")
        real_passcode = self.get_author_passcode()
        if not hmac.compare_digest(str(passcode or ""), str(real_passcode)):
            raise PermissionError("管理密碼不正確")

        token = secrets.token_hex(32)
        now = time.time()
        expires_at = now + 86400  # 24 小時

        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 清理過期 Session
            cursor.execute("DELETE FROM author_sessions WHERE expires_at < ?", (now,))
            cursor.execute(
                "INSERT INTO author_sessions (token, created_at, expires_at) VALUES (?, ?, ?)",
                (token, now, expires_at)
            )
            conn.commit()

        return {"success": True, "token": token, "expires_at": expires_at}

    def verify_author_token(self, token):
        if not token or not isinstance(token, str):
            return False
        now = time.time()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT expires_at FROM author_sessions WHERE token = ?",
                (token,)
            )
            row = cursor.fetchone()
            if row and row["expires_at"] > now:
                return True
        return False

    def get_author_summary(self, token):
        """作者總覽：列出受許可文章、各篇讚數與留言數量"""
        if not self.verify_author_token(token):
            raise PermissionError("未授權的管理請求，請先登入")

        eligible = self.get_eligible_articles()
        summary_list = []

        with self._get_connection() as conn:
            cursor = conn.cursor()
            for article_id, meta in eligible.items():
                cursor.execute(
                    "SELECT COUNT(*) FROM likes WHERE article_id = ? AND active = 1",
                    (article_id,)
                )
                likes_count = cursor.fetchone()[0]

                cursor.execute(
                    "SELECT COUNT(*) FROM messages WHERE article_id = ?",
                    (article_id,)
                )
                total_msgs = cursor.fetchone()[0]

                cursor.execute(
                    "SELECT COUNT(*) FROM messages WHERE article_id = ? AND is_read = 0",
                    (article_id,)
                )
                unread_msgs = cursor.fetchone()[0]

                summary_list.append({
                    "article_id": article_id,
                    "title": meta["title"],
                    "trip": meta["trip"],
                    "output": meta["output"],
                    "likes_count": likes_count,
                    "total_messages": total_msgs,
                    "unread_messages": unread_msgs,
                })

        return {"success": True, "articles": summary_list}

    def get_author_messages(self, token, article_id=None, *, trip=None, q="", status="all", unread="0", page=1, page_size=20):
        """作者讀取私密留言清單（依時間新到舊排序）"""
        if not self.verify_author_token(token):
            raise PermissionError("未授權的管理請求，請先登入")

        eligible = self.get_eligible_articles()
        if article_id and article_id not in eligible:
            raise ValueError(f"未知或未開放回饋的文章: {article_id}")

        if status not in ("pending", "in_progress", "done", "all"):
            raise ValueError("無效的處理狀態")
        if not isinstance(q, str) or len(q) > 200:
            raise ValueError("搜尋文字不得超過 200 字")
        if unread not in ("0", "1"):
            raise ValueError("無效的未讀條件")
        try:
            page, page_size = int(page), int(page_size)
        except (TypeError, ValueError):
            raise ValueError("無效的頁碼") from None
        if page < 1 or page_size < 1 or page_size > 100:
            raise ValueError("無效的頁碼或每頁筆數")
        if trip and trip not in {item["trip"] for item in eligible.values()}:
            raise ValueError("未知的旅程")
        where, params = ["1=1"], []
        if article_id:
            where.append("article_id = ?")
            params.append(article_id)
        if trip:
            ids = [key for key, meta in eligible.items() if meta["trip"] == trip]
            where.append("article_id IN (" + ",".join("?" for _ in ids) + ")")
            params.extend(ids)
        if unread == "1":
            where.append("is_read = 0")
        if q.strip():
            where.append("(instr(lower(content), lower(?)) > 0 OR instr(lower(coalesce(nickname,'')), lower(?)) > 0)")
            params.extend([q.strip(), q.strip()])
        base = " AND ".join(where)
        with self._get_connection() as conn:
            conn.execute("BEGIN")
            counts = {key: 0 for key in ("pending", "in_progress", "done")}
            for row in conn.execute(f"SELECT status, count(*) n FROM messages WHERE {base} GROUP BY status", params):
                counts[row["status"]] = row["n"]
            counts["all"] = sum(counts.values())
            counts["unread"] = conn.execute(f"SELECT count(*) FROM messages WHERE {base} AND is_read=0", params).fetchone()[0]
            total = counts[status]
            pages = max(1, (total + page_size - 1) // page_size)
            page = min(page, pages)
            if status != "all":
                where.append("status = ?")
                params.append(status)
            rows = conn.execute(
                "SELECT * FROM messages WHERE " + " AND ".join(where) + " ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?",
                [*params, page_size, (page - 1) * page_size],
            ).fetchall()
            messages = [self._author_message(row, eligible) for row in rows]
        return {"success": True, "messages": messages, "counts": counts, "total": total,
                "page": page, "page_size": page_size, "pages": pages}

    def _author_message(self, row, eligible):
        meta = eligible.get(row["article_id"], {})
        output = meta.get("output", "")
        url = "/" + output[5:] if output.startswith("docs/") and ".." not in output else None
        result = {key: row[key] for key in ("id", "article_id", "nickname", "content", "created_at", "status", "author_note", "version")}
        result.update(is_read=bool(row["is_read"]), article_title=meta.get("title", row["article_id"]),
                      article_url=url, trip=meta.get("trip", row["article_id"].split(":")[0]))
        return result

    def update_author_message(self, token, message_id, version, **changes):
        if not self.verify_author_token(token):
            raise PermissionError("未授權的管理請求，請先登入")
        if not isinstance(message_id, str) or not message_id or type(version) is not int or version < 0:
            raise ValueError("無效的留言識別碼或版本")
        if not changes or set(changes) - {"status", "author_note", "is_read"}:
            raise ValueError("無效的更新欄位")
        if "status" in changes and changes["status"] not in ("pending", "in_progress", "done"):
            raise ValueError("無效的處理狀態")
        if "is_read" in changes and type(changes["is_read"]) is not bool:
            raise ValueError("無效的已讀值")
        if "author_note" in changes and (not isinstance(changes["author_note"], str) or len(changes["author_note"]) > 5000):
            raise ValueError("作者筆記不得超過 5000 字")
        with self._get_connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute("SELECT * FROM messages WHERE id=?", (message_id,)).fetchone()
            if row is None:
                raise ValueError("找不到指定之留言")
            if row["version"] != version:
                raise FeedbackConflictError("留言已在其他頁面更新，請重新載入後合併筆記")
            assignments = ", ".join(f"{key}=?" for key in changes)
            conn.execute(f"UPDATE messages SET {assignments}, version=version+1 WHERE id=? AND version=?",
                         [*changes.values(), message_id, version])
            row = conn.execute("SELECT * FROM messages WHERE id=?", (message_id,)).fetchone()
            conn.commit()
        return {"success": True, "message": self._author_message(row, self.get_eligible_articles())}

    def mark_message_read(self, token, message_id):
        """作者標記留言為已讀"""
        if not self.verify_author_token(token):
            raise PermissionError("未授權的管理請求，請先登入")
        if not message_id or not isinstance(message_id, str):
            raise ValueError("無效的留言識別碼")

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE messages SET is_read = 1, version=version+1 WHERE id = ?", (message_id,))
            if cursor.rowcount == 0:
                raise ValueError("找不到指定之留言")
            conn.commit()

        return {"success": True, "message_id": message_id, "is_read": True}
