import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from tools.feedback_service import FeedbackService, FeedbackConflictError, ClosingConnection


class InboxTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        trips = self.root / 'trips'
        for trip in ('alpha', 'beta'):
            folder = trips / trip
            folder.mkdir(parents=True)
            (folder / 'blog-migration.json').write_text(json.dumps({'entries': [
                {'id': 'story', 'title': trip, 'feedback': True,
                 'output': f'docs/{trip}/blog/story.html'}]}), encoding='utf-8')
        self.args = dict(db_path=self.root / 'test.db', secret_path=self.root / 'secret.json', trips_dir=trips)
        self.service = FeedbackService(**self.args)
        self.token = self.service.author_login(self.service.get_author_passcode())['token']
        for i in range(65):
            self.service.submit_message(f'{"alpha" if i < 40 else "beta"}:story', f'client{i}', f'sub{i}',
                                        'Reader', f'Synthetic question {i:02d}')

    def tearDown(self):
        self.temp.cleanup()

    def test_paging_filters_counts_and_empty(self):
        first = self.service.get_author_messages(self.token, status='pending')
        self.assertEqual((first['total'], first['pages'], len(first['messages'])), (65, 4, 20))
        ids = []
        for page in range(1, 5):
            ids.extend(m['id'] for m in self.service.get_author_messages(self.token, page=page)['messages'])
        self.assertEqual(len(set(ids)), 65)
        filtered = self.service.get_author_messages(self.token, trip='beta', q='question', unread='1')
        self.assertEqual(filtered['total'], 25)
        self.assertEqual(self.service.get_author_messages(self.token, article_id='alpha:story')['total'], 40)
        empty = self.service.get_author_messages(self.token, q='absent', page=99)
        self.assertEqual((empty['total'], empty['page'], empty['pages']), (0, 1, 1))
        msg = first['messages'][0]
        self.service.update_author_message(self.token, msg['id'], 0, status='done', is_read=True)
        pending = self.service.get_author_messages(self.token, status='pending')
        self.assertEqual((pending['total'], pending['counts']['done'], pending['counts']['unread']), (64, 1, 64))

    def test_conflict_validation_and_restart(self):
        msg = self.service.get_author_messages(self.token)['messages'][0]
        saved = self.service.update_author_message(self.token, msg['id'], 0, author_note='<script>literal</script>', status='in_progress')['message']
        self.assertEqual(saved['version'], 1)
        self.assertFalse(saved['is_read'])
        with self.assertRaises(FeedbackConflictError):
            self.service.update_author_message(self.token, msg['id'], 0, author_note='stale')
        with self.assertRaises(PermissionError):
            self.service.get_author_messages('invalid')
        with self.assertRaises(PermissionError):
            self.service.update_author_message('invalid', msg['id'], 1, status='done')
        for changes in ({'status': 'bad'}, {'author_note': 'x'*5001}, {'is_read': 'false'}, {'content': 'overwrite'}):
            with self.assertRaises(ValueError):
                self.service.update_author_message(self.token, msg['id'], 1, **changes)
        with self.assertRaises(ValueError):
            self.service.update_author_message(self.token, 'missing', 0, status='done')
        for kwargs in ({'page': 0}, {'page_size': 1000}, {'trip': 'missing'}, {'unread': 'bad'}, {'status': 'bad'}):
            with self.assertRaises(ValueError):
                self.service.get_author_messages(self.token, **kwargs)
        restarted = FeedbackService(**self.args)
        current = restarted.get_author_messages(self.token, status='in_progress')['messages'][0]
        self.assertEqual(current['author_note'], '<script>literal</script>')
        self.assertEqual(current['content'], msg['content'])

    def test_legacy_migration_preserves_values_and_is_repeatable(self):
        old = self.root / 'legacy.db'
        with sqlite3.connect(old, factory=ClosingConnection) as conn:
            conn.execute('CREATE TABLE messages (id TEXT PRIMARY KEY, article_id TEXT, client_id TEXT, client_submission_id TEXT, nickname TEXT, content TEXT, is_read INTEGER, created_at TEXT, UNIQUE(article_id,client_submission_id))')
            conn.execute("INSERT INTO messages VALUES ('old','alpha:story','c','s',NULL,'original',1,'2026-01-01')")
        args = dict(self.args, db_path=old)
        FeedbackService(**args)
        FeedbackService(**args)
        with sqlite3.connect(old, factory=ClosingConnection) as conn:
            self.assertEqual(conn.execute('SELECT content,is_read,status,author_note,version FROM messages').fetchone(), ('original',1,'pending','',0))
            self.assertEqual(conn.execute('PRAGMA user_version').fetchone()[0], 1)
        self.assertEqual(len(list((self.root/'backups').glob('legacy-before-inbox-*.db'))), 1)


if __name__ == '__main__':
    unittest.main()
