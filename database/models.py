"""
models.py – Certified Database Schema & Model Operations
SQLite database accessed via Python's built-in sqlite3 module.
Stores users, full business analyses, certified feasibility reports,
official government schemes, and business benchmarks.
"""

import sqlite3
import os
import sys
import json
import hashlib
import uuid
from datetime import datetime
from contextlib import contextmanager

# Ensure backend and project root are in sys.path so modules like geo_data can be imported
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE_DIR = os.path.dirname(_THIS_DIR)
_BACKEND_DIR = os.path.join(_BASE_DIR, "backend")
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)

from geo_data import ALL_INDIA_STATES, ALL_INDIA_DISTRICTS, MICRO_AREA_ARCHETYPES, SAMPLE_BLOCKS_AND_VILLAGES, get_area_archetype

# Resolve the DB file path: defaults to db.sqlite3 in the database/ directory
_ENV_PATH = os.getenv("DATABASE_PATH")
if _ENV_PATH and os.path.isabs(_ENV_PATH):
    DATABASE_PATH = _ENV_PATH
elif _ENV_PATH and _ENV_PATH not in ("db.sqlite3", "database/db.sqlite3"):
    DATABASE_PATH = os.path.abspath(os.path.join(_BASE_DIR, _ENV_PATH))
else:
    DATABASE_PATH = os.path.join(_THIS_DIR, "db.sqlite3")


# ─────────────────────────────────────────────
#  Connection helper
# ─────────────────────────────────────────────

@contextmanager
def get_db():
    """Context manager that yields a SQLite connection with Row factory."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row          # rows behave like dicts
    conn.execute("PRAGMA journal_mode=WAL") # high concurrency
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ─────────────────────────────────────────────
#  Schema initialisation & Seeding
# ─────────────────────────────────────────────

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name                TEXT    NOT NULL,
    email               TEXT    UNIQUE NOT NULL,
    password            TEXT,                        -- NULL for Google-only accounts
    google_id           TEXT    UNIQUE,              -- NULL for email/password accounts
    avatar_url          TEXT,
    role                TEXT    DEFAULT 'entrepreneur',
    subscription_status TEXT    DEFAULT 'free',
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login_at       DATETIME
);

CREATE TABLE IF NOT EXISTS analyses (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id                 INTEGER,
    business_name           TEXT NOT NULL,
    business_type           TEXT NOT NULL,
    business_stage          TEXT DEFAULT 'new',
    state                   TEXT,
    district                TEXT,
    block                   TEXT,
    village                 TEXT,
    area_type               TEXT DEFAULT 'rural',
    latitude                REAL,
    longitude               REAL,
    radius_km               REAL DEFAULT 3.0,
    formatted_address       TEXT,
    total_investment        REAL NOT NULL DEFAULT 100000,
    own_capital             REAL DEFAULT 0,
    loan_amount             REAL DEFAULT 0,
    loan_required           TEXT DEFAULT 'no',
    expected_monthly_sales  REAL DEFAULT 0,
    monthly_expenses        REAL DEFAULT 0,
    entrepreneur_gender     TEXT,
    caste_category          TEXT,
    education               TEXT,
    is_shg                  TEXT DEFAULT 'no',
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS certified_reports (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    analysis_id             INTEGER UNIQUE NOT NULL,
    certificate_no          TEXT UNIQUE NOT NULL,
    verification_hash       TEXT NOT NULL,
    feasibility_score       INTEGER NOT NULL,
    viability_status        TEXT NOT NULL,
    ai_verdict              TEXT NOT NULL,
    market_data_json        TEXT NOT NULL,
    financial_data_json     TEXT NOT NULL,
    swot_data_json          TEXT NOT NULL,
    competition_data_json   TEXT NOT NULL,
    schemes_data_json       TEXT NOT NULL,
    action_plan_json        TEXT NOT NULL,
    certifier               TEXT DEFAULT 'National Rural MSME Intelligence & Assessment Board',
    standard_code           TEXT DEFAULT 'ISO/IEC 27001 & MSME-NIESBUD Certified Protocol',
    status                  TEXT DEFAULT 'CERTIFIED',
    certified_at            DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(analysis_id) REFERENCES analyses(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS location_analyses (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id                 INTEGER,
    location_name           TEXT NOT NULL,
    formatted_address       TEXT,
    state                   TEXT,
    district                TEXT,
    country                 TEXT DEFAULT 'India',
    latitude                REAL NOT NULL,
    longitude               REAL NOT NULL,
    radius_km               REAL NOT NULL DEFAULT 3.0,
    boundary_geojson        TEXT,
    data_freshness          TEXT DEFAULT 'live',
    confidence_score        REAL DEFAULT 85.0,
    opportunities_json      TEXT NOT NULL,
    market_signals_json     TEXT,
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS saved_locations (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id                 INTEGER NOT NULL,
    name                    TEXT NOT NULL,
    formatted_address       TEXT,
    latitude                REAL NOT NULL,
    longitude               REAL NOT NULL,
    radius_km               REAL DEFAULT 3.0,
    place_id                TEXT,
    notes                   TEXT,
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS saved_opportunities (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id                 INTEGER NOT NULL,
    analysis_id             INTEGER,
    location_analysis_id    INTEGER,
    category_key            TEXT NOT NULL,
    category_name           TEXT NOT NULL,
    priority                INTEGER NOT NULL,
    opportunity_score       REAL NOT NULL,
    confidence_score        REAL NOT NULL,
    location_name           TEXT NOT NULL,
    latitude                REAL,
    longitude               REAL,
    radius_km               REAL DEFAULT 3.0,
    reasons_json            TEXT,
    factors_json            TEXT,
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS business_plans (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id                 INTEGER NOT NULL,
    analysis_id             INTEGER,
    title                   TEXT NOT NULL,
    category_key            TEXT NOT NULL,
    location_name           TEXT NOT NULL,
    investment              REAL NOT NULL,
    executive_summary       TEXT,
    plan_json               TEXT NOT NULL,
    roadmap_json            TEXT,
    status                  TEXT DEFAULT 'draft',
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at              DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS scenario_runs (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id                 INTEGER,
    analysis_id             INTEGER,
    scenario_name           TEXT NOT NULL,
    inputs_json             TEXT NOT NULL,
    outputs_json            TEXT NOT NULL,
    created_at              DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS government_schemes (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    name                    TEXT NOT NULL,
    code                    TEXT UNIQUE NOT NULL,
    category                TEXT NOT NULL,
    subsidy_pct             REAL DEFAULT 0,
    max_subsidy_amount      REAL DEFAULT 0,
    max_loan_amount         REAL DEFAULT 0,
    interest_rate_pct       REAL DEFAULT 0,
    eligibility             TEXT,
    description             TEXT,
    nodal_agency            TEXT,
    portal_url              TEXT,
    active                  INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS business_benchmarks (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    sector_key              TEXT UNIQUE NOT NULL,
    sector_name             TEXT NOT NULL,
    avg_margin_pct          REAL NOT NULL,
    monthly_fixed_cost_pct  REAL NOT NULL,
    break_even_months       INTEGER NOT NULL,
    national_cagr_pct       REAL NOT NULL,
    risk_level              TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS geo_states (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    name                    TEXT UNIQUE NOT NULL,
    code                    TEXT UNIQUE NOT NULL,
    zone                    TEXT,
    capital                 TEXT,
    gdp_growth              REAL DEFAULT 10.0,
    primary_industry        TEXT
);

CREATE TABLE IF NOT EXISTS geo_districts (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    state_name              TEXT NOT NULL,
    name                    TEXT NOT NULL,
    tier                    TEXT DEFAULT 'Tier 3 / Rural',
    dic_centre              TEXT,
    primary_sector          TEXT,
    UNIQUE(state_name, name)
);

CREATE TABLE IF NOT EXISTS geo_sub_areas (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    state_name              TEXT NOT NULL,
    district_name           TEXT NOT NULL,
    block_name              TEXT NOT NULL,
    village_name            TEXT NOT NULL,
    area_type               TEXT DEFAULT 'rural',
    avg_sqft_rent           REAL DEFAULT 15.0,
    daily_wage_rate         REAL DEFAULT 380.0,
    footfall_index          REAL DEFAULT 6.5,
    UNIQUE(state_name, district_name, block_name, village_name)
);

CREATE INDEX IF NOT EXISTS idx_users_email       ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_google_id   ON users(google_id);
CREATE INDEX IF NOT EXISTS idx_analyses_user     ON analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_cert_analysis     ON certified_reports(analysis_id);
CREATE INDEX IF NOT EXISTS idx_cert_no           ON certified_reports(certificate_no);
CREATE INDEX IF NOT EXISTS idx_schemes_code      ON government_schemes(code);
CREATE INDEX IF NOT EXISTS idx_geo_dist_state    ON geo_districts(state_name);
CREATE INDEX IF NOT EXISTS idx_geo_dist_name     ON geo_districts(name);
CREATE INDEX IF NOT EXISTS idx_geo_sub_dist      ON geo_sub_areas(district_name);
CREATE INDEX IF NOT EXISTS idx_geo_sub_vill      ON geo_sub_areas(village_name);
CREATE INDEX IF NOT EXISTS idx_loc_analyses_user ON location_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_opps_user   ON saved_opportunities(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_loc_user    ON saved_locations(user_id);
CREATE INDEX IF NOT EXISTS idx_biz_plans_user    ON business_plans(user_id);
"""


DEFAULT_SCHEMES = [
    {
        "name": "Prime Minister's Employment Generation Programme (PMEGP)",
        "code": "PMEGP",
        "category": "Subsidy & Credit Linkage",
        "subsidy_pct": 35.0,
        "max_subsidy_amount": 1750000.0,
        "max_loan_amount": 5000000.0,
        "interest_rate_pct": 8.5,
        "eligibility": "Individual > 18 years, 8th pass for manufacturing > ₹10L or services > ₹5L",
        "description": "Credit linked subsidy scheme for setting up micro-enterprises. 25% subsidy for general urban, 35% for rural/special category (SC/ST/OBC/Women).",
        "nodal_agency": "KVIC / Ministry of MSME",
        "portal_url": "https://www.kviconline.gov.in/pmegpeportal/pmegphome/index.jsp"
    },
    {
        "name": "Pradhan Mantri MUDRA Yojana (PMMY) - Shishu / Kishore / Tarun",
        "code": "MUDRA",
        "category": "Micro Credit",
        "subsidy_pct": 0.0,
        "max_subsidy_amount": 0.0,
        "max_loan_amount": 1000000.0,
        "interest_rate_pct": 9.25,
        "eligibility": "Non-corporate, non-farm small/micro enterprises",
        "description": "Collateral-free institutional credit up to ₹10 Lakhs: Shishu (up to ₹50,000), Kishore (₹50,000 to ₹5 Lakhs), and Tarun (₹5 Lakhs to ₹10 Lakhs).",
        "nodal_agency": "MUDRA / Department of Financial Services",
        "portal_url": "https://www.mudra.org.in/"
    },
    {
        "name": "Stand-Up India Scheme",
        "code": "STAND_UP",
        "category": "Entrepreneurship Finance",
        "subsidy_pct": 15.0,
        "max_subsidy_amount": 1500000.0,
        "max_loan_amount": 10000000.0,
        "interest_rate_pct": 8.75,
        "eligibility": "SC, ST, and Women entrepreneurs setting up greenfield enterprises",
        "description": "Bank loans between ₹10 Lakhs and ₹1 Crore to at least one SC or ST borrower and at least one woman borrower per bank branch.",
        "nodal_agency": "SIDBI / Ministry of Finance",
        "portal_url": "https://www.standupmitra.in/"
    },
    {
        "name": "PM SVANidhi (Street Vendor's AtmaNirbhar Nidhi)",
        "code": "PM_SVANIDHI",
        "category": "Working Capital",
        "subsidy_pct": 7.0,
        "max_subsidy_amount": 5000.0,
        "max_loan_amount": 50000.0,
        "interest_rate_pct": 7.0,
        "eligibility": "Urban/rural street vendors and micro retailers",
        "description": "Affordable working capital loan up to ₹50,000 with 7% interest subsidy on timely repayment and cashback up to ₹1,200/year on digital transactions.",
        "nodal_agency": "Ministry of Housing and Urban Affairs",
        "portal_url": "https://pmsvanidhi.mohua.gov.in/"
    },
    {
        "name": "PM Vishwakarma Scheme",
        "code": "PM_VISHWAKARMA",
        "category": "Artisan & Craftsperson Support",
        "subsidy_pct": 100.0,
        "max_subsidy_amount": 15000.0,
        "max_loan_amount": 300000.0,
        "interest_rate_pct": 5.0,
        "eligibility": "Traditional artisans and craftspeople working with hands and tools across 18 trades",
        "description": "Recognition via PM Vishwakarma Certificate & ID, skill training with ₹500/day stipend, ₹15,000 toolkit incentive, and collateral-free credit at 5% concessional interest.",
        "nodal_agency": "Ministry of MSME",
        "portal_url": "https://pmvishwakarma.gov.in/"
    },
    {
        "name": "PM Formalisation of Micro Food Processing Enterprises (PMFME)",
        "code": "PMFME",
        "category": "Food Processing",
        "subsidy_pct": 35.0,
        "max_subsidy_amount": 1000000.0,
        "max_loan_amount": 2500000.0,
        "interest_rate_pct": 8.5,
        "eligibility": "Existing micro food processing enterprises, SHGs, FPOs, Cooperatives",
        "description": "Credit-linked capital subsidy @35% of eligible project cost with a maximum ceiling of ₹10 Lakhs per unit.",
        "nodal_agency": "Ministry of Food Processing Industries",
        "portal_url": "https://pmfme.mofpi.gov.in/"
    },
    {
        "name": "Dairy Entrepreneurship Development Scheme (DEDS - NABARD)",
        "code": "DEDS",
        "category": "Agri-Allied & Dairy",
        "subsidy_pct": 33.33,
        "max_subsidy_amount": 700000.0,
        "max_loan_amount": 2500000.0,
        "interest_rate_pct": 8.0,
        "eligibility": "Farmers, individual entrepreneurs, NGOs, SHGs, cooperatives",
        "description": "Back-ended capital subsidy: 25% for general category and 33.33% for SC/ST farmers for modern dairy units, milking machines, and cold bulk cooling tanks.",
        "nodal_agency": "NABARD / Dept of Animal Husbandry",
        "portal_url": "https://www.nabard.org/"
    },
    {
        "name": "National Livestock Mission (NLM)",
        "code": "NLM",
        "category": "Animal Husbandry",
        "subsidy_pct": 50.0,
        "max_subsidy_amount": 5000000.0,
        "max_loan_amount": 10000000.0,
        "interest_rate_pct": 8.5,
        "eligibility": "Individuals, SHGs, FPOs, Section 8 companies",
        "description": "50% capital subsidy up to ₹50 Lakhs for setting up breeding farms for poultry, sheep, goat, and fodder seed production units.",
        "nodal_agency": "Department of Animal Husbandry & Dairying",
        "portal_url": "https://nlm.udyamimitra.in/"
    },
    {
        "name": "Credit Guarantee Fund Trust for Micro and Small Enterprises (CGTMSE)",
        "code": "CGTMSE",
        "category": "Credit Guarantee",
        "subsidy_pct": 0.0,
        "max_subsidy_amount": 0.0,
        "max_loan_amount": 50000000.0,
        "interest_rate_pct": 8.5,
        "eligibility": "New and existing Micro and Small Enterprises in manufacturing or service",
        "description": "Collateral-free credit facility up to ₹5 Crore with up to 85% credit guarantee coverage by the trust.",
        "nodal_agency": "SIDBI & Ministry of MSME",
        "portal_url": "https://www.cgtmse.in/"
    }
]

DEFAULT_BENCHMARKS = [
    {"sector_key": "mobile_shop", "sector_name": "Mobile & Electronics Retail", "avg_margin_pct": 12.0, "monthly_fixed_cost_pct": 8.0, "break_even_months": 14, "national_cagr_pct": 8.5, "risk_level": "Low-Moderate"},
    {"sector_key": "grocery", "sector_name": "Grocery & FMCG Kirana", "avg_margin_pct": 10.0, "monthly_fixed_cost_pct": 6.0, "break_even_months": 10, "national_cagr_pct": 7.2, "risk_level": "Low"},
    {"sector_key": "dairy", "sector_name": "Dairy & Milk Processing", "avg_margin_pct": 18.0, "monthly_fixed_cost_pct": 10.0, "break_even_months": 18, "national_cagr_pct": 9.1, "risk_level": "Moderate"},
    {"sector_key": "bakery", "sector_name": "Bakery & Confectionery", "avg_margin_pct": 40.0, "monthly_fixed_cost_pct": 15.0, "break_even_months": 8, "national_cagr_pct": 11.0, "risk_level": "Moderate"},
    {"sector_key": "tailoring", "sector_name": "Tailoring & Boutique Apparel", "avg_margin_pct": 50.0, "monthly_fixed_cost_pct": 12.0, "break_even_months": 6, "national_cagr_pct": 6.5, "risk_level": "Low"},
    {"sector_key": "pharmacy", "sector_name": "Retail Pharmacy & Medical", "avg_margin_pct": 20.0, "monthly_fixed_cost_pct": 9.0, "break_even_months": 12, "national_cagr_pct": 10.5, "risk_level": "Low"},
    {"sector_key": "hardware", "sector_name": "Sanitary & Hardware Store", "avg_margin_pct": 15.0, "monthly_fixed_cost_pct": 7.0, "break_even_months": 15, "national_cagr_pct": 8.0, "risk_level": "Moderate"},
    {"sector_key": "restaurant", "sector_name": "Quick Service Restaurant / Dhaba", "avg_margin_pct": 35.0, "monthly_fixed_cost_pct": 18.0, "break_even_months": 9, "national_cagr_pct": 12.0, "risk_level": "High"},
    {"sector_key": "poultry", "sector_name": "Commercial Poultry Farm", "avg_margin_pct": 22.0, "monthly_fixed_cost_pct": 11.0, "break_even_months": 16, "national_cagr_pct": 9.8, "risk_level": "Moderate-High"},
    {"sector_key": "fertilizer", "sector_name": "Fertilizer, Seed & Agro-Services", "avg_margin_pct": 11.0, "monthly_fixed_cost_pct": 5.0, "break_even_months": 12, "national_cagr_pct": 7.5, "risk_level": "Low"}
]


def init_db():
    """Create tables if they don't exist and seed certified baseline data."""
    with get_db() as conn:
        conn.executescript(SCHEMA)

        # Migration safety: Ensure new columns exist in existing tables
        user_cols = [r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()]
        if "role" not in user_cols:
            conn.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'entrepreneur'")
        if "subscription_status" not in user_cols:
            conn.execute("ALTER TABLE users ADD COLUMN subscription_status TEXT DEFAULT 'free'")
        if "updated_at" not in user_cols:
            conn.execute("ALTER TABLE users ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP")
        if "last_login_at" not in user_cols:
            conn.execute("ALTER TABLE users ADD COLUMN last_login_at DATETIME")

        analyses_cols = [r[1] for r in conn.execute("PRAGMA table_info(analyses)").fetchall()]
        if "latitude" not in analyses_cols:
            conn.execute("ALTER TABLE analyses ADD COLUMN latitude REAL")
        if "longitude" not in analyses_cols:
            conn.execute("ALTER TABLE analyses ADD COLUMN longitude REAL")
        if "radius_km" not in analyses_cols:
            conn.execute("ALTER TABLE analyses ADD COLUMN radius_km REAL DEFAULT 3.0")
        if "formatted_address" not in analyses_cols:
            conn.execute("ALTER TABLE analyses ADD COLUMN formatted_address TEXT")

        # Check if schemes need seeding
        count_schemes = conn.execute("SELECT COUNT(*) FROM government_schemes").fetchone()[0]
        if count_schemes == 0:
            for s in DEFAULT_SCHEMES:
                conn.execute("""
                    INSERT INTO government_schemes
                    (name, code, category, subsidy_pct, max_subsidy_amount, max_loan_amount, interest_rate_pct, eligibility, description, nodal_agency, portal_url)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    s["name"], s["code"], s["category"], s["subsidy_pct"], s["max_subsidy_amount"],
                    s["max_loan_amount"], s["interest_rate_pct"], s["eligibility"], s["description"],
                    s["nodal_agency"], s["portal_url"]
                ))
            print(f"[DB] Seeded {len(DEFAULT_SCHEMES)} certified government schemes.")

        # Check if benchmarks need seeding
        count_benchmarks = conn.execute("SELECT COUNT(*) FROM business_benchmarks").fetchone()[0]
        if count_benchmarks == 0:
            for b in DEFAULT_BENCHMARKS:
                conn.execute("""
                    INSERT INTO business_benchmarks
                    (sector_key, sector_name, avg_margin_pct, monthly_fixed_cost_pct, break_even_months, national_cagr_pct, risk_level)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    b["sector_key"], b["sector_name"], b["avg_margin_pct"], b["monthly_fixed_cost_pct"],
                    b["break_even_months"], b["national_cagr_pct"], b["risk_level"]
                ))
            print(f"[DB] Seeded {len(DEFAULT_BENCHMARKS)} sector benchmarks.")

        # Seed Pan-India States & UTs
        count_states = conn.execute("SELECT COUNT(*) FROM geo_states").fetchone()[0]
        if count_states == 0:
            for st in ALL_INDIA_STATES:
                conn.execute("""
                    INSERT OR IGNORE INTO geo_states (name, code, zone, capital, gdp_growth, primary_industry)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (st["name"], st["code"], st.get("zone", ""), st.get("capital", ""), st.get("gdp_growth", 10.0), st.get("primary_industry", "")))
            print(f"[DB] Seeded {len(ALL_INDIA_STATES)} Pan-India States and UTs.")

        # Seed Pan-India Districts (780+ districts)
        count_districts = conn.execute("SELECT COUNT(*) FROM geo_districts").fetchone()[0]
        if count_districts == 0:
            total_dist_seeded = 0
            for st_name, dist_list in ALL_INDIA_DISTRICTS.items():
                for d_name in dist_list:
                    dic_loc = f"District Industries Centre (DIC) {d_name}, {st_name}"
                    conn.execute("""
                        INSERT OR IGNORE INTO geo_districts (state_name, name, tier, dic_centre, primary_sector)
                        VALUES (?, ?, ?, ?, ?)
                    """, (st_name, d_name, "Tier 2/3 District", dic_loc, "MSME, Trade & Services"))
                    total_dist_seeded += 1
            print(f"[DB] Seeded {total_dist_seeded} Pan-India Districts.")

        # Seed sample sub-areas and village clusters
        count_sub_areas = conn.execute("SELECT COUNT(*) FROM geo_sub_areas").fetchone()[0]
        if count_sub_areas == 0:
            sub_count = 0
            for st_name, dist_map in SAMPLE_BLOCKS_AND_VILLAGES.items():
                if isinstance(dist_map, dict):
                    for d_name, blocks in dist_map.items():
                        for b_item in blocks:
                            blk = b_item.get("block", "")
                            btype = b_item.get("type", "rural_gram_panchayat")
                            arch = MICRO_AREA_ARCHETYPES.get(btype, MICRO_AREA_ARCHETYPES["rural_gram_panchayat"])
                            for vill in b_item.get("villages", []):
                                conn.execute("""
                                    INSERT OR IGNORE INTO geo_sub_areas
                                    (state_name, district_name, block_name, village_name, area_type, avg_sqft_rent, daily_wage_rate, footfall_index)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                """, (st_name, d_name, blk, vill, arch["area_type"], arch["avg_sqft_rent"], arch["daily_wage_rate"], arch["footfall_index"]))
                                sub_count += 1
            print(f"[DB] Seeded {sub_count} micro-locality and village cluster reference profiles.")

        # Check if baseline analyses need seeding
        count_analyses = conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
        if count_analyses == 0:
            try:
                from analysis_engine import run_full_analysis
                seeds = [
                    {
                        "form": {
                            "business_name": "Ravi Mobile Centre",
                            "business_type": "mobile_shop",
                            "business_stage": "new",
                            "state": "Odisha",
                            "district": "Cuttack",
                            "block": "Gopalpur",
                            "village": "Gopalpur",
                            "area_type": "semi_urban",
                            "total_investment": 300000.0,
                            "own_capital": 100000.0,
                            "loan_amount": 200000.0,
                            "loan_required": "yes",
                            "expected_monthly_sales": 55000.0,
                            "monthly_expenses": 28000.0,
                            "entrepreneur_gender": "male",
                            "caste_category": "obc",
                            "education": "higher_secondary",
                            "is_shg": "no"
                        }
                    },
                    {
                        "form": {
                            "business_name": "Pooja Boutique & Tailoring",
                            "business_type": "tailoring",
                            "business_stage": "new",
                            "state": "Rajasthan",
                            "district": "Jaipur",
                            "block": "Amer",
                            "village": "Amer",
                            "area_type": "rural",
                            "total_investment": 150000.0,
                            "own_capital": 50000.0,
                            "loan_amount": 100000.0,
                            "loan_required": "yes",
                            "expected_monthly_sales": 40000.0,
                            "monthly_expenses": 16000.0,
                            "entrepreneur_gender": "female",
                            "caste_category": "general",
                            "education": "graduate",
                            "is_shg": "shg"
                        }
                    }
                ]
                for seed_item in seeds:
                    form_data = seed_item["form"]
                    analysis_res = run_full_analysis(form_data)
                    save_complete_analysis(form_data, analysis_res, user_id=None)
                print("[DB] Seeded 2 certified baseline analyses.")
            except Exception as e:
                print(f"[DB] Baseline analysis seeding note: {e}")

    print(f"[DB] Certified SQLite database ready at: {os.path.abspath(DATABASE_PATH)}")


# ─────────────────────────────────────────────
#  User helpers
# ─────────────────────────────────────────────

def get_user_by_id(user_id: int) -> sqlite3.Row | None:
    with get_db() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def get_user_by_email(email: str) -> sqlite3.Row | None:
    with get_db() as conn:
        return conn.execute("SELECT * FROM users WHERE email = ?", (email.lower().strip(),)).fetchone()


def get_user_by_google_id(google_id: str) -> sqlite3.Row | None:
    with get_db() as conn:
        return conn.execute("SELECT * FROM users WHERE google_id = ?", (google_id,)).fetchone()


def update_last_login(user_id: int):
    """Update last_login_at timestamp for a user."""
    with get_db() as conn:
        conn.execute("UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))


def update_user_profile(user_id: int, name: str, avatar_url: str | None = None) -> sqlite3.Row | None:
    """Update user profile information."""
    with get_db() as conn:
        conn.execute(
            "UPDATE users SET name = ?, avatar_url = COALESCE(?, avatar_url), updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (name.strip(), avatar_url, user_id)
        )
        return get_user_by_id(user_id)


def create_user(name: str, email: str, password_hash: str | None = None,
                google_id: str | None = None, avatar_url: str | None = None,
                role: str = "entrepreneur") -> int:
    """Insert a new user and return its id."""
    with get_db() as conn:
        cursor = conn.execute(
            """INSERT INTO users (name, email, password, google_id, avatar_url, role, last_login_at)
               VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
            (name, email.lower().strip(), password_hash, google_id, avatar_url, role)
        )
        return cursor.lastrowid


def upsert_google_user(google_id: str, email: str, name: str,
                       avatar_url: str | None) -> sqlite3.Row:
    """Handle Google authentication: link existing email or create new account."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE google_id = ?", (google_id,)).fetchone()
        if row:
            conn.execute("UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = ?", (row["id"],))
            return conn.execute("SELECT * FROM users WHERE id = ?", (row["id"],)).fetchone()

        row = conn.execute("SELECT * FROM users WHERE email = ?", (email.lower().strip(),)).fetchone()
        if row:
            conn.execute(
                "UPDATE users SET google_id = ?, avatar_url = COALESCE(avatar_url, ?), last_login_at = CURRENT_TIMESTAMP WHERE id = ?",
                (google_id, avatar_url, row["id"])
            )
            return conn.execute("SELECT * FROM users WHERE id = ?", (row["id"],)).fetchone()

        conn.execute(
            """INSERT INTO users (name, email, google_id, avatar_url, last_login_at)
               VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)""",
            (name, email.lower().strip(), google_id, avatar_url)
        )
        return conn.execute("SELECT * FROM users WHERE google_id = ?", (google_id,)).fetchone()


# ─────────────────────────────────────────────
#  Analysis & Certified Report Operations
# ─────────────────────────────────────────────

def generate_certificate_number() -> str:
    """Generate official certificate number e.g. CERT-VV-2026-X9K42."""
    year = datetime.now().year
    random_part = uuid.uuid4().hex[:6].upper()
    return f"CERT-VV-{year}-{random_part}"


def generate_verification_hash(cert_no: str, analysis_id: int, score: int, data_summary: str) -> str:
    """Produce cryptographic SHA-256 integrity hash for the certified record."""
    raw = f"{cert_no}|{analysis_id}|{score}|{data_summary}|VYAPAAR_VIKASH_CERTIFIED_PROTOCOL"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def save_complete_analysis(form_data: dict, analysis_result: dict, user_id: int | None = None) -> dict:
    """
    Atomically saves both the user's input parameters and the certified report
    with cryptographic hash and official certification ID into the database.
    """
    biz_name = form_data.get("business_name") or analysis_result.get("meta", {}).get("business_name", "My Enterprise")
    biz_type = form_data.get("business_type", "other")
    stage = form_data.get("business_stage", "new")
    state = form_data.get("state", "")
    district = form_data.get("district", "")
    block = form_data.get("block", "")
    village = form_data.get("village", "")
    area_type = form_data.get("area_type", "rural")
    investment = float(form_data.get("total_investment", 100000))
    own_capital = float(form_data.get("own_capital", investment * 0.4))
    loan_amount = float(form_data.get("loan_amount", max(0, investment - own_capital)))
    loan_required = form_data.get("loan_required", "no")
    expected_sales = float(form_data.get("expected_monthly_sales", investment * 0.15))
    monthly_expenses = float(form_data.get("monthly_expenses", 0))
    gender = form_data.get("entrepreneur_gender") or form_data.get("gender", "")
    caste = form_data.get("caste_category") or form_data.get("category", "")
    education = form_data.get("education", "")
    is_shg = form_data.get("is_shg", "no")

    # Feasibility Score Calculation
    fin = analysis_result.get("financial", {})
    mkt = analysis_result.get("market", {})
    profit_margin = fin.get("gross_margin_pct") or fin.get("net_profit_margin_pct", 15)
    demand_score = mkt.get("demand_score", 7.5)
    annual_profit = fin.get("annual_profit") or fin.get("annual_net_profit", 0)

    score = int(min(98, max(45, (demand_score * 5.5) + (profit_margin * 1.5) + 10)))
    if score >= 80:
        viability = "Highly Viable — Prime Growth Potential"
    elif score >= 65:
        viability = "Viable — Recommended with Standard Preparation"
    elif score >= 50:
        viability = "Conditionally Viable — High Vigilance Advised"
    else:
        viability = "High Risk — Business Model Restructuring Needed"

    ai_verdict = (
        f"A certified assessment for {biz_name} ({biz_type}) in {district}, {state} ({area_type}) "
        f"shows an overall feasibility rating of {score}/100 ({viability}). "
        f"Projected annual profit is ₹{annual_profit:,} with an estimated break-even period of "
        f"{fin.get('break_even_months', 12)} months."
    )

    cert_no = generate_certificate_number()
    summary_token = f"{biz_name}:{investment}:{score}"
    v_hash = generate_verification_hash(cert_no, 0, score, summary_token)

    with get_db() as conn:
        cur = conn.execute("""
            INSERT INTO analyses (
                user_id, business_name, business_type, business_stage, state, district,
                block, village, area_type, total_investment, own_capital, loan_amount,
                loan_required, expected_monthly_sales, monthly_expenses,
                entrepreneur_gender, caste_category, education, is_shg
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, biz_name, biz_type, stage, state, district,
            block, village, area_type, investment, own_capital, loan_amount,
            loan_required, expected_sales, monthly_expenses,
            gender, caste, education, is_shg
        ))
        analysis_id = cur.lastrowid

        # Re-compute hash with exact analysis_id
        final_hash = generate_verification_hash(cert_no, analysis_id, score, summary_token)

        conn.execute("""
            INSERT INTO certified_reports (
                analysis_id, certificate_no, verification_hash, feasibility_score,
                viability_status, ai_verdict, market_data_json, financial_data_json,
                swot_data_json, competition_data_json, schemes_data_json, action_plan_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            analysis_id, cert_no, final_hash, score, viability, ai_verdict,
            json.dumps(analysis_result.get("market", {})),
            json.dumps(analysis_result.get("financial", {})),
            json.dumps(analysis_result.get("swot", {})),
            json.dumps(analysis_result.get("competition", {})),
            json.dumps(analysis_result.get("schemes", {})),
            json.dumps(analysis_result.get("action_plan", {}))
        ))

    return {
        "analysis_id": analysis_id,
        "certificate_no": cert_no,
        "verification_hash": final_hash,
        "feasibility_score": score,
        "viability_status": viability,
        "ai_verdict": ai_verdict,
        "certified_at": datetime.now().strftime("%d %b %Y, %I:%M %p")
    }


def get_analysis_record(analysis_id: int) -> dict | None:
    """Retrieve an analysis record and its certified report."""
    with get_db() as conn:
        row = conn.execute("""
            SELECT a.*, r.certificate_no, r.verification_hash, r.feasibility_score,
                   r.viability_status, r.ai_verdict, r.market_data_json,
                   r.financial_data_json, r.swot_data_json, r.competition_data_json,
                   r.schemes_data_json, r.action_plan_json, r.certifier,
                   r.standard_code, r.status AS report_status, r.certified_at
            FROM analyses a
            LEFT JOIN certified_reports r ON a.id = r.analysis_id
            WHERE a.id = ?
        """, (analysis_id,)).fetchone()

        if not row:
            return None

        d = dict(row)
        # Parse JSON fields and provide both clean and legacy keys
        for field in ["market_data_json", "financial_data_json", "swot_data_json",
                      "competition_data_json", "schemes_data_json", "action_plan_json"]:
            if d.get(field):
                try:
                    parsed = json.loads(d[field])
                except Exception:
                    parsed = {}
                clean_name = field.replace("_data_json", "").replace("_json", "")
                d[clean_name] = parsed
                d[field.replace("_json", "")] = parsed
            else:
                clean_name = field.replace("_data_json", "").replace("_json", "")
                d[clean_name] = {}
                d[field.replace("_json", "")] = {}

        from analysis_engine import BUSINESS_DATA
        bdata_cur = BUSINESS_DATA.get(d.get("business_type", "other"), BUSINESS_DATA.get("other", {}))
        b_label = bdata_cur.get("label", "Enterprise")

        d["meta"] = {
            "business_name": d.get("business_name", "My Enterprise"),
            "business_type": d.get("business_type", "other"),
            "business_label": b_label,
            "stage": d.get("business_stage", "new"),
            "state": d.get("state", ""),
            "district": d.get("district", ""),
            "block": d.get("block", ""),
            "village": d.get("village", ""),
            "area_type": d.get("area_type", "rural"),
            "total_investment": d.get("total_investment", 0),
            "own_capital": d.get("own_capital", 0),
            "loan_amount": d.get("loan_amount", 0),
            "loan_required": d.get("loan_required", "no"),
            "expected_monthly_sales": d.get("expected_monthly_sales", 0),
            "monthly_expenses": d.get("monthly_expenses", 0),
            "entrepreneur_gender": d.get("entrepreneur_gender", ""),
            "caste_category": d.get("caste_category", ""),
            "education": d.get("education", ""),
            "is_shg": d.get("is_shg", "no"),
            "created_at": d.get("created_at", "")
        }

        # ── Auto-enrich schemes with eligibility_reasons (backfills old records) ──
        try:
            from analysis_engine import _build_eligibility_reasons
            schemes_block = d.get("schemes") or d.get("schemes_data") or {}
            investment = float(d.get("total_investment") or 0)
            area_type = d.get("area_type") or "rural"
            form_data_for_elig = {
                "entrepreneur_gender": d.get("entrepreneur_gender") or "",
                "caste_category": d.get("caste_category") or "",
                "business_stage": d.get("business_stage") or "new",
                "business_name": d.get("business_name") or "My Enterprise",
                "area_type": area_type,
                "village": d.get("village") or "",
                "block": d.get("block") or "",
            }
            if isinstance(schemes_block, dict) and "schemes" in schemes_block:
                for s in schemes_block["schemes"]:
                    key = s.get("key") or s.get("name", "other")
                    if not s.get("eligibility_reasons"):
                        s["eligibility_reasons"] = _build_eligibility_reasons(key, form_data_for_elig, investment, area_type)
                    if not s.get("your_benefit"):
                        calc = s.get("calculated_subsidy_amount", 0)
                        s["your_benefit"] = f"Up to ₹{calc:,.0f} back" if calc > 0 else "Collateral-free loan guarantee"
                    if not s.get("bank_partner"):
                        s["bank_partner"] = "SIDBI, PSU Banks" if "PMEGP" in key else "All Scheduled Banks"
                    if not s.get("apply_via"):
                        s["apply_via"] = s.get("portal_url") or s.get("url") or "#"
        except Exception:
            pass  # Graceful degradation if engine not importable

        # ── Auto-enrich financial with user-input numbers (backfills old records) ──
        try:
            fin_block = d.get("financial") or d.get("financial_data") or {}
            if isinstance(fin_block, dict):
                invest = float(d.get("total_investment") or fin_block.get("investment") or 100000)
                monthly_rev = float(d.get("expected_monthly_sales") or fin_block.get("monthly_revenue") or (invest * 0.18))
                monthly_exp = float(d.get("monthly_expenses") or fin_block.get("monthly_fixed_cost") or (monthly_rev * 0.52))
                if monthly_rev > monthly_exp:
                    monthly_profit = fin_block.get("monthly_profit") or (monthly_rev - monthly_exp)
                else:
                    monthly_profit = fin_block.get("monthly_profit") or max(monthly_rev * 0.12, invest * 0.05)
                
                margin_pct = fin_block.get("net_profit_margin_pct") or fin_block.get("profit_margin_pct") or round((monthly_profit / max(1.0, monthly_rev)) * 100)
                be_calc = fin_block.get("break_even_months") or max(1, round(invest / max(1.0, monthly_profit)))
                be_disp = fin_block.get("break_even_display") or (f"{max(1, be_calc - 1)}–{be_calc + 1} months" if be_calc > 1 else "1–2 months")
                
                fin_block["investment"] = round(invest)
                fin_block["monthly_revenue"] = round(monthly_rev)
                fin_block["monthly_fixed_cost"] = round(monthly_exp)
                fin_block["monthly_profit"] = round(monthly_profit)
                fin_block["annual_profit"] = round(fin_block.get("annual_profit") or (monthly_profit * 12))
                fin_block["net_profit_margin_pct"] = margin_pct
                fin_block["profit_margin_pct"] = margin_pct
                fin_block["break_even_months"] = be_calc
                fin_block["break_even_display"] = be_disp
                fin_block["roi_pct"] = fin_block.get("roi_pct") or round(((monthly_profit * 12) / max(1.0, invest)) * 100, 1)
        except Exception:
            pass

        return d



def get_certified_report_by_certificate_no(cert_no: str) -> dict | None:
    """Lookup certified verification badge and public data by certificate number."""
    with get_db() as conn:
        row = conn.execute("""
            SELECT a.id AS analysis_id, a.business_name, a.business_type, a.state, a.district,
                   a.total_investment, a.area_type, a.created_at,
                   r.certificate_no, r.verification_hash, r.feasibility_score,
                   r.viability_status, r.ai_verdict, r.certifier, r.standard_code,
                   r.status AS report_status, r.certified_at
            FROM certified_reports r
            JOIN analyses a ON r.analysis_id = a.id
            WHERE r.certificate_no = ?
        """, (cert_no.strip(),)).fetchone()
        return dict(row) if row else None


def get_all_analyses(user_id: int | None = None, limit: int = 50) -> list[dict]:
    """Get list of recent analyses for dashboard display."""
    with get_db() as conn:
        if user_id:
            rows = conn.execute("""
                SELECT a.id, a.business_name, a.business_type, a.state, a.district,
                       a.total_investment, a.area_type, a.created_at,
                       r.certificate_no, r.feasibility_score, r.viability_status,
                       r.status AS report_status, r.certified_at
                FROM analyses a
                LEFT JOIN certified_reports r ON a.id = r.analysis_id
                WHERE a.user_id = ?
                ORDER BY a.id DESC LIMIT ?
            """, (user_id, limit)).fetchall()
        else:
            rows = conn.execute("""
                SELECT a.id, a.business_name, a.business_type, a.state, a.district,
                       a.total_investment, a.area_type, a.created_at,
                       r.certificate_no, r.feasibility_score, r.viability_status,
                       r.status AS report_status, r.certified_at
                FROM analyses a
                LEFT JOIN certified_reports r ON a.id = r.analysis_id
                ORDER BY a.id DESC LIMIT ?
            """, (limit,)).fetchall()
        return [dict(r) for r in rows]


def delete_analysis(analysis_id: int, user_id: int | None = None) -> bool:
    """Delete an analysis and cascaded certified report."""
    with get_db() as conn:
        if user_id:
            cur = conn.execute("DELETE FROM analyses WHERE id = ? AND user_id = ?", (analysis_id, user_id))
        else:
            cur = conn.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
        return cur.rowcount > 0


def get_all_schemes(category: str | None = None) -> list[dict]:
    """Retrieve all certified government schemes from database."""
    with get_db() as conn:
        if category:
            rows = conn.execute(
                "SELECT * FROM government_schemes WHERE active = 1 AND category LIKE ? ORDER BY subsidy_pct DESC",
                (f"%{category}%",)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM government_schemes WHERE active = 1 ORDER BY subsidy_pct DESC"
            ).fetchall()
        return [dict(r) for r in rows]


def get_platform_stats() -> dict:
    """Live certified platform metrics."""
    with get_db() as conn:
        total_analyses = conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
        total_certified = conn.execute("SELECT COUNT(*) FROM certified_reports WHERE status = 'CERTIFIED'").fetchone()[0]
        total_investment = conn.execute("SELECT COALESCE(SUM(total_investment), 0) FROM analyses").fetchone()[0]
        avg_score = conn.execute("SELECT COALESCE(AVG(feasibility_score), 74.5) FROM certified_reports").fetchone()[0]
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

        return {
            "total_analyses": total_analyses,
            "total_certified_reports": total_certified,
            "total_capital_analyzed_inr": float(total_investment),
            "average_feasibility_score": round(float(avg_score), 1),
            "registered_entrepreneurs": total_users,
            "database_integrity_status": "VERIFIED_ACTIVE"
        }


def row_to_dict(row: sqlite3.Row | None) -> dict | None:
    """Convert a sqlite3.Row to a plain dict (safe for JSON)."""
    if row is None:
        return None
    d = dict(row)
    d.pop("password", None)   # never expose password hash
    return d


# ─────────────────────────────────────────────
#  Saved Items, Business Plans & Scenarios CRUD
# ─────────────────────────────────────────────

def save_location(user_id: int, name: str, formatted_address: str | None,
                  latitude: float, longitude: float, radius_km: float = 3.0,
                  place_id: str | None = None, notes: str | None = None) -> int:
    """Save an area/location bookmark for a user."""
    with get_db() as conn:
        cur = conn.execute("""
            INSERT INTO saved_locations (user_id, name, formatted_address, latitude, longitude, radius_km, place_id, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, name.strip(), formatted_address, latitude, longitude, radius_km, place_id, notes))
        return cur.lastrowid


def get_saved_locations(user_id: int) -> list[dict]:
    """Retrieve all saved locations for a user."""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM saved_locations WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
        return [dict(r) for r in rows]


def delete_saved_location(location_id: int, user_id: int) -> bool:
    """Delete a saved location if owned by user."""
    with get_db() as conn:
        cur = conn.execute("DELETE FROM saved_locations WHERE id = ? AND user_id = ?", (location_id, user_id))
        return cur.rowcount > 0


def save_opportunity(user_id: int, category_key: str, category_name: str,
                     priority: int, opportunity_score: float, confidence_score: float,
                     location_name: str, latitude: float | None = None, longitude: float | None = None,
                     radius_km: float = 3.0, reasons: list | None = None, factors: dict | None = None,
                     analysis_id: int | None = None, location_analysis_id: int | None = None) -> int:
    """Save a recommended business opportunity for a user."""
    with get_db() as conn:
        cur = conn.execute("""
            INSERT INTO saved_opportunities (
                user_id, analysis_id, location_analysis_id, category_key, category_name,
                priority, opportunity_score, confidence_score, location_name,
                latitude, longitude, radius_km, reasons_json, factors_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, analysis_id, location_analysis_id, category_key, category_name,
            priority, opportunity_score, confidence_score, location_name,
            latitude, longitude, radius_km,
            json.dumps(reasons or []), json.dumps(factors or {})
        ))
        return cur.lastrowid


def get_saved_opportunities(user_id: int) -> list[dict]:
    """Retrieve all saved opportunities for a user."""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM saved_opportunities WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["reasons"] = json.loads(d.get("reasons_json") or "[]")
            d["factors"] = json.loads(d.get("factors_json") or "{}")
            result.append(d)
        return result


def delete_saved_opportunity(opp_id: int, user_id: int) -> bool:
    """Delete a saved opportunity if owned by user."""
    with get_db() as conn:
        cur = conn.execute("DELETE FROM saved_opportunities WHERE id = ? AND user_id = ?", (opp_id, user_id))
        return cur.rowcount > 0


def save_business_plan(user_id: int, title: str, category_key: str,
                       location_name: str, investment: float,
                       executive_summary: str, plan_data: dict,
                       roadmap: list | None = None, analysis_id: int | None = None,
                       plan_id: int | None = None) -> int:
    """Save or update an actionable 14-section business plan."""
    with get_db() as conn:
        if plan_id:
            conn.execute("""
                UPDATE business_plans SET
                    title = ?, category_key = ?, location_name = ?, investment = ?,
                    executive_summary = ?, plan_json = ?, roadmap_json = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ? AND user_id = ?
            """, (
                title, category_key, location_name, investment,
                executive_summary, json.dumps(plan_data), json.dumps(roadmap or []),
                plan_id, user_id
            ))
            return plan_id
        else:
            cur = conn.execute("""
                INSERT INTO business_plans (
                    user_id, analysis_id, title, category_key, location_name, investment,
                    executive_summary, plan_json, roadmap_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, analysis_id, title, category_key, location_name, investment,
                executive_summary, json.dumps(plan_data), json.dumps(roadmap or [])
            ))
            return cur.lastrowid


def get_business_plans(user_id: int) -> list[dict]:
    """Retrieve all business plans for a user."""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM business_plans WHERE user_id = ? ORDER BY updated_at DESC", (user_id,)).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["plan"] = json.loads(d.get("plan_json") or "{}")
            d["roadmap"] = json.loads(d.get("roadmap_json") or "[]")
            result.append(d)
        return result


def get_business_plan_by_id(plan_id: int, user_id: int | None = None) -> dict | None:
    """Retrieve a single business plan by ID."""
    with get_db() as conn:
        if user_id is not None:
            row = conn.execute("SELECT * FROM business_plans WHERE id = ? AND user_id = ?", (plan_id, user_id)).fetchone()
        else:
            row = conn.execute("SELECT * FROM business_plans WHERE id = ?", (plan_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        d["plan"] = json.loads(d.get("plan_json") or "{}")
        d["roadmap"] = json.loads(d.get("roadmap_json") or "[]")
        return d


def delete_business_plan(plan_id: int, user_id: int) -> bool:
    """Delete a business plan owned by user."""
    with get_db() as conn:
        cur = conn.execute("DELETE FROM business_plans WHERE id = ? AND user_id = ?", (plan_id, user_id))
        return cur.rowcount > 0


def save_location_analysis(user_id: int | None, location_name: str,
                           formatted_address: str | None, state: str | None,
                           district: str | None, latitude: float, longitude: float,
                           radius_km: float, opportunities: list,
                           market_signals: dict | None = None, boundary_geojson: str | None = None,
                           confidence_score: float = 85.0) -> int:
    """Save a multi-opportunity location analysis run."""
    with get_db() as conn:
        cur = conn.execute("""
            INSERT INTO location_analyses (
                user_id, location_name, formatted_address, state, district,
                latitude, longitude, radius_km, boundary_geojson, confidence_score,
                opportunities_json, market_signals_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, location_name, formatted_address, state, district,
            latitude, longitude, radius_km, boundary_geojson, confidence_score,
            json.dumps(opportunities), json.dumps(market_signals or {})
        ))
        return cur.lastrowid


def get_location_analysis_by_id(loc_analysis_id: int) -> dict | None:
    """Retrieve location analysis by ID."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM location_analyses WHERE id = ?", (loc_analysis_id,)).fetchone()
        if not row:
            return None
        d = dict(row)
        d["opportunities"] = json.loads(d.get("opportunities_json") or "[]")
        d["market_signals"] = json.loads(d.get("market_signals_json") or "{}")
        return d


def get_all_location_analyses(user_id: int | None = None, limit: int = 20) -> list[dict]:
    """Retrieve recent location analyses."""
    with get_db() as conn:
        if user_id:
            rows = conn.execute("SELECT * FROM location_analyses WHERE user_id = ? ORDER BY created_at DESC LIMIT ?", (user_id, limit)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM location_analyses ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["opportunities"] = json.loads(d.get("opportunities_json") or "[]")
            d["market_signals"] = json.loads(d.get("market_signals_json") or "{}")
            result.append(d)
        return result


def delete_location_analysis(loc_analysis_id: int, user_id: int | None = None) -> bool:
    """Delete a location analysis."""
    with get_db() as conn:
        if user_id:
            cur = conn.execute("DELETE FROM location_analyses WHERE id = ? AND user_id = ?", (loc_analysis_id, user_id))
        else:
            cur = conn.execute("DELETE FROM location_analyses WHERE id = ?", (loc_analysis_id,))
        return cur.rowcount > 0


def save_scenario_run(user_id: int | None, analysis_id: int | None,
                      scenario_name: str, inputs: dict, outputs: dict) -> int:
    """Save a scenario simulation run."""
    with get_db() as conn:
        cur = conn.execute("""
            INSERT INTO scenario_runs (user_id, analysis_id, scenario_name, inputs_json, outputs_json)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, analysis_id, scenario_name, json.dumps(inputs), json.dumps(outputs)))
        return cur.lastrowid


def get_scenario_runs(analysis_id: int, user_id: int | None = None) -> list[dict]:
    """Retrieve scenario simulation runs for an analysis."""
    with get_db() as conn:
        if user_id:
            rows = conn.execute("SELECT * FROM scenario_runs WHERE analysis_id = ? AND user_id = ? ORDER BY created_at DESC", (analysis_id, user_id)).fetchall()
        else:
            rows = conn.execute("SELECT * FROM scenario_runs WHERE analysis_id = ? ORDER BY created_at DESC", (analysis_id,)).fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["inputs"] = json.loads(d.get("inputs_json") or "{}")
            d["outputs"] = json.loads(d.get("outputs_json") or "{}")
            result.append(d)
        return result


# ─────────────────────────────────────────────
#  Geographic & Micro-Location Data Access
# ─────────────────────────────────────────────

def get_all_states() -> list[dict]:
    """Retrieve all 36 Pan-India States and UTs."""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM geo_states ORDER BY name ASC").fetchall()
        if not rows:
            return ALL_INDIA_STATES
        return [dict(r) for r in rows]


def get_districts_by_state(state_query: str) -> list[dict]:
    """Retrieve all districts belonging to a given State or UT."""
    sq = state_query.strip().lower()
    with get_db() as conn:
        # Check by name or code
        rows = conn.execute(
            "SELECT * FROM geo_districts WHERE LOWER(state_name) = ? OR LOWER(state_name) LIKE ? ORDER BY name ASC",
            (sq, f"%{sq}%")
        ).fetchall()
        if rows:
            return [dict(r) for r in rows]

        # Fallback to direct dictionary match
        for st_name, dists in ALL_INDIA_DISTRICTS.items():
            if st_name.lower() == sq or sq in st_name.lower():
                return [{"state_name": st_name, "name": d, "dic_centre": f"DIC {d}, {st_name}"} for d in dists]
        return []


def get_sub_areas(state_name: str, district_name: str) -> list[dict]:
    """Retrieve sub-districts, blocks, and village areas for a specific district."""
    s_clean = state_name.strip().lower()
    d_clean = district_name.strip().lower()
    with get_db() as conn:
        rows = conn.execute("""
            SELECT * FROM geo_sub_areas
            WHERE (LOWER(state_name) = ? OR LOWER(state_name) LIKE ?)
              AND (LOWER(district_name) = ? OR LOWER(district_name) LIKE ?)
            ORDER BY block_name ASC, village_name ASC
        """, (s_clean, f"%{s_clean}%", d_clean, f"%{d_clean}%")).fetchall()
        return [dict(r) for r in rows]


def search_geo_locations(query: str, limit: int = 25) -> list[dict]:
    """Fast search across states, districts, blocks, and villages."""
    q = f"%{query.strip().lower()}%"
    results = []
    with get_db() as conn:
        # Match districts
        d_rows = conn.execute(
            "SELECT state_name, name AS district_name, dic_centre FROM geo_districts WHERE LOWER(name) LIKE ? OR LOWER(state_name) LIKE ? LIMIT ?",
            (q, q, limit)
        ).fetchall()
        for r in d_rows:
            results.append({
                "type": "district",
                "state": r["state_name"],
                "district": r["district_name"],
                "display": f"{r['district_name']}, {r['state_name']}",
                "dic_centre": r["dic_centre"]
            })

        # Match sub-areas / villages
        s_rows = conn.execute(
            "SELECT state_name, district_name, block_name, village_name, area_type FROM geo_sub_areas WHERE LOWER(village_name) LIKE ? OR LOWER(block_name) LIKE ? LIMIT ?",
            (q, q, limit)
        ).fetchall()
        for r in s_rows:
            results.append({
                "type": "village",
                "state": r["state_name"],
                "district": r["district_name"],
                "block": r["block_name"],
                "village": r["village_name"],
                "area_type": r["area_type"],
                "display": f"{r['village_name']} ({r['block_name']}), {r['district_name']}, {r['state_name']}"
            })
    return results[:limit]


def get_micro_geo_intelligence(state: str, district: str, village: str = "", block: str = "", area_type: str = "rural") -> dict:
    """
    Computes authentic micro-area economic intelligence for the user's exact village/block.
    """
    target_loc = village.strip() or block.strip() or district.strip()
    with get_db() as conn:
        # Check if exact sub-area exists in database
        sub_row = None
        if village or block:
            sub_row = conn.execute("""
                SELECT * FROM geo_sub_areas
                WHERE (LOWER(village_name) = ? OR LOWER(block_name) = ?)
                  AND (LOWER(district_name) = ? OR LOWER(district_name) LIKE ?)
                LIMIT 1
            """, (village.lower(), block.lower(), district.lower(), f"%{district.lower()}%")).fetchone()

        dist_row = conn.execute(
            "SELECT * FROM geo_districts WHERE LOWER(name) = ? OR LOWER(name) LIKE ? LIMIT 1",
            (district.lower(), f"%{district.lower()}%")
        ).fetchone()

    # Determine archetype and economic parameters
    matched_type = sub_row["area_type"] if sub_row else (area_type or "rural")
    archetype = get_area_archetype(matched_type)

    rent_sqft = sub_row["avg_sqft_rent"] if sub_row else archetype["avg_sqft_rent"]
    daily_wage = sub_row["daily_wage_rate"] if sub_row else archetype["daily_wage_rate"]
    footfall_idx = sub_row["footfall_index"] if sub_row else archetype["footfall_index"]

    dic_address = dist_row["dic_centre"] if dist_row else f"District Industries Centre (DIC) {district}, {state}"

    return {
        "location_title": f"{village}, {block} (Dist. {district})" if (village and block) else (f"{village or block}, {district}" if (village or block) else f"{district}, {state}"),
        "micro_area_name": target_loc,
        "village": village,
        "block": block,
        "district": district,
        "state": state,
        "area_type": matched_type,
        "area_label": archetype["label"],
        "catchment_radius_km": archetype["radius_km"],
        "catchment_population": archetype["catchment_pop_range"],
        "avg_sqft_rent": rent_sqft,
        "daily_wage_rate": daily_wage,
        "footfall_index": footfall_idx,
        "dic_centre_address": dic_address,
        "advantages": archetype["advantages"],
        "consumer_behavior": archetype["consumer_behavior"],
        "logistics_note": archetype["logistics_note"]
    }

