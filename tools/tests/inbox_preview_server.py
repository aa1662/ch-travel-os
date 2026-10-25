"""Isolated, synthetic inbox for browser review. Never uses the author's database."""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.feedback_service import FeedbackService


def main():
    root = ROOT / '.local_data' / 'inbox-preview'
    root.mkdir(parents=True, exist_ok=True)
    trips = root / 'trips'
    for trip, label in [('synthetic-germany', '測試德國旅程'), ('synthetic-japan', '測試日本旅程')]:
        folder = trips / trip
        folder.mkdir(parents=True, exist_ok=True)
        (folder / 'blog-migration.json').write_text(json.dumps({'dest': '2026-germany', 'entries': [
            {'id': 'story', 'title': label, 'feedback': True,
             'output': 'docs/2026-germany/blog/hanau-frankfurt.html'}]}, ensure_ascii=False), encoding='utf-8')
    db, secret = root/'preview.db', root/'secret.json'
    # This fixed credential belongs only to synthetic, loopback preview data.
    secret.write_text(json.dumps({'passcode': 'synthetic-inbox-preview'}), encoding='utf-8')
    service = FeedbackService(db, secret, trips)
    with service._get_connection() as conn:
        # Deterministic likes exist only in this disposable synthetic database.
        for trip, count in [('synthetic-germany', 7), ('synthetic-japan', 3)]:
            for i in range(count):
                conn.execute('INSERT OR IGNORE INTO likes (article_id,client_id,active,created_at,updated_at) VALUES (?,?,?,?,?)',
                             (f'{trip}:story', f'preview-like-{i}', 1, '2026-10-24T12:00:00+00:00', '2026-10-24T12:00:00+00:00'))
        for i in range(65):
            trip = 'synthetic-germany' if i < 40 else 'synthetic-japan'
            conn.execute('INSERT OR IGNORE INTO messages (id,article_id,client_id,client_submission_id,nickname,content,is_read,created_at) VALUES (?,?,?,?,?,?,?,?)',
                         (f'preview-{i:03}', f'{trip}:story', f'preview-client-{i}', f'preview-sub-{i}',
                          f'測試讀者 {i:02}', f'合成測試問題 {i:02}：這條散步路線適合安排半天嗎？\n這是隔離驗收資料。', 0, '2026-10-24T12:00:00+00:00'))
    os.environ.update(CH_FEEDBACK_DB=str(db), CH_FEEDBACK_SECRET=str(secret), CH_FEEDBACK_TRIPS=str(trips))
    from tools import server
    server.PORT = 8091
    server.main()


if __name__ == '__main__':
    main()
