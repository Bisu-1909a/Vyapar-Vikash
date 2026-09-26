"""
app.py – Flask application factory and entry point.

Run:
    cd backend
    pip install -r requirements.txt
    python app.py
"""

import os
import sys
from datetime import timedelta

# Ensure project root, database, api, and backend directories are in sys.path
backend_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(backend_dir)
for p in [base_dir, os.path.join(base_dir, "database"), os.path.join(base_dir, "api"), backend_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

from flask import Flask, jsonify, send_from_directory
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

# ── Load environment variables from .env ──────
env_path = os.path.join(backend_dir, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

# ── Local modules (database, api, backend) ────
try:
    from database.models import init_db
except ImportError:
    from models import init_db

try:
    from api.auth import auth_bp, bcrypt
    from api.google_oauth import google_bp, oauth, register_google
    from api.analysis_api import analysis_bp
except ImportError:
    from auth import auth_bp, bcrypt
    from google_oauth import google_bp, oauth, register_google
    from analysis_api import analysis_bp


def create_app() -> Flask:
    app = Flask(__name__)

    # ── Core config ───────────────────────────
    app.config["SECRET_KEY"]         = os.getenv("SECRET_KEY", "dev-secret-change-me!")
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=7)

    # ── Extensions ────────────────────────────
    bcrypt.init_app(app)
    oauth.init_app(app)
    register_google(app)

    # Allow requests from the frontend dev server and file:// origin
    frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
    CORS(app,
         origins=[
             frontend_origin,
             "http://localhost:3000",
             "http://127.0.0.1:3000",
             "http://localhost:8080",
             "http://127.0.0.1:8080",
             "http://localhost:5000",
             "http://127.0.0.1:5000",
             "null"  # covers file:// origin
         ],
         supports_credentials=True)

    # ── Blueprints ────────────────────────────
    app.register_blueprint(auth_bp)
    app.register_blueprint(google_bp)
    app.register_blueprint(analysis_bp)

    # ── Frontend Static File Serving ──────────
    FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))

    @app.route("/")
    @app.route("/index.html")
    def serve_index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.route("/pages/<path:filename>")
    def serve_pages(filename):
        # Handle analyze.html alias
        if filename == "analyze.html":
            filename = "analyse.html"
        pages_dir = os.path.join(FRONTEND_DIR, "pages")
        return send_from_directory(pages_dir, filename)

    @app.route("/css/<path:filename>")
    def serve_css(filename):
        css_dir = os.path.join(FRONTEND_DIR, "css")
        return send_from_directory(css_dir, filename)

    @app.route("/js/<path:filename>")
    def serve_js(filename):
        js_dir = os.path.join(FRONTEND_DIR, "js")
        return send_from_directory(js_dir, filename)

    @app.route("/assets/<path:filename>")
    def serve_assets(filename):
        assets_dir = os.path.join(FRONTEND_DIR, "assets")
        return send_from_directory(assets_dir, filename)

    # ── Health check ──────────────────────────
    @app.route("/api/health")
    def health():
        return jsonify({
            "status": "ok",
            "message": "Vyapaar Vikash API is running",
            "database": "certified_sqlite"
        }), 200

    # ── Global error handlers ─────────────────
    @app.errorhandler(404)
    def not_found(err):
        from flask import request
        if request.path.startswith("/api/"):
            return jsonify({"error": "API Route not found"}), 404
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.errorhandler(405)
    def method_not_allowed(_):
        return jsonify({"error": "Method not allowed"}), 405

    @app.errorhandler(500)
    def internal_error(err):
        return jsonify({"error": "Internal server error", "detail": str(err)}), 500

    return app


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    # Initialise database (creates tables if missing)
    init_db()

    app = create_app()
    print("\n" + "="*55)
    print("  Vyapaar Vikash Backend")
    print("  API: http://localhost:5000")
    print("  Health: http://localhost:5000/api/health")
    print("="*55 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
