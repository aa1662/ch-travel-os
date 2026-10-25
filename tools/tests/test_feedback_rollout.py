"""Config contract, 31 article output checks, and disposable real HTTP rollout."""
import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.request
import urllib.error
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
from feedback_eligibility import feedback_eligible
from feedback_service import FeedbackService
from build_trip_html import render_reader_feedback

TRIPS = {'2023-tokyo': 2, '2024-australia': 5, '2025-2026-beijing': 4, '2026-germany': 16, '2026-osaka': 4}

class RolloutTests(unittest.TestCase):
    def test_shared_eligibility(self):
        base = {'id': 'story', 'feedback': True, 'output': 'docs/alpha/blog/story.html'}
        cases = [({}, True), ({'feedback': 'true'}, False), ({'feedback': 1}, False),
                 ({'feedback': False}, False), ({'status': 'draft'}, False),
                 ({'id': ''}, False), ({'id': None}, False)]
        cases += [({'output': value}, False) for value in [None, '', 'docs/alpha/index.html',
                  'docs/beta/blog/story.html', 'https://test/story.html', 'docs/alpha/blog/../story.html',
                  'docs/alpha/blog/story.html?x=1', 'core/author-feedback.html', 'docs/alpha/blog/story.HTML']]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); folder = root/'trips/alpha'; folder.mkdir(parents=True)
            service = FeedbackService(root/'test.db', root/'secret.json', root/'trips')
            for updates, expected in cases:
                with self.subTest(updates=updates):
                    entry = dict(base, **updates)
                    (folder/'blog-migration.json').write_text(json.dumps({'entries': [entry]}), encoding='utf-8')
                    self.assertEqual(feedback_eligible(entry, 'alpha'), expected)
                    self.assertEqual(bool(service.get_eligible_articles()), expected)
                    self.assertEqual(bool(render_reader_feedback(entry, 'alpha')), expected)
            self.assertTrue(feedback_eligible(dict(base, output='docs/beta/blog/story.html'), 'alpha', 'beta'))

    def test_rollout_outputs(self):
        for trip, count in TRIPS.items():
            config = json.loads((ROOT/f'trips/{trip}/blog-migration.json').read_text(encoding='utf-8'))
            entries = [e for e in config['entries'] if e.get('status') != 'draft']
            self.assertEqual(len(entries), count)
            for entry in entries:
                with self.subTest(trip=trip, entry=entry['id']):
                    self.assertTrue(feedback_eligible(entry, trip, config.get('dest')))
                    page = (ROOT/entry['output']).read_text(encoding='utf-8')
                    self.assertEqual(page.count('class="reader-feedback-section"'), 1)
                    self.assertEqual(page.count(f'data-article-id="{trip}:{entry["id"]}"'), 1)
                    for button in ('btnFeedbackLike', 'btnToggleComment', 'btnSubmitFeedback'):
                        self.assertIn(f'id="{button}" disabled', page)
                    self.assertIn('core/js/app.js?v=20261025-feedback-availability', page)
                    self.assertIn('core/css/style.css?v=20261025-related', page)
        self.assertFalse((ROOT/'docs/core/author-feedback.html').exists())
        self.assertEqual((ROOT/'core/js/app.js').read_bytes(), (ROOT/'docs/core/js/app.js').read_bytes())

    def test_real_http_all_articles_and_restart(self):
        # Set isolation BEFORE importing server: its module startup creates a service.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch.dict(os.environ, CH_FEEDBACK_DB=str(root/'http.db'), CH_FEEDBACK_SECRET=str(root/'secret.json'), CH_FEEDBACK_TRIPS=str(ROOT/'trips')):
                import server
                previous = server.feedback_service
                service = FeedbackService(root/'http.db', root/'secret.json', ROOT/'trips')
                server.feedback_service = service
                httpd = ThreadingHTTPServer(('127.0.0.1', 0), partial(server.TravelOSMultiTripHandler, directory=str(ROOT/'docs')))
                thread = threading.Thread(target=httpd.serve_forever, daemon=True); thread.start()
                def request(path, body=None, token=None):
                    headers = {'Content-Type': 'application/json'}
                    if token: headers['Authorization'] = 'Bearer '+token
                    req = urllib.request.Request(f'http://127.0.0.1:{httpd.server_port}'+path,
                        data=json.dumps(body).encode() if body is not None else None, headers=headers)
                    try:
                        with urllib.request.urlopen(req, timeout=10) as response:
                            return response.status, json.loads(response.read())
                    except urllib.error.HTTPError as error:
                        return error.code, json.loads(error.read())
                try:
                    articles = service.get_eligible_articles()
                    self.assertEqual(len(articles), 31)
                    for index, article in enumerate(articles):
                        client = f'rollout-client-{index}'
                        self.assertEqual(request(f'/api/feedback/status?article_id={article}&client_id={client}')[0], 200)
                        payload = {'article_id': article, 'client_id': client, 'action': 'like'}
                        self.assertEqual(request('/api/feedback/like', payload)[0], 200)
                        self.assertEqual(request('/api/feedback/like', payload)[0], 200)
                        message = {'article_id': article, 'client_id': client, 'client_submission_id': f'rollout-sub-{index}', 'content': 'Synthetic rollout question'}
                        first = request('/api/feedback/message', message)
                        second = request('/api/feedback/message', message)
                        self.assertEqual(first[0], 200); self.assertEqual(second[0], 200)
                        self.assertEqual(first[1]['message_id'], second[1]['message_id'])
                    self.assertEqual(request('/api/feedback/status?article_id=unknown:story&client_id=test')[0], 400)
                    self.assertEqual(request('/api/author/messages')[0], 401)
                    _, login = request('/api/author/login', {'passcode': service.get_author_passcode()})
                    token = login['token']
                    self.assertEqual(request('/api/author/messages?page_size=50', token=token)[1]['total'], 31)
                    server.feedback_service = FeedbackService(root/'http.db', root/'secret.json', ROOT/'trips')
                    self.assertEqual(request('/api/author/messages', token=token)[1]['total'], 31)
                    with service._get_connection() as conn:
                        self.assertEqual(conn.execute('SELECT COUNT(*) FROM likes WHERE active=1').fetchone()[0],31)
                        self.assertEqual(conn.execute('PRAGMA user_version').fetchone()[0],1)
                finally:
                    httpd.shutdown();httpd.server_close();thread.join();server.feedback_service=previous

if __name__ == '__main__': unittest.main()
