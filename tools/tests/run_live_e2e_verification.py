#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import urllib.request
import urllib.error
from pathlib import Path

BASE_URL = os.environ.get("CH_FEEDBACK_TEST_URL")
if not BASE_URL or os.environ.get("CH_FEEDBACK_TEST_DISPOSABLE") != "1":
    raise SystemExit("Set CH_FEEDBACK_TEST_URL and CH_FEEDBACK_TEST_DISPOSABLE=1 for an isolated test server only")
ART_ID = "2026-germany:day-09"
CLIENT_ID = "e2e-live-user-001"
SUB_ID = "e2e-live-sub-001"
PASSCODE = os.environ["CH_FEEDBACK_TEST_PASSCODE"]

out_lines = []

def log(msg):
    print(msg)
    out_lines.append(msg)

def req(path, method="GET", data=None, token=None):
    url = BASE_URL + path
    headers = {"Content-Type": "application/json"} if data else {}
    if token:
        headers["Authorization"] = "Bearer " + token
    body = json.dumps(data).encode("utf-8") if data else None
    r = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read().decode("utf-8"))

def main():
    log("=== CH Travel OS 讀者回饋與作者管理 E2E 真實流程驗證 ===")

    # Step 1: 檢查文章初始狀態
    code, res = req(f"/api/feedback/status?article_id={ART_ID}&client_id={CLIENT_ID}")
    assert code == 200 and res["liked"] is False
    log(f"1. 讀者初始狀態: code={code}, liked={res['liked']}")

    # Step 2: 點讚操作 (免登入、無裝置指紋)
    code, res = req("/api/feedback/like", "POST", {"article_id": ART_ID, "client_id": CLIENT_ID, "action": "like"})
    assert code == 200 and res["liked"] is True
    log(f"2. 點讚成功: code={code}, liked={res['liked']}")

    # Step 3: 重複點讚 (冪等防重複計數)
    code, res = req("/api/feedback/like", "POST", {"article_id": ART_ID, "client_id": CLIENT_ID, "action": "like"})
    assert code == 200 and res["liked"] is True
    log(f"3. 重試點讚（冪等確認）: code={code}, liked={res['liked']}")

    # Step 4: 留言獨立於點讚 (暱稱選填、不收 Email、純文字安全儲存)
    msg_payload = {
        "article_id": ART_ID,
        "client_id": CLIENT_ID,
        "client_submission_id": SUB_ID,
        "nickname": "台北讀者",
        "content": "哈瑙的格林童話起點太迷人了！想請問菲利普斯魯厄宮冬天有開嗎？"
    }
    code, res = req("/api/feedback/message", "POST", msg_payload)
    assert code == 200 and res["success"] is True
    msg_id = res["message_id"]
    log(f"4. 送出私密留言成功: code={code}, message_id={msg_id}")

    # Step 5: 重試留言 (client_submission_id 防重複收件)
    code, res_dup = req("/api/feedback/message", "POST", msg_payload)
    assert code == 200 and res_dup["message_id"] == msg_id and res_dup.get("duplicate_prevented") is True
    log(f"5. 重試留言防重複收件確認: code={code}, duplicate_prevented=True")

    # Step 6: 拒絕未知文章與純空白內容
    code, res_bad1 = req("/api/feedback/message", "POST", {**msg_payload, "article_id": "unknown:article", "client_submission_id": "sub-bad-1"})
    assert code == 400
    log(f"6a. 拒絕未知文章: code={code}, error={res_bad1.get('error')}")

    code, res_bad2 = req("/api/feedback/message", "POST", {**msg_payload, "content": "   ", "client_submission_id": "sub-bad-2"})
    assert code == 400
    log(f"6b. 拒絕純空白留言: code={code}, error={res_bad2.get('error')}")

    # Step 7: 未授權管理請求拒絕 (401)
    code, res_auth_fail = req("/api/author/summary")
    assert code == 401
    log(f"7. 未授權管理請求阻斷: code={code}, error={res_auth_fail.get('error')}")

    # Step 8: 作者密碼驗證
    code, res_login_err = req("/api/author/login", "POST", {"passcode": "wrong"})
    assert code == 401
    log(f"8a. 錯誤密碼阻斷: code={code}")

    code, res_login = req("/api/author/login", "POST", {"passcode": PASSCODE})
    assert code == 200 and res_login["success"] is True
    token = res_login["token"]
    log(f"8b. 正確密碼登入成功: code={code}, token={token[:8]}...")

    # Step 9: 作者查看總覽與統計
    code, res_summary = req("/api/author/summary", token=token)
    art = next(a for a in res_summary["articles"] if a["article_id"] == ART_ID)
    assert art["likes_count"] == 1 and art["total_messages"] == 1 and art["unread_messages"] == 1
    log(f"9. 作者查看統計: 讚數={art['likes_count']}, 總留言={art['total_messages']}, 未讀={art['unread_messages']}")

    # Step 10: 作者查看留言清單
    code, res_msgs = req(f"/api/author/messages?article_id={ART_ID}", token=token)
    msg_item = res_msgs["messages"][0]
    assert msg_item["id"] == msg_id and msg_item["nickname"] == "台北讀者" and msg_item["is_read"] is False
    log(f"10. 作者讀取留言: 暱稱={msg_item['nickname']}, 內容={msg_item['content'][:20]}..., 已讀={msg_item['is_read']}")

    # Step 11: 作者標記為已讀
    code, res_read = req("/api/author/mark-read", "POST", {"message_id": msg_id}, token=token)
    assert code == 200 and res_read["is_read"] is True
    log(f"11. 標記已讀成功: code={code}")

    # Step 12: 驗證未讀數更新為 0
    code, res_summary2 = req("/api/author/summary", token=token)
    art2 = next(a for a in res_summary2["articles"] if a["article_id"] == ART_ID)
    assert art2["unread_messages"] == 0
    log(f"12. 統計即時更新: 未讀留言數={art2['unread_messages']}")

    # Step 13: 讀者取消點讚 (unlike)
    code, res_unlike = req("/api/feedback/like", "POST", {"article_id": ART_ID, "client_id": CLIENT_ID, "action": "unlike"})
    assert code == 200 and res_unlike["liked"] is False
    log(f"13. 讀者取消點讚: code={code}, liked={res_unlike['liked']}")

    # Step 14: 驗證讚數更新為 0
    code, res_summary3 = req("/api/author/summary", token=token)
    art3 = next(a for a in res_summary3["articles"] if a["article_id"] == ART_ID)
    assert art3["likes_count"] == 0
    log(f"14. 統計即時更新: 讚數={art3['likes_count']}")

    # Step 15: 驗證未開放文章無回饋區塊
    with urllib.request.urlopen(f"{BASE_URL}/2026-germany/blog/heidelberg-castle.html") as r:
        other_html = r.read().decode("utf-8")
        assert "reader-feedback-section" not in other_html
        log("15. 驗證未開放文章 (Heidelberg): 無 reader-feedback-section，正常無干擾")

    log("=== ✅ E2E 所有 15 項真實場景 100% 通過！ ===")

    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)
    (out_dir / "reader_feedback_e2e.log").write_text("\n".join(out_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
