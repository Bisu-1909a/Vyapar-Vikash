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

---

## 🤖 AI Layer: LLM + Tool-Calling over Flask APIs + PostgreSQL

The AI Advisor is an LLM agent that can only answer through **typed tools**. Each tool wraps one of the app's existing deterministic engines or one of its ORM queries, so every figure it gives traces back to the analysis engine or the database.

```
Browser ──► POST /api/ai/advisor ──► LLM (OpenAI-compatible, tool calling)
                                       │  calls tools by name with JSON args
                                       ▼
                         ai/tools.py  (Pydantic-validated, user-scoped, audited)
                                       │
                 analysis_engine / opportunity_engine / database.models (SQLAlchemy ORM)
                                       │
                               PostgreSQL  (SQLite fallback for local dev)
```

### Tools
`GET /api/tools` lists every tool with its JSON input schema. `POST /api/tools/<name>` runs a tool directly with a JSON body.

| Tool | What it does |
|---|---|
| `run_feasibility_analysis` | Feasibility score, revenue/profit, break-even, ROI, EMI, market, competition, matched schemes |
| `get_analysis` / `list_my_analyses` | Saved certified analyses (only the signed-in user's own records, plus public samples) |
| `discover_opportunities` | Ranks business categories for a location |
| `simulate_scenario` | What-if: rent %, demand %, new competitors |
| `generate_business_plan` | Plan outline with financial summary and roadmap |
| `list_government_schemes` / `get_sector_benchmark` | Scheme and benchmark tables |
| `get_location_intelligence` / `search_locations` | Micro-area economics and location search |
| `list_my_business_plans` / `list_my_saved_opportunities` | The signed-in user's saved items |
| `list_business_types` | Valid keys for the other tools |

### Accuracy & safety
- **No raw SQL.** All data access goes through SQLAlchemy models (`database/orm.py`), and schema changes go through Alembic (`migrations/`).
- **Validated inputs.** Pydantic models use enums for business types and area types, numeric bounds, and reject unknown fields.
- **User isolation.** The user id comes from the Flask session, never from the LLM. `list_my_*` tools require sign-in, and another user's analysis returns `forbidden`.
- **Read-only.** Tools can't create, change or delete business data.
- **Grounding check.** Each figure in an LLM reply is checked against the tool outputs and the user's own inputs. Figures that can't be traced are returned in `grounding.unverified_numbers`, and the reply gets a caution line.
- **Audit log.** Each tool call is written to the `ai_tool_calls` table (tool, args, ok/error, duration, user, source). Users can view their own calls at `GET /api/ai/tool_calls`.
- **Rate limits.** Per user/IP limits (`AI_ADVISOR_RATE_LIMIT_PER_MIN`, `AI_TOOLS_RATE_LIMIT_PER_MIN`), plus a cap on tool-call rounds per question.
- **Graceful fallback.** With no `LLM_API_KEY`, or if the provider errors, the advisor falls back to the previous rule-based replies.

### Setup
```bash
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env      # set SECRET_KEY, DATABASE_URL, LLM_* (see comments in the file)

# Local PostgreSQL (optional; without DATABASE_URL the app uses database/db.sqlite3)
docker run -d --name vyapar-pg -e POSTGRES_USER=vyapar -e POSTGRES_PASSWORD=change-me -e POSTGRES_DB=vyapar -p 5432:5432 postgres:16

python run.py          # runs Alembic migrations + seeds reference data on start
```
Any OpenAI-compatible provider with tool calling works: OpenAI, Groq, Gemini (OpenAI endpoint), OpenRouter, or Ollama. Set `LLM_BASE_URL`, `LLM_API_KEY` and `LLM_MODEL`.

Schema change workflow: edit `database/orm.py`, run `alembic revision --autogenerate -m "..."`, then `alembic upgrade head`.

### Tests
```bash
pip install -r requirements-dev.txt
pytest                                                                     # SQLite
TEST_DATABASE_URL=postgresql://vyapar:change-me@localhost:5432/vyapar_test pytest   # PostgreSQL
```
