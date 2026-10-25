"""Isolated HTTP integration checks; no Worker or daily server is contacted."""
import io
import json
import os
import shutil
import subprocess
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch, Mock
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server
from cloud_feedback_service import CloudFeedbackService, CloudFeedbackUnavailable, _NoRedirect
from feedback_service import FeedbackService


class CloudBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.service = FeedbackService(db_path=cls.root / 'test.db',
                                     secret_path=cls.root / 'auth.json', trips_dir=cls.root / 'trips')
        cls.token = cls.service.author_login(cls.service.get_author_passcode())['token']
        cls.service_patch = patch.object(server, 'feedback_service', cls.service)
        cls.service_patch.start()
        cls.httpd = ThreadingHTTPServer(('127.0.0.1', 0), server.TravelOSMultiTripHandler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = 'http://127.0.0.1:' + str(cls.httpd.server_port)
        cls.client = urllib.request.build_opener()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join()
        cls.service_patch.stop()
        cls.temp.cleanup()

    def setUp(self):
        self.config = self.root / 'cloud.json'
        self.secret = 'synthetic-cloud-admin-secret'
        self.config.write_text(json.dumps({'url': 'https://feedback.example', 'admin_secret': self.secret}))
        self.env = patch.dict(os.environ, {'CH_FEEDBACK_CLOUD_CONFIG': str(self.config)})
        self.env.start()
        self.addCleanup(self.env.stop)
        self.opener = Mock()
        self.remote = patch('cloud_feedback_service.urllib.request.build_opener', return_value=self.opener)
        self.remote.start()
        self.addCleanup(self.remote.stop)
        self.reply({'success': True, 'articles': []})

    def reply(self, data, status=200):
        response = io.BytesIO(json.dumps(data).encode())
        response.code = status
        self.opener.open.return_value = response

    def request(self, action, *, source='cloud', token=True, payload=None, method=None, headers=None):
        request_headers = dict(headers or {})
        if source is not None:
            request_headers['X-Feedback-Source'] = source
        if token:
            request_headers['Authorization'] = 'Bearer ' + self.token
        if payload is not None:
            request_headers['Content-Type'] = 'application/json'
        req = urllib.request.Request(self.url + '/api/author/' + action,
            headers=request_headers, data=None if payload is None else json.dumps(payload).encode(), method=method)
        try:
            response = self.client.open(req)
        except urllib.error.HTTPError as exc:
            response = exc
        with response:
            return response.code, json.loads(response.read())

    def test_authentication_precedes_every_cloud_operation(self):
        for action, payload in [('sources', None), ('summary', None), ('messages', None),
                                ('update-message', {'message_id': 'm', 'version': 0}),
                                ('mark-read', {'message_id': 'm'})]:
            with self.subTest(action=action):
                self.assertEqual(self.request(action, token=False, payload=payload)[0], 401)
                self.assertEqual(self.request(action, token=False, payload=payload,
                                              headers={'Authorization': 'Bearer invalid-session'})[0], 401)
        self.opener.open.assert_not_called()

    def test_cloud_selection_does_not_change_local_login(self):
        code, data = self.request('login', token=False,
                                  payload={'passcode': self.service.get_author_passcode()})
        self.assertEqual(code, 200)
        self.assertTrue(self.service.verify_author_token(data['token']))
        self.assertNotIn(self.secret, json.dumps(data))
        self.opener.open.assert_not_called()

    def test_sources_only_exposes_names_and_default_and_env_override(self):
        code, data = self.request('sources')
        self.assertEqual((code, data), (200, {'success': True, 'sources': ['local', 'cloud'], 'default': 'cloud'}))
        self.assertNotIn(self.secret, json.dumps(data))
        self.assertNotIn('feedback.example', json.dumps(data))
        self.config.unlink()
        self.assertEqual(self.request('sources')[1], {'success': True, 'sources': ['local'], 'default': 'local'})
        self.opener.open.assert_not_called()

    def test_get_forwarding_preserves_filters_and_uses_only_cloud_credential(self):
        query = 'messages?article_id=alpha%3Astory&trip=alpha&q=%E6%97%85%E8%A1%8C&status=done&unread=1&page=2&page_size=5'
        dto = {'success': True, 'messages': [], 'counts': {'all': 0}, 'page': 2, 'pages': 2}
        self.reply(dto)
        self.assertEqual(self.request(query), (200, dto))
        req = self.opener.open.call_args.args[0]
        self.assertEqual(req.full_url, 'https://feedback.example/internal/author/' + query)
        self.assertEqual(req.get_header('Authorization'), 'Bearer ' + self.secret)
        self.assertEqual(req.get_header('User-agent'), 'CHTravelAuthorBridge/1.0')
        self.assertNotIn(self.token, str(req.headers))
        self.assertIsNone(req.data)
        self.assertEqual(self.opener.open.call_args.kwargs['timeout'], 10)

    def test_canonical_https_config_routes_all_author_actions(self):
        for base in ('https://chxtravel.com', 'https://chxtravel.com/'):
            self.config.write_text(json.dumps({'url': base, 'admin_secret': self.secret}))
            self.assertEqual(self.request('sources')[1]['default'], 'cloud')
            for action, payload in [('summary', None), ('messages?status=all', None),
                                    ('update-message', {'message_id': 'm', 'version': 0, 'status': 'done'}),
                                    ('mark-read', {'message_id': 'm'})]:
                with self.subTest(base=base, action=action):
                    self.reply({'success': True})
                    self.assertEqual(self.request(action, payload=payload)[0], 200)
                    req = self.opener.open.call_args.args[0]
                    self.assertEqual(req.full_url, 'https://chxtravel.com/internal/author/' + action)
                    self.assertEqual(req.get_header('User-agent'), 'CHTravelAuthorBridge/1.0')
                    self.assertEqual(req.get_header('Authorization'), 'Bearer ' + self.secret)

    def test_post_forwarding_and_http_conflict_contract(self):
        payload = {'message_id': 'm', 'version': 7, 'author_note': '私人筆記', 'status': 'done', 'is_read': True}
        dto = {'success': False, 'error': '版本衝突', 'message': {'id': 'm', 'version': 8}}
        self.opener.open.side_effect = urllib.error.HTTPError('https://feedback.example', 409, 'Conflict', {},
                                                             io.BytesIO(json.dumps(dto).encode()))
        self.assertEqual(self.request('update-message', payload=payload), (409, dto))
        req = self.opener.open.call_args.args[0]
        self.assertEqual(req.method, 'POST')
        self.assertEqual(json.loads(req.data), payload)
        self.assertTrue(req.full_url.endswith('/internal/author/update-message'))
        self.opener.open.side_effect = None
        dto = {'success': True, 'message_id': 'm', 'is_read': True}
        self.reply(dto)
        self.assertEqual(self.request('mark-read', payload={'message_id': 'm'}), (200, dto))
        self.assertTrue(self.opener.open.call_args.args[0].full_url.endswith('/internal/author/mark-read'))

    def test_missing_config_and_unknown_source_fail_without_local_fallback(self):
        self.assertEqual(self.request('summary', source='typo')[0], 503)
        self.config.unlink()
        for action, payload in [('summary', None), ('messages', None),
                                ('update-message', {'message_id': 'm', 'version': 0}),
                                ('mark-read', {'message_id': 'm'})]:
            self.assertEqual(self.request(action, payload=payload)[0], 503)
        self.opener.open.assert_not_called()

    def test_no_header_and_explicit_local_stay_local(self):
        for source in (None, 'local'):
            self.assertEqual(self.request('summary', source=source), (200, {'success': True, 'articles': []}))
        self.opener.open.assert_not_called()

    def test_remote_errors_and_secret_echo_are_generic(self):
        for status in (401, 403, 500, 302):
            self.opener.open.side_effect = urllib.error.HTTPError('https://feedback.example', status, self.secret, {},
                                                                 io.BytesIO(self.secret.encode()))
            code, data = self.request('summary')
            self.assertEqual(code, 503)
            self.assertNotIn(self.secret, json.dumps(data))
        for exc in (TimeoutError(self.secret), urllib.error.URLError(self.secret)):
            self.opener.open.side_effect = exc
            self.assertEqual(self.request('summary'), (503, {'success': False, 'error': '雲端回饋服務暫時無法使用'}))
        self.opener.open.side_effect = None
        for data in ({'success': True, 'error': self.secret}, [], {'articles': []}):
            self.reply(data)
            code, body = self.request('summary')
            self.assertEqual(code, 503)
            self.assertNotIn(self.secret, json.dumps(body))

    def test_remote_validation_error_and_malformed_local_body(self):
        dto = {'success': False, 'error': '無效的頁碼'}
        self.reply(dto, 400)
        self.assertEqual(self.request('messages?page=0'), (400, dto))
        self.opener.open.reset_mock()
        self.assertEqual(self.request('update-message', payload=[])[0], 400)
        self.opener.open.assert_not_called()

    def test_origin_host_and_json_guards_precede_forwarding(self):
        self.assertEqual(self.request('summary', headers={'Host': 'evil.example'})[0], 403)
        self.assertEqual(self.request('mark-read', payload={}, headers={'Origin': 'https://evil.example'})[0], 403)
        self.opener.open.assert_not_called()

    def test_redirect_policy_never_forwards_admin_secret(self):
        self.assertIsNone(_NoRedirect().redirect_request(None, None, 302, '', {}, 'https://other.example'))

    def test_bad_config_never_leaks_or_contacts_remote(self):
        for config in ({'url': 'http://feedback.example', 'admin_secret': self.secret},
                       {'url': 'https://user:password@feedback.example', 'admin_secret': self.secret},
                       {'url': 'https://feedback.example?secret=x', 'admin_secret': self.secret},
                       {'url': 'https://feedback.example', 'admin_secret': ''}):
            self.config.write_text(json.dumps(config))
            with self.assertRaises(CloudFeedbackUnavailable) as exc:
                CloudFeedbackService().request('summary')
            self.assertNotIn(self.secret, str(exc.exception))
        self.opener.open.assert_not_called()


class SourceSelectorTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'), 'Node is required for the admin UI behavior harness')
    def test_source_races_and_unsaved_draft_guard(self):
        script = r"""
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const html=fs.readFileSync('core/author-feedback.html','utf8');
const nodes={};
function node(){return {value:'',textContent:'',hidden:false,disabled:false,dataset:{},children:[],
 classList:{add(){},remove(){},toggle(){}},setAttribute(){},removeAttribute(){},
 append(...n){this.children.push(...n)},add(n){this.children.push(n)},
 replaceChildren(...n){this.children=n},addEventListener(k,f){this['on'+k]=f},
 focus(){},scrollIntoView(){},showModal(){this.open=true},close(){this.open=false}};}
for(const match of html.matchAll(/id="([^"]+)"/g))nodes[match[1]]=node();
nodes.overviewSort.value='likes_count';
const pending=[];let savedToken='synthetic-session';
function response(data,status=200){return {ok:status===200,status,json:async()=>data};}
const counts={pending:1,in_progress:0,done:0,unread:1,all:1};
function summary(label){return {success:true,articles:[{article_id:label+':story',trip:label,title:label,likes_count:1,total_messages:1,unread_messages:1}]};}
function messages(label){return {success:true,messages:[{id:'same-id',article_id:label+':story',article_title:label,trip:label,
 content:label+' content',author_note:label+' note',status:'pending',version:0,is_read:false}],counts,total:1,page:1,pages:1};}
const context={document:{getElementById:id=>nodes[id],createElement:node,
 querySelectorAll:()=>nodes.statusTabs.children},window:{addEventListener(){}},
 sessionStorage:{getItem:()=>savedToken,setItem:(k,v)=>savedToken=v,removeItem:()=>savedToken=''},
 Option:function(text,value){return {text,value}},AbortController,DOMException,URL,URLSearchParams,
 location:{origin:'http://localhost:8080'},navigator:{},
 fetch:(path,options)=>{
 if(path==='/api/author/sources')return Promise.resolve(response({success:true,sources:['local','cloud'],default:'cloud'}));
 return new Promise(resolve=>pending.push({path,options,resolve}));
 }};
vm.runInNewContext(html.match(/<script>([\s\S]*?)<\/script>/)[1],context);
const settle=()=>new Promise(resolve=>setImmediate(resolve));
function change(source){nodes.feedbackSource.value=source;nodes.feedbackSource.onchange({target:nodes.feedbackSource});}
function complete(source,kind,data,status=200){
 const req=pending.find(r=>!r.done && r.options.headers['X-Feedback-Source']===source && r.path.includes('/'+kind));
 assert.ok(req,source+' '+kind);req.done=true;req.resolve(response(data,status));return req;
}
(async()=>{
 await settle();assert.equal(nodes.feedbackSource.value,'cloud');
 assert.equal(pending.length,2);
 change('local');assert.equal(nodes.feedbackSource.value,'local');
 complete('cloud','summary',summary('old-cloud'));
 complete('cloud','messages',{success:false,error:'expired old source'},401);
 await settle();assert.equal(savedToken,'synthetic-session');assert.equal(nodes.dashboardView.hidden,false);
 assert.equal(nodes.overviewRows.children.length,0);assert.equal(nodes.messagesList.children.length,0);
 complete('local','summary',summary('local'));complete('local','messages',messages('local'));
 await settle();assert.equal(nodes.messagesList.children.length,1);
 nodes.messagesList.children[0].onclick();
 assert.equal(nodes.messageBody.textContent,'local content');
 nodes.authorNote.value='unsaved draft';nodes.authorNote.oninput({target:nodes.authorNote});
 const before=pending.length;change('cloud');
 assert.equal(nodes.feedbackSource.value,'local');assert.equal(nodes.unsavedDialog.open,true);
 assert.equal(pending.length,before);assert.equal(nodes.authorNote.value,'unsaved draft');
 nodes.modalStay.onclick();assert.equal(nodes.feedbackSource.value,'local');
 change('cloud');nodes.modalDiscard.onclick();
 assert.equal(nodes.feedbackSource.value,'cloud');assert.equal(nodes.authorNote.value,'');
 assert.equal(nodes.messageBody.textContent,'');assert.equal(nodes.copyText.value,'');
 assert.equal(nodes.messagesList.children.length,0);assert.equal(nodes.overviewRows.children.length,0);
 assert.equal(nodes.detailContent.hidden,true);
 complete('cloud','summary',summary('new-cloud'));complete('cloud','messages',messages('new-cloud'));
 await settle();nodes.messagesList.children[0].onclick();
 assert.equal(nodes.messageBody.textContent,'new-cloud content');
 assert.equal(nodes.authorNote.value,'new-cloud note');
 for(const req of pending)assert.equal(req.options.headers.Authorization,'Bearer synthetic-session');
 console.log('source default, stale responses, draft stay/discard, and data clearing passed');
})().catch(e=>{console.error(e);process.exitCode=1});
"""
        result = subprocess.run(['node', '-e', script], cwd=Path(__file__).resolve().parents[2],
                                capture_output=True, text=True, encoding='utf-8', timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
