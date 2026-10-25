"""Local-only author bridge. Credentials never form part of a browser DTO."""
import json
import os
from pathlib import Path
import urllib.error
import urllib.parse
import urllib.request


class CloudFeedbackUnavailable(Exception):
    def __init__(self):
        super().__init__("雲端回饋服務暫時無法使用")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class CloudFeedbackService:
    def __init__(self, config_path=None):
        self.config_path = Path(config_path or os.environ.get("CH_FEEDBACK_CLOUD_CONFIG")
                                or Path(__file__).resolve().parents[1] / ".local_data/cloud_feedback.json")

    def _config(self):
        try:
            data = json.loads(self.config_path.read_text(encoding="utf-8"))
            url, secret = data["url"], data["admin_secret"]
            parsed = urllib.parse.urlsplit(url)
            if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
                    or parsed.query or parsed.fragment or not isinstance(secret, str) or not secret.strip()
                    or "\r" in secret or "\n" in secret):
                raise ValueError()
            return url.rstrip("/"), secret
        except Exception:
            raise CloudFeedbackUnavailable() from None

    def sources(self):
        try:
            self._config()
        except CloudFeedbackUnavailable:
            return {"success": True, "sources": ["local"], "default": "local"}
        return {"success": True, "sources": ["local", "cloud"], "default": "cloud"}

    def request(self, action, *, query="", payload=None):
        if action not in ("summary", "messages", "update-message", "mark-read"):
            raise CloudFeedbackUnavailable()
        try:
            url, secret = self._config()
            url += "/internal/author/" + action
            if query:
                url += "?" + query
            body = None if payload is None else json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=body, headers={
                "Authorization": "Bearer " + secret, "Content-Type": "application/json",
                "Accept": "application/json", "User-Agent": "CHTravelAuthorBridge/1.0",
            }, method="GET" if body is None else "POST")
            opener = urllib.request.build_opener(_NoRedirect())
            try:
                response = opener.open(req, timeout=10)
            except urllib.error.HTTPError as exc:
                response = exc
            with response:
                status = response.code
                raw = response.read(2_000_001)
            if status not in (200, 400, 409) or len(raw) > 2_000_000:
                raise ValueError()
            data = json.loads(raw)
            if (not isinstance(data, dict) or type(data.get("success")) is not bool
                    or secret in json.dumps(data, ensure_ascii=False)):
                raise ValueError()
            return data, status
        except Exception:
            raise CloudFeedbackUnavailable() from None
