"""
google_oauth.py – Google OAuth2 login flow using the Authlib library.

Flow:
  1. Browser hits GET /auth/google
  2. Flask redirects user to Google's consent screen
  3. Google redirects back to GET /auth/google/callback with a code
  4. Flask exchanges the code for an access token, fetches user info
  5. Flask upserts the user in SQLite, sets the session, redirects to dashboard
"""

import os
import sys

# Ensure project root, database, and backend directories are in sys.path
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE_DIR = os.path.dirname(_THIS_DIR)
for _p in [_BASE_DIR, os.path.join(_BASE_DIR, "database"), os.path.join(_BASE_DIR, "backend")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from flask import Blueprint, redirect, session, url_for, jsonify
from authlib.integrations.flask_client import OAuth

try:
    from database.models import upsert_google_user, row_to_dict
except ImportError:
    from models import upsert_google_user, row_to_dict

google_bp = Blueprint("google_oauth", __name__)

# Initialised in app.py via oauth.init_app(app)
oauth = OAuth()

GOOGLE_CLIENT_ID     = os.getenv("GOOGLE_CLIENT_ID",     "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

# Only register Google client if credentials are provided
_google_configured = bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
                          and "your-google-client-id" not in GOOGLE_CLIENT_ID)


def register_google(app):
    """Call this from app.py after oauth.init_app(app)."""
    if _google_configured:
        oauth.register(
            name="google",
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )


# ─────────────────────────────────────────────
#  GET /auth/google  – kick off OAuth dance
# ─────────────────────────────────────────────

@google_bp.route("/auth/google")
def google_login():
    if not _google_configured:
        # Redirect to login page with a friendly notice instead of raw JSON error
        return redirect(_get_redirect_target("pages/login.html?error=google_not_configured"))

    redirect_uri = url_for("google_oauth.google_callback", _external=True)
    return oauth.google.authorize_redirect(redirect_uri)



# ─────────────────────────────────────────────
#  GET /auth/google/callback
# ─────────────────────────────────────────────

def _get_redirect_target(subpath: str) -> str:
    """Helper to resolve frontend target based on FRONTEND_ORIGIN or relative path."""
    origin = os.getenv("FRONTEND_ORIGIN", "").strip()
    if origin and not any(h in origin for h in ["localhost:8080", "127.0.0.1:8080"]):
        return f"{origin.rstrip('/')}/{subpath.lstrip('/')}"
    return f"/{subpath.lstrip('/')}"


@google_bp.route("/auth/google/callback")
def google_callback():
    if not _google_configured:
        return redirect(_get_redirect_target("pages/login.html?error=google_not_configured"))

    try:
        token     = oauth.google.authorize_access_token()
        user_info = token.get("userinfo") or oauth.google.userinfo()
    except Exception as exc:
        print(f"[Google OAuth] Error: {exc}")
        return redirect(_get_redirect_target("pages/login.html?error=google_auth_failed"))

    google_id  = user_info.get("sub")
    email      = user_info.get("email", "")
    name       = user_info.get("name", email.split("@")[0] if email else "User")
    avatar_url = user_info.get("picture")

    if not google_id or not email:
        return redirect(_get_redirect_target("pages/login.html?error=google_missing_info"))

    user = upsert_google_user(
        google_id=google_id,
        email=email,
        name=name,
        avatar_url=avatar_url
    )

    session["user_id"] = user["id"]
    session.permanent  = True

    # Redirect to the frontend dashboard
    return redirect(_get_redirect_target("pages/dashboard.html"))
