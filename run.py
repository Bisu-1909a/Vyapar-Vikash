"""
run.py – Convenient root entry point for Vyapaar Vikash.
Separated Architecture:
  • database/  - SQLite database and models
  • backend/   - Core application logic and calculation engines
  • api/       - REST API routes and authentication
  • frontend/  - UI pages, styling, and JavaScript client

Usage:
  python run.py
  (or: python backend/app.py)
"""

import os
import sys

# Ensure root, backend, database, and api folders are in sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
for path in [
    root_dir,
    os.path.join(root_dir, "backend"),
    os.path.join(root_dir, "database"),
    os.path.join(root_dir, "api")
]:
    if path not in sys.path:
        sys.path.insert(0, path)

from database.models import init_db
from backend.app import create_app

if __name__ == "__main__":
    init_db()
    app = create_app()
    print("\n" + "="*55)
    print("  Vyapaar Vikash (Separated Architecture)")
    print("  • Database: database/db.sqlite3")
    print("  • Backend:  backend/")
    print("  • API:      api/")
    print("  • Frontend: frontend/")
    print("  URL:        http://localhost:5000")
    print("  Health:     http://localhost:5000/api/health")
    print("="*55 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=True)
