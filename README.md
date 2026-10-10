# Vyapaar Vikash (व्यापार विकास)
**AI-Powered Hyperlocal Business Feasibility & Opportunity Intelligence Platform for India**

---

## 📁 Modular Project Structure

The project has been separated into clean, decoupled, and dedicated folders:

```
antigravityproject-main/
│
├── 📂 database/                 # Dedicated Database Layer
│   ├── __init__.py              # DB exports (init_db, get_db, CRUD functions)
│   ├── models.py                # Certified SQLite schemas, seeders, queries
│   └── db.sqlite3               # SQLite production database file
│
├── 📂 api/                      # Dedicated REST API Layer
│   ├── __init__.py              # Blueprint exports (auth_bp, analysis_bp, google_bp)
│   ├── analysis_api.py          # Business analysis, schemes, stats, geo API routes
│   ├── auth.py                  # User registration, login, logout, profile routes
│   └── google_oauth.py          # Google OAuth2 integration routes
│
├── 📂 backend/                  # Core Backend Engines & Server Factory
│   ├── app.py                   # Flask application factory & static file server
│   ├── analysis_engine.py       # 6-module certified feasibility calculation engine
│   ├── opportunity_engine.py    # Local opportunity scoring and discovery engine
│   ├── geo_data.py              # 36 States/UTs, 760+ Districts, archetype datasets
│   ├── requirements.txt         # Python dependencies
│   └── .env                     # Environment variables configuration
│
├── 📂 frontend/                 # Frontend User Interface
│   ├── index.html               # Landing page
│   ├── pages/                   # Application pages (analyse, dashboard, login, etc.)
│   ├── css/                     # Styling and design system
│   ├── js/                      # Frontend JavaScript and API client
│   └── assets/                  # Icons and static media assets
│
└── 🚀 run.py                    # Root entrypoint to run the entire application
```

---

## 🚀 How to Run

### Method 1: Root Entrypoint (Recommended)
```bash
python run.py
```

### Method 2: From Backend Directory
```bash
cd backend
python app.py
```

- **Local Application URL:** [http://localhost:5000](http://localhost:5000)
- **Local Feasibility Tool:** [http://localhost:5000/pages/analyse.html](http://localhost:5000/pages/analyse.html)
- **Local API Health Check:** [http://localhost:5000/api/health](http://localhost:5000/api/health)

---

## 🌐 Public Live Shareable URLs (Worldwide Access)

The platform is accessible worldwide over secure HTTPS via Cloudflare Tunnel:

- **🏠 Public Application URL:** [https://many-hamilton-egg-birmingham.trycloudflare.com](https://many-hamilton-egg-birmingham.trycloudflare.com)
- **📍 Feasibility & Opportunity Tool:** [https://many-hamilton-egg-birmingham.trycloudflare.com/pages/analyse.html](https://many-hamilton-egg-birmingham.trycloudflare.com/pages/analyse.html)
- **📊 User Dashboard:** [https://many-hamilton-egg-birmingham.trycloudflare.com/pages/dashboard.html](https://many-hamilton-egg-birmingham.trycloudflare.com/pages/dashboard.html)
- **🩺 Public Health Check:** [https://many-hamilton-egg-birmingham.trycloudflare.com/api/health](https://many-hamilton-egg-birmingham.trycloudflare.com/api/health)

> **To launch a new public tunnel at any time:**
> ```bash
> .\cf.exe tunnel --url http://localhost:5000
> ```
