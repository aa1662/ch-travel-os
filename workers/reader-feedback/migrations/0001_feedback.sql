CREATE TABLE likes (
 article_id TEXT NOT NULL, client_id TEXT NOT NULL, active INTEGER NOT NULL CHECK(active IN (0,1)),
 updated_at TEXT NOT NULL, PRIMARY KEY(article_id,client_id)
);
CREATE TABLE messages (
 id TEXT PRIMARY KEY, article_id TEXT NOT NULL, client_submission_id TEXT NOT NULL,
 nickname TEXT, content TEXT NOT NULL, is_read INTEGER NOT NULL DEFAULT 0 CHECK(is_read IN(0,1)),
 created_at TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN('pending','in_progress','done')),
 author_note TEXT NOT NULL DEFAULT '', version INTEGER NOT NULL DEFAULT 0,
 UNIQUE(article_id,client_submission_id)
);
CREATE INDEX messages_article_date ON messages(article_id,created_at DESC,id DESC);
CREATE INDEX messages_status_date ON messages(status,created_at DESC,id DESC);
CREATE TABLE rate_limits (key TEXT PRIMARY KEY, count INTEGER NOT NULL, expires INTEGER NOT NULL);
CREATE INDEX rate_limits_expiry ON rate_limits(expires);
