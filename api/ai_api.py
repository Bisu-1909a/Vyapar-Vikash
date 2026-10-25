"""
ai_api.py – AI tool layer endpoints.

  GET  /api/tools                – catalogue of tools with JSON input schemas
  POST /api/tools/<name>         – run one tool with a JSON body (validated)
  POST /api/ai/advisor           – LLM advisor (falls back to rule-based replies when no LLM is configured)
  GET  /api/ai/tool_calls        – the signed-in user's recent tool-call audit log
"""

import os
import sys
import threading
import time
from collections import defaultdict, deque

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE_DIR = os.path.dirname(_THIS_DIR)
for _p in [_BASE_DIR, os.path.join(_BASE_DIR, "database"), os.path.join(_BASE_DIR, "backend"), _THIS_DIR]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from flask import Blueprint, jsonify, request, session

from ai import agent, tools
from database.models import get_analysis_owner, get_tool_calls

try:
    from api.analysis_api import ai_advisor as rule_based_advisor
except ImportError:
    from analysis_api import ai_advisor as rule_based_advisor

ai_bp = Blueprint("ai", __name__)

_STATUS = {"validation_error": 400, "invalid_request": 400, "auth_required": 401,
           "forbidden": 403, "not_found": 404, "internal_error": 500}

_PROFILE_KEYS = ("business_type", "business_name", "district", "state", "village", "investment",
                 "stage", "area_type", "analysis_id")


class _RateLimiter:
    def __init__(self):
        self._hits = defaultdict(deque)
        self._lock = threading.Lock()
        self._last_sweep = time.monotonic()

    def _sweep(self, now: float, window: float) -> None:
        for k in [k for k, q in self._hits.items() if not q or now - q[-1] > window]:
            del self._hits[k]
        self._last_sweep = now

    def allow(self, key: str, limit: int, window: float = 60.0) -> bool:
        now = time.monotonic()
        with self._lock:
            if now - self._last_sweep > window:
                self._sweep(now, window)
            q = self._hits[key]
            while q and now - q[0] > window:
                q.popleft()
            if len(q) >= limit:
                return False
            q.append(now)
            return True


_limiter = _RateLimiter()


def _client_ip() -> str:
    # Behind a reverse proxy / tunnel (e.g. cloudflared) every request comes from 127.0.0.1;
    # set TRUST_PROXY=1 there so anonymous users get separate rate-limit buckets.
    if os.getenv("TRUST_PROXY") == "1":
        fwd = request.headers.get("CF-Connecting-IP") or (request.headers.get("X-Forwarded-For") or "").split(",")[0]
        if fwd.strip():
            return fwd.strip()
    return request.remote_addr or "unknown"


def _rate_limited(bucket: str, env_var: str, default: int):
    who = f"u{session['user_id']}" if session.get("user_id") else f"ip{_client_ip()}"
    if not _limiter.allow(f"{bucket}:{who}", int(os.getenv(env_var) or default)):
        return jsonify({"status": "error", "error": "Too many requests. Please wait a minute and try again."}), 429
    return None


def _ctx() -> tools.ToolContext:
    return tools.ToolContext(user_id=session.get("user_id"), source="api")


@ai_bp.route("/api/tools", methods=["GET"])
def list_tools():
    catalogue = tools.list_tools()
    return jsonify({"status": "success", "count": len(catalogue), "tools": catalogue}), 200


@ai_bp.route("/api/tools/<string:name>", methods=["POST"])
def run_tool(name: str):
    limited = _rate_limited("tools", "AI_TOOLS_RATE_LIMIT_PER_MIN", 60)
    if limited:
        return limited
    body = request.get_json(silent=True)
    result = tools.execute(name, body if body is not None else {}, _ctx())
    status = 200 if result["ok"] else _STATUS.get(result.get("error_type"), 400)
    return jsonify({"status": "success" if result["ok"] else "error", **result}), status


@ai_bp.route("/api/ai/advisor", methods=["POST"])
def advisor():
    limited = _rate_limited("advisor", "AI_ADVISOR_RATE_LIMIT_PER_MIN", 20)
    if limited:
        return limited

    body = request.get_json(silent=True) or {}
    message = (body.get("message") or "").strip()
    if not message:
        return jsonify({"status": "error", "error": "Message is required."}), 400

    analysis_id = body.get("analysis_id")
    if analysis_id not in (None, ""):
        try:
            exists, owner = get_analysis_owner(int(analysis_id))
        except (TypeError, ValueError):
            return jsonify({"status": "error", "error": "analysis_id must be an integer."}), 400
        if exists and owner is not None and owner != session.get("user_id"):
            return jsonify({"status": "error", "error": "This analysis belongs to another user."}), 403

    if not agent.is_configured():
        resp, status = rule_based_advisor()
        data = resp.get_json()
        data["engine"] = "rules"
        return jsonify(data), status

    profile = {k: body.get(k) for k in _PROFILE_KEYS}
    try:
        result = agent.run_advisor(message, profile, _ctx(), history=body.get("history"))
    except Exception as e:
        print(f"[AI Advisor] LLM call failed, using rule-based fallback: {e!r}")
        resp, status = rule_based_advisor()
        data = resp.get_json()
        data["engine"] = "rules_fallback"
        return jsonify(data), status

    return jsonify({"status": "success", "engine": "llm", **result}), 200


@ai_bp.route("/api/ai/tool_calls", methods=["GET"])
def my_tool_calls():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    limit = max(1, min(int(request.args.get("limit", 50)), 200))
    return jsonify({"status": "success", "tool_calls": get_tool_calls(user_id=user_id, limit=limit)}), 200
