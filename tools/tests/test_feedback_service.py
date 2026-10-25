import os
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.feedback_service import FeedbackService


class FeedbackServiceTests(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.db_path = Path(self.test_dir) / "test_feedback.db"
        self.secret_path = Path(self.test_dir) / "test_secret.json"
        self.trips_dir = Path(__file__).resolve().parent.parent.parent / "trips"
        self.service = FeedbackService(
            db_path=self.db_path,
            secret_path=self.secret_path,
            trips_dir=self.trips_dir,
        )

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_article_eligibility_whitelist(self):
        eligible = self.service.get_eligible_articles()
        self.assertIn("2026-germany:day-09", eligible)
        self.assertTrue(self.service.is_eligible("2026-germany:day-09"))

        # Unknown / unapproved articles must be rejected
        self.assertFalse(self.service.is_eligible("2026-germany:not-published"))
        self.assertFalse(self.service.is_eligible("2023-tokyo:day-01"))
        self.assertFalse(self.service.is_eligible("random:id"))

        with self.assertRaises(ValueError):
            self.service.toggle_like("2026-germany:not-published", "client-1", "like")

        with self.assertRaises(ValueError):
            self.service.submit_message("2026-germany:not-published", "client-1", "sub-1", "Nick", "Hello")

    def test_like_and_unlike_idempotency(self):
        art_id = "2026-germany:day-09"
        client_a = "client-a-uuid"
        client_b = "client-b-uuid"

        # Initial status
        st_a = self.service.get_reader_status(art_id, client_a)
        self.assertFalse(st_a["liked"])

        # Client A likes
        res = self.service.toggle_like(art_id, client_a, "like")
        self.assertTrue(res["liked"])
        self.assertTrue(self.service.get_reader_status(art_id, client_a)["liked"])

        # Client A likes again (idempotent retry)
        res_dup = self.service.toggle_like(art_id, client_a, "like")
        self.assertTrue(res_dup["liked"])

        # Client B likes
        self.service.toggle_like(art_id, client_b, "like")

        # Verify summary counts via author
        login = self.service.author_login(self.service.get_author_passcode())
        token = login["token"]
        summary = self.service.get_author_summary(token)
        art_summary = next(a for a in summary["articles"] if a["article_id"] == art_id)
        self.assertEqual(art_summary["likes_count"], 2)

        # Client A unlikes
        res_unlike = self.service.toggle_like(art_id, client_a, "unlike")
        self.assertFalse(res_unlike["liked"])
        self.assertFalse(self.service.get_reader_status(art_id, client_a)["liked"])

        # Client A unlikes again (idempotent)
        res_unlike_dup = self.service.toggle_like(art_id, client_a, "unlike")
        self.assertFalse(res_unlike_dup["liked"])

        # Verify count decreased by 1
        summary2 = self.service.get_author_summary(token)
        art_summary2 = next(a for a in summary2["articles"] if a["article_id"] == art_id)
        self.assertEqual(art_summary2["likes_count"], 1)

    def test_comment_independent_of_like_and_validation(self):
        art_id = "2026-germany:day-09"
        client = "client-commenter"

        # Submit comment without liking
        res = self.service.submit_message(
            art_id, client, "sub-1", "小明", "這篇文章寫得好棒，喜歡哈瑙與法蘭克福的對比！"
        )
        self.assertTrue(res["success"])
        self.assertIn("msg_", res["message_id"])

        # Reader status remains unliked
        st = self.service.get_reader_status(art_id, client)
        self.assertFalse(st["liked"])

        # Test validation: empty/whitespace content
        with self.assertRaises(ValueError):
            self.service.submit_message(art_id, client, "sub-2", "小明", "   ")

        # Test validation: content exceeding 1000 chars
        with self.assertRaises(ValueError):
            self.service.submit_message(art_id, client, "sub-3", "小明", "A" * 1001)

        # Test validation: nickname exceeding 40 chars
        with self.assertRaises(ValueError):
            self.service.submit_message(art_id, client, "sub-4", "N" * 41, "合法內容")

        # Nickname optional (None / empty string)
        res_anon = self.service.submit_message(art_id, client, "sub-5", "", "匿名讀者留言")
        self.assertTrue(res_anon["success"])

    def test_comment_deduplication_on_retry(self):
        art_id = "2026-germany:day-09"
        client = "client-dedup"
        sub_id = "same-submission-uuid"

        res1 = self.service.submit_message(art_id, client, sub_id, "阿華", "留言文字")
        self.assertTrue(res1["success"])
        msg_id1 = res1["message_id"]

        # Retry with identical submission id
        res2 = self.service.submit_message(art_id, client, sub_id, "阿華", "留言文字")
        self.assertTrue(res2["success"])
        self.assertEqual(res2["message_id"], msg_id1)
        self.assertTrue(res2.get("duplicate_prevented"))

        # Verify only 1 record exists in messages table
        login = self.service.author_login(self.service.get_author_passcode())
        msgs = self.service.get_author_messages(login["token"], art_id)["messages"]
        self.assertEqual(len(msgs), 1)

    def test_author_auth_and_mark_read(self):
        art_id = "2026-germany:day-09"

        # Unauthorized access
        with self.assertRaises(PermissionError):
            self.service.get_author_summary("invalid-token")

        with self.assertRaises(PermissionError):
            self.service.get_author_messages("invalid-token")

        with self.assertRaises(PermissionError):
            self.service.mark_message_read("invalid-token", "msg_test")

        # Invalid password
        with self.assertRaises(PermissionError):
            self.service.author_login("wrong-password")

        # Valid login
        login = self.service.author_login(self.service.get_author_passcode())
        token = login["token"]
        self.assertTrue(self.service.verify_author_token(token))

        # Add message
        msg_res = self.service.submit_message(art_id, "cid-auth", "sub-auth-1", "讀者A", "哈囉 CH！")
        msg_id = msg_res["message_id"]

        # Author checks messages
        msgs = self.service.get_author_messages(token, art_id)["messages"]
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0]["id"], msg_id)
        self.assertFalse(msgs[0]["is_read"])

        # Check summary unread count
        summary = self.service.get_author_summary(token)["articles"]
        art_sm = next(a for a in summary if a["article_id"] == art_id)
        self.assertEqual(art_sm["unread_messages"], 1)

        # Mark read
        mark_res = self.service.mark_message_read(token, msg_id)
        self.assertTrue(mark_res["is_read"])

        # Check summary unread count becomes 0
        summary2 = self.service.get_author_summary(token)["articles"]
        art_sm2 = next(a for a in summary2 if a["article_id"] == art_id)
        self.assertEqual(art_sm2["unread_messages"], 0)

    def test_data_persistence_across_service_restarts(self):
        art_id = "2026-germany:day-09"
        client = "persist-client"

        self.service.toggle_like(art_id, client, "like")
        msg = self.service.submit_message(art_id, client, "sub-persist", "旅人", "持久化測試留言")
        login = self.service.author_login(self.service.get_author_passcode())
        token = login["token"]
        self.service.mark_message_read(token, msg["message_id"])

        # Simulate service restart: instantiate a NEW service with same db and secret path
        restarted_service = FeedbackService(
            db_path=self.db_path,
            secret_path=self.secret_path,
            trips_dir=self.trips_dir,
        )

        # Check like persisted
        self.assertTrue(restarted_service.get_reader_status(art_id, client)["liked"])

        # Check token and message persisted
        self.assertTrue(restarted_service.verify_author_token(token))
        msgs = restarted_service.get_author_messages(token, art_id)["messages"]
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0]["content"], "持久化測試留言")
        self.assertTrue(msgs[0]["is_read"])

    def test_xss_safety_text_storage(self):
        art_id = "2026-germany:day-09"
        xss_content = "<script>alert('xss')</script><img src=x onerror=alert(1)>"
        res = self.service.submit_message(art_id, "cid-xss", "sub-xss", "<script>foo</script>", xss_content)

        login = self.service.author_login(self.service.get_author_passcode())
        msgs = self.service.get_author_messages(login["token"], art_id)["messages"]
        # Stored strictly as plain string without modification, ready for safe DOM textContent rendering
        self.assertEqual(msgs[0]["content"], xss_content)
        self.assertEqual(msgs[0]["nickname"], "<script>foo</script>")


if __name__ == "__main__":
    unittest.main()
