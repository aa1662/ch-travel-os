import articles from './articles.json';

const origins = new Set(['https://chxtravel.com', 'https://www.chxtravel.com']);
const states = ['pending', 'in_progress', 'done'];
class HttpError extends Error {
  constructor(status, message) { super(message); this.status = status; }
}
function requireValue(ok, message = '無效的請求', status = 400) {
  if (!ok) throw new HttpError(status, message);
}
function text(value, max, required = false) {
  requireValue(typeof value === 'string' && [...value].length <= max);
  requireValue(!required || value.trim().length > 0);
  return value;
}
function identity(value) { return text(value, 64, true); }
function eligible(id) {
  requireValue(typeof id === 'string' && Object.hasOwn(articles, id), '未知或未開放回饋的文章');
  return articles[id];
}
function json(data, status = 200) {
  return Response.json(data, {status, headers: {'Cache-Control': 'no-store',
    'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'no-referrer'}});
}
async function body(request) {
  requireValue((request.headers.get('content-type') || '').split(';')[0] === 'application/json', '請使用 JSON', 415);
  requireValue(Number(request.headers.get('content-length') || 0) <= 40000, '請求過大', 413);
  const reader = request.body?.getReader();
  requireValue(reader, '請求缺少內容');
  const chunks = []; let length = 0;
  while (true) {
    const part = await reader.read(); if (part.done) break;
    length += part.value.length;
    if (length > 40000) { await reader.cancel(); throw new HttpError(413, '請求過大'); }
    chunks.push(part.value);
  }
  const bytes = new Uint8Array(length); let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.length; }
  let data; try { data = JSON.parse(new TextDecoder('utf-8', {fatal: true}).decode(bytes)); }
  catch { throw new HttpError(400, '無效的 JSON'); }
  requireValue(data && typeof data === 'object' && !Array.isArray(data));
  return data;
}
async function authorized(request, secret) {
  if (!secret || secret.length < 32) return false;
  const given = request.headers.get('authorization') || '';
  const digest = value => crypto.subtle.digest('SHA-256', new TextEncoder().encode(value));
  const [a,b] = await Promise.all([digest(given),digest('Bearer ' + secret)]);
  const x = new Uint8Array(a), y = new Uint8Array(b);
  let different = 0; for (let i = 0; i < x.length; i++) different |= x[i] ^ y[i];
  return different === 0;
}
async function rate(env, request, client, action) {
  requireValue(env.RATE_SECRET?.length >= 32, '回饋服務暫時無法使用', 503);
  const minute = Math.floor(Date.now() / 60000);
  // Daily salted hash only: no raw IP or user-agent is stored in D1 or logs.
  const digest = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(
    env.RATE_SECRET + ':' + Math.floor(minute / 1440) + ':' + (request.headers.get('CF-Connecting-IP') || 'local')));
  const ip = [...new Uint8Array(digest)].map(x => x.toString(16).padStart(2,'0')).join('');
  const limits = action === 'message' ? [10,30] : action === 'status' ? [120,600] : [30,120];
  const keys = [`c:${action}:${client}:${minute}`, `i:${action}:${ip}:${minute}`];
  const result = await env.DB.batch(keys.map(key => env.DB.prepare(
    'INSERT INTO rate_limits(key,count,expires) VALUES(?,1,?) ON CONFLICT(key) DO UPDATE SET count=count+1 RETURNING count'
  ).bind(key, minute + 10)));
  requireValue(result.every((r,i) => r.results[0].count <= limits[i]), '操作過於頻繁，請稍後再試', 429);
  await env.DB.prepare('DELETE FROM rate_limits WHERE expires < ?').bind(minute).run();
}
function dto(row) {
  const meta = articles[row.article_id];
  const {id, article_id, nickname, content, created_at, status, author_note, version} = row;
  return {id,article_id,nickname,content,created_at,status,author_note,version,is_read:!!row.is_read,
    article_title:meta?.title || article_id, article_url:meta ? '/' + meta.output.slice(5) : null,
    trip:meta?.trip || article_id.split(':')[0]};
}
async function summary(env) {
  const results = await env.DB.batch([
    env.DB.prepare('SELECT article_id,count(*) n FROM likes WHERE active=1 GROUP BY article_id'),
    env.DB.prepare('SELECT article_id,count(*) n,sum(CASE WHEN is_read=0 THEN 1 ELSE 0 END) unread FROM messages GROUP BY article_id')]);
  const likes = new Map(results[0].results.map(r => [r.article_id,r.n]));
  const msgs = new Map(results[1].results.map(r => [r.article_id,r]));
  return {success:true,articles:Object.values(articles).map(a => ({...a,likes_count:likes.get(a.article_id)||0,
    total_messages:msgs.get(a.article_id)?.n||0,unread_messages:msgs.get(a.article_id)?.unread||0}))};
}
async function messages(env, params) {
  const status = params.get('status') || 'all', unread = params.get('unread') || '0';
  const q = text(params.get('q') || '',200).trim(), article = params.get('article_id'), trip = params.get('trip');
  let page = Number(params.get('page') || 1), size = Number(params.get('page_size') || 20);
  requireValue([...states,'all'].includes(status) && ['0','1'].includes(unread));
  requireValue(Number.isInteger(page) && page > 0 && Number.isInteger(size) && size > 0 && size <= 100);
  if (article) eligible(article);
  if (trip) requireValue(Object.values(articles).some(a => a.trip === trip));
  const ids = Object.keys(articles).filter(id => (!article || id === article) && (!trip || articles[id].trip === trip));
  const where = [`article_id IN (${ids.map(() => '?').join(',')})`], values = [...ids];
  if (unread === '1') where.push('is_read=0');
  if (q) { where.push("(instr(lower(content),lower(?))>0 OR instr(lower(coalesce(nickname,'')),lower(?))>0)"); values.push(q,q); }
  const clause = where.join(' AND ');
  const rows = await env.DB.prepare(`SELECT status,count(*) n,sum(CASE WHEN is_read=0 THEN 1 ELSE 0 END) unread FROM messages WHERE ${clause} GROUP BY status`).bind(...values).all();
  const counts = {pending:0,in_progress:0,done:0,all:0,unread:0};
  for (const row of rows.results) { counts[row.status] = row.n; counts.all += row.n; counts.unread += row.unread; }
  const total = counts[status], pages = Math.max(1,Math.ceil(total/size)); page = Math.min(page,pages);
  if (status !== 'all') { where.push('status=?'); values.push(status); }
  const selected = await env.DB.prepare(`SELECT * FROM messages WHERE ${where.join(' AND ')} ORDER BY created_at DESC,id DESC LIMIT ? OFFSET ?`).bind(...values,size,(page-1)*size).all();
  return {success:true,messages:selected.results.map(dto),counts,total,page,page_size:size,pages};
}
async function update(env, data) {
  const {message_id,version,...changes} = data;
  identity(message_id);
  requireValue(Number.isInteger(version) && version >= 0);
  const keys = Object.keys(changes);
  requireValue(keys.length > 0 && keys.every(k => ['status','is_read','author_note'].includes(k)));
  if ('status' in changes) requireValue(states.includes(changes.status));
  if ('is_read' in changes) requireValue(typeof changes.is_read === 'boolean');
  if ('author_note' in changes) text(changes.author_note,5000);
  const statement = env.DB.prepare(`UPDATE messages SET ${keys.map(k=>k+'=?').join(',')},version=version+1 WHERE id=? AND version=? RETURNING *`)
    .bind(...keys.map(k => typeof changes[k] === 'boolean' ? Number(changes[k]) : changes[k]),message_id,version);
  const result = await statement.first();
  if (!result) {
    const exists = await env.DB.prepare('SELECT id FROM messages WHERE id=?').bind(message_id).first();
    throw new HttpError(exists ? 409 : 400, exists ? '留言已在其他頁面更新，請重新載入後合併筆記' : '找不到指定之留言');
  }
  return {success:true,message:dto(result)};
}
export default {
  async fetch(request, env) {
    try {
      const url = new URL(request.url), path = url.pathname;
      if (path.startsWith('/internal/author/')) {
        requireValue(await authorized(request,env.ADMIN_SECRET), '未授權',401);
        if (request.method === 'GET' && path === '/internal/author/summary') return json(await summary(env));
        if (request.method === 'GET' && path === '/internal/author/messages') return json(await messages(env,url.searchParams));
        if (request.method === 'POST' && path === '/internal/author/update-message') return json(await update(env,await body(request)));
        if (request.method === 'POST' && path === '/internal/author/mark-read') {
          const data = await body(request); identity(data.message_id);
          const row = await env.DB.prepare('UPDATE messages SET is_read=1,version=version+1 WHERE id=? RETURNING id').bind(data.message_id).first();
          requireValue(row,'找不到指定之留言'); return json({success:true,message_id:row.id,is_read:true});
        }
        throw new HttpError(404,'找不到 API');
      }
      requireValue(path.startsWith('/api/feedback/'),'找不到 API',404);
      if (request.method === 'GET' && path === '/api/feedback/status') {
        const article_id = url.searchParams.get('article_id'), client_id = url.searchParams.get('client_id');
        eligible(article_id); identity(client_id); await rate(env,request,client_id,'status');
        const row = await env.DB.prepare('SELECT active FROM likes WHERE article_id=? AND client_id=?').bind(article_id,client_id).first();
        return json({success:true,article_id,liked:!!row?.active});
      }
      requireValue(request.method === 'POST' && ['/api/feedback/like','/api/feedback/message'].includes(path),'找不到 API',404);
      requireValue(origins.has(request.headers.get('Origin')),'非法或跨來源請求',403);
      const data = await body(request), {article_id,client_id} = data;
      eligible(article_id); identity(client_id);
      if (path.endsWith('/like')) {
        requireValue(['like','unlike'].includes(data.action)); await rate(env,request,client_id,'like');
        const active = Number(data.action === 'like');
        await env.DB.prepare('INSERT INTO likes(article_id,client_id,active,updated_at) VALUES(?,?,?,?) ON CONFLICT(article_id,client_id) DO UPDATE SET active=excluded.active,updated_at=excluded.updated_at')
          .bind(article_id,client_id,active,new Date().toISOString()).run();
        return json({success:true,article_id,liked:!!active});
      }
      const submission = identity(data.client_submission_id);
      const content = text(data.content,1000,true).trim();
      const nickname = data.nickname == null ? null : text(data.nickname,40).trim() || null;
      await rate(env,request,client_id,'message');
      const id = 'msg_' + crypto.randomUUID().replaceAll('-',''), created = new Date().toISOString();
      await env.DB.prepare('INSERT INTO messages(id,article_id,client_submission_id,nickname,content,created_at) VALUES(?,?,?,?,?,?) ON CONFLICT(article_id,client_submission_id) DO NOTHING')
        .bind(id,article_id,submission,nickname,content,created).run();
      const row = await env.DB.prepare('SELECT id,created_at FROM messages WHERE article_id=? AND client_submission_id=?').bind(article_id,submission).first();
      return json({success:true,message_id:row.id,created_at:row.created_at,...(row.id !== id ? {duplicate_prevented:true} : {})});
    } catch (error) {
      return json({success:false,error:error instanceof HttpError ? error.message : '回饋服務暫時無法使用，請稍後重試'}, error instanceof HttpError ? error.status : 503);
    }
  }
};
