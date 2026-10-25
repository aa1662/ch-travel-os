import json
import sys
import tempfile
import threading
import unittest
import urllib.request
import urllib.error
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLS_DIR))
import server
from feedback_service import FeedbackService


class ServerFeedbackRoutesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp()
        cls.temp_path = Path(cls.temp_dir)
        cls.db_path = cls.temp_path / "routes_test.db"
        cls.secret_path = cls.temp_path / "routes_secret.json"

        # Point server.feedback_service to test instance
        cls.test_service = FeedbackService(
            db_path=cls.db_path,
            secret_path=cls.secret_path,
        )
        cls.orig_service = server.feedback_service
        server.feedback_service = cls.test_service

        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), partial(server.TravelOSMultiTripHandler, directory=str(server.DOCS_DIR)))
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        server.feedback_service = cls.orig_service
        import shutil
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    def _url(self, path):
        return f"http://127.0.0.1:{self.port}{path}"

    def setUp(self):
        # Each HTTP case owns an empty, disposable test database.
        with self.test_service._get_connection() as conn:
            for table in ('messages', 'likes', 'rate_limits', 'author_sessions'):
                conn.execute(f'DELETE FROM {table}')

    def _json_request(self, method, path, data=None, token=None):
        url = self._url(path)
        body = json.dumps(data).encode("utf-8") if data is not None else None
        headers = {}
        if data is not None:
            headers["Content-Type"] = "application/json"
        if token:
            headers["Authorization"] = f"Bearer {token}"
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as err:
            err_body = err.read().decode("utf-8")
            try:
                return err.code, json.loads(err_body)
            except Exception:
                return err.code, {"error": err_body}

    def test_author_portal_served(self):
        url = self._url("/core/author-feedback.html")
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            content = resp.read().decode("utf-8")
            self.assertIn("讀者回饋", content)

    def test_inbox_update_conflict_and_private_routes(self):
        service = self.test_service
        message = service.submit_message('2026-germany:day-09', 'inbox-http', 'inbox-http-sub', None, 'Synthetic inbox question')
        code, login = self._json_request('POST', '/api/author/login', {'passcode': service.get_author_passcode()})
        self.assertEqual(code, 200)
        token = login['token']
        payload = {'message_id': message['message_id'], 'version': 0, 'status': 'in_progress', 'author_note': 'Synthetic note'}
        code, _ = self._json_request('POST', '/api/author/update-message', payload)
        self.assertEqual(code, 401)
        code, saved = self._json_request('POST', '/api/author/update-message', payload, token)
        self.assertEqual(code, 200)
        self.assertEqual(saved['message']['version'], 1)
        code, _ = self._json_request('POST', '/api/author/update-message', payload, token)
        self.assertEqual(code, 409)
        code, result = self._json_request('GET', '/api/author/messages?status=in_progress&q=Synthetic&page_size=1', token=token)
        self.assertEqual(code, 200)
        self.assertEqual(result['total'], 1)
        self.assertEqual(result['messages'][0]['author_note'], 'Synthetic note')
        code, _ = self._json_request('GET', '/api/author/messages?page_size=10000', token=token)
        self.assertEqual(code, 400)
        req = urllib.request.Request(self._url('/api/author/messages'), headers={'Host': 'untrusted.test', 'Authorization': 'Bearer '+token})
        with self.assertRaises(urllib.error.HTTPError) as response:
            urllib.request.urlopen(req)
        self.assertEqual(response.exception.code, 403)

    def test_summary_counts_active_likes_across_articles_and_read_updates(self):
        germany = '2026-germany:day-09'
        tokyo = '2023-tokyo:tokyo-arrival-meiji-jingu'
        self.assertEqual(self._json_request('GET', '/api/author/summary')[0], 401)
        for article, client in [(germany, 'one'), (germany, 'two'), (tokyo, 'three')]:
            payload = {'article_id': article, 'client_id': client, 'action': 'like'}
            self.assertEqual(self._json_request('POST', '/api/feedback/like', payload)[0], 200)
            self.assertEqual(self._json_request('POST', '/api/feedback/like', payload)[0], 200)
        self._json_request('POST', '/api/feedback/like',
                           {'article_id': germany, 'client_id': 'two', 'action': 'unlike'})
        code, message = self._json_request('POST', '/api/feedback/message',
            {'article_id': germany, 'client_id': 'one', 'client_submission_id': 'overview-test', 'content': 'Synthetic overview question'})
        self.assertEqual(code, 200)
        _, login = self._json_request('POST', '/api/author/login', {'passcode': self.test_service.get_author_passcode()})
        token = login['token']
        code, result = self._json_request('GET', '/api/author/summary', token=token)
        self.assertEqual(code, 200)
        articles = {a['article_id']: a for a in result['articles']}
        self.assertEqual(articles[germany]['likes_count'], 1)
        self.assertEqual(articles[tokyo]['likes_count'], 1)
        self.assertEqual(articles[germany]['total_messages'], 1)
        self.assertEqual(articles[germany]['unread_messages'], 1)
        self.assertEqual(articles[tokyo]['total_messages'], 0)
        self.assertEqual(articles['2026-germany:day-01']['likes_count'], 0)
        code, _ = self._json_request('POST', '/api/author/update-message',
            {'message_id': message['message_id'], 'version': 0, 'is_read': True}, token)
        self.assertEqual(code, 200)
        _, result = self._json_request('GET', '/api/author/summary', token=token)
        articles = {a['article_id']: a for a in result['articles']}
        self.assertEqual(articles[germany]['unread_messages'], 0)
        self.assertEqual(articles[germany]['total_messages'], 1)
        self.assertEqual(articles[germany]['likes_count'], 1)

    def test_reader_feedback_flow_and_author_management(self):
        art_id = "2026-germany:day-09"
        client_id = "test-http-client-1"

        # 1. Reader checks initial like status
        code, data = self._json_request("GET", f"/api/feedback/status?article_id={art_id}&client_id={client_id}")
        self.assertEqual(code, 200)
        self.assertFalse(data["liked"])

        # 2. Unknown article status rejected
        code, data = self._json_request("GET", f"/api/feedback/status?article_id=unknown:article&client_id={client_id}")
        self.assertEqual(code, 400)
        self.assertFalse(data["success"])

        # 3. Reader likes the article
        code, data = self._json_request("POST", "/api/feedback/like", {
            "article_id": art_id,
            "client_id": client_id,
            "action": "like"
        })
        self.assertEqual(code, 200)
        self.assertTrue(data["liked"])

        # 4. Reader re-checks status -> now liked
        code, data = self._json_request("GET", f"/api/feedback/status?article_id={art_id}&client_id={client_id}")
        self.assertEqual(code, 200)
        self.assertTrue(data["liked"])

        # 5. Reader submits a private comment without liking again
        sub_id = "http-submission-12345"
        code, data = self._json_request("POST", "/api/feedback/message", {
            "article_id": art_id,
            "client_id": client_id,
            "client_submission_id": sub_id,
            "nickname": "德國旅人",
            "content": "哈瑙的格林紀念碑很有童話感！"
        })
        self.assertEqual(code, 200)
        self.assertTrue(data["success"])
        msg_id = data["message_id"]

        # 6. Retry with same submission ID -> deduplicated
        code, data_dup = self._json_request("POST", "/api/feedback/message", {
            "article_id": art_id,
            "client_id": client_id,
            "client_submission_id": sub_id,
            "nickname": "德國旅人",
            "content": "哈瑙的格林紀念碑很有童話感！"
        })
        self.assertEqual(code, 200)
        self.assertEqual(data_dup["message_id"], msg_id)
        self.assertTrue(data_dup.get("duplicate_prevented"))

        # 7. Unauthenticated access to author summary returns 401
        code, data = self._json_request("GET", "/api/author/summary")
        self.assertEqual(code, 401)

        # 8. Author login with wrong passcode returns 401
        code, data = self._json_request("POST", "/api/author/login", {"passcode": "wrong-secret"})
        self.assertEqual(code, 401)

        # 9. Author login with correct passcode returns token
        code, data = self._json_request("POST", "/api/author/login", {"passcode": self.test_service.get_author_passcode()})
        self.assertEqual(code, 200)
        self.assertTrue(data["success"])
        token = data["token"]

        # 10. Author checks summary with token
        code, data = self._json_request("GET", "/api/author/summary", token=token)
        self.assertEqual(code, 200)
        articles = data["articles"]
        target = next(a for a in articles if a["article_id"] == art_id)
        self.assertEqual(target["likes_count"], 1)
        self.assertEqual(target["total_messages"], 1)
        self.assertEqual(target["unread_messages"], 1)

        # 11. Author checks messages list
        code, data = self._json_request("GET", f"/api/author/messages?article_id={art_id}", token=token)
        self.assertEqual(code, 200)
        msgs = data["messages"]
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0]["id"], msg_id)
        self.assertEqual(msgs[0]["nickname"], "德國旅人")
        self.assertFalse(msgs[0]["is_read"])

        # 12. Author marks message as read
        code, data = self._json_request("POST", "/api/author/mark-read", {"message_id": msg_id}, token=token)
        self.assertEqual(code, 200)
        self.assertTrue(data["success"])

        # 13. Verify unread count is now 0
        code, data = self._json_request("GET", "/api/author/summary", token=token)
        target2 = next(a for a in data["articles"] if a["article_id"] == art_id)
        self.assertEqual(target2["unread_messages"], 0)

        # 14. Reader unlikes
        code, data = self._json_request("POST", "/api/feedback/like", {
            "article_id": art_id,
            "client_id": client_id,
            "action": "unlike"
        })
        self.assertEqual(code, 200)
        self.assertFalse(data["liked"])

        # 15. Verify likes count is now 0
        code, data = self._json_request("GET", "/api/author/summary", token=token)
        target3 = next(a for a in data["articles"] if a["article_id"] == art_id)
        self.assertEqual(target3["likes_count"], 0)


if __name__ == "__main__":
    unittest.main()
