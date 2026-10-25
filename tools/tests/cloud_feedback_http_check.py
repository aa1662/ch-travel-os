"""Real Worker/D1 HTTP regression against an isolated LOCAL Wrangler database.

Never accepts a production URL. Supply an ignored JSON file with url and
admin_secret; no secrets, submitted contents or reader IDs are printed.
"""
import argparse
import json
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path


def run(config):
    base = config['url'].rstrip('/')
    assert urllib.parse.urlsplit(base).hostname in ('127.0.0.1', 'localhost')
    article = '2026-germany:day-09'
    client, submission = uuid.uuid4().hex, uuid.uuid4().hex

    def call(path, data=None, author=False, expected=200, origin='https://chxtravel.com'):
        headers = {'Origin': origin, 'Content-Type': 'application/json'}
        if author:
            headers['Authorization'] = 'Bearer ' + config['admin_secret']
        req = urllib.request.Request(base+path, data=None if data is None else json.dumps(data).encode(), headers=headers)
        try:
            response = urllib.request.urlopen(req)
        except urllib.error.HTTPError as exc:
            response = exc
        assert response.status == expected, (path, response.status, expected)
        assert response.headers.get('Cache-Control') == 'no-store'
        return json.load(response)

    status_path = '/api/feedback/status?' + urllib.parse.urlencode(dict(article_id=article,client_id=client))
    assert call(status_path)['liked'] is False
    call('/internal/author/summary', expected=401)
    call('/api/feedback/like', dict(article_id=article,client_id=client,action='like'), expected=403, origin='https://evil.example')
    like = dict(article_id=article,client_id=client,action='like')
    assert call('/api/feedback/like',like)['liked']
    assert call('/api/feedback/like',like)['liked']
    assert call(status_path)['liked']
    initial = next(a for a in call('/internal/author/summary',author=True)['articles'] if a['article_id']==article)
    assert initial['likes_count'] >= 1
    message = dict(article_id=article,client_id=client,client_submission_id=submission,nickname='系統測試',content='隔離資料庫的整合驗證留言')
    first = call('/api/feedback/message',message)
    again = call('/api/feedback/message',message)
    assert again['message_id'] == first['message_id'] and again['duplicate_prevented']
    result = call('/internal/author/messages?status=all&page_size=1',author=True)
    row = next(m for m in result['messages'] if m['id']==first['message_id'])
    update = dict(message_id=row['id'],version=row['version'],author_note='隔離筆記',status='in_progress',is_read=True)
    saved = call('/internal/author/update-message',update,author=True)['message']
    assert saved['version']==row['version']+1 and saved['status']=='in_progress' and saved['is_read']
    call('/internal/author/update-message',update,author=True,expected=409)
    assert call('/internal/author/messages?status=in_progress&unread=1',author=True)['total']==0
    filtered = call('/internal/author/messages?status=in_progress&q='+urllib.parse.quote('隔離資料庫'),author=True)
    assert any(m['id']==row['id'] and m['author_note']=='隔離筆記' for m in filtered['messages'])
    call('/api/feedback/message',{**message,'client_submission_id':uuid.uuid4().hex,'content':'x'*1001},expected=400)
    call('/api/feedback/like',{**like,'article_id':'2026-germany:unknown'},expected=400)
    assert not call('/api/feedback/like',{**like,'action':'unlike'})['liked']
    assert not call(status_path)['liked']
    # Rate limiting remains effective when callers rotate anonymous IDs.
    for i in range(28):
        call('/api/feedback/message',{**message,'client_id':uuid.uuid4().hex,'client_submission_id':uuid.uuid4().hex})
    call('/api/feedback/message',{**message,'client_id':uuid.uuid4().hex,'client_submission_id':uuid.uuid4().hex},expected=429)
    print('Worker real D1 HTTP: auth, origin, whitelist, idempotence, counts, notes, conflict, filters, rate limits OK')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config',required=True)
    run(json.loads(Path(parser.parse_args().config).read_text(encoding='utf-8')))
