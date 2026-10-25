"""
models.py – Certified data-access layer for Vyapaar Vikash.

Every function here goes through SQLAlchemy ORM models (see database/orm.py),
so the same code runs on PostgreSQL (DATABASE_URL) and SQLite (local fallback).
Public function names and return shapes are unchanged from the original
sqlite3 implementation so API routes keep working.
"""

import os
import sys
import json
import hashlib
import uuid
from datetime import datetime
from contextlib import contextmanager

from sqlalchemy import delete, func, or_, select

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE_DIR = os.path.dirname(_THIS_DIR)
_BACKEND_DIR = os.path.join(_BASE_DIR, "backend")
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)

from geo_data import ALL_INDIA_STATES, ALL_INDIA_DISTRICTS, MICRO_AREA_ARCHETYPES, SAMPLE_BLOCKS_AND_VILLAGES, get_area_archetype

try:
    from database.orm import (
        Base, User, Analysis, CertifiedReport, LocationAnalysis, SavedLocation,
        SavedOpportunity, BusinessPlan, ScenarioRun, GovernmentScheme,
        BusinessBenchmark, GeoState, GeoDistrict, GeoSubArea, AiToolCall,
        get_engine, session_scope, resolve_database_url, _resolve_sqlite_path,
    )
except ImportError:
    from orm import (
        Base, User, Analysis, CertifiedReport, LocationAnalysis, SavedLocation,
        SavedOpportunity, BusinessPlan, ScenarioRun, GovernmentScheme,
        BusinessBenchmark, GeoState, GeoDistrict, GeoSubArea, AiToolCall,
        get_engine, session_scope, resolve_database_url, _resolve_sqlite_path,
    )

DATABASE_PATH = _resolve_sqlite_path()


@contextmanager
def get_db():
    """Transactional ORM session (kept under the old name for compatibility)."""
    with session_scope() as s:
        yield s


def _loads(raw, default):
    try:
        return json.loads(raw) if raw else default
    except (TypeError, ValueError):
        return default


def _ilike_contains(column, text: str):
    return func.lower(column).contains(text.strip().lower(), autoescape=True)


# ─────────────────────────────────────────────
#  Seed data
# ─────────────────────────────────────────────

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


def _seed_reference_data(s) -> None:
    if not s.scalar(select(func.count()).select_from(GovernmentScheme)):
        s.add_all(GovernmentScheme(**sc) for sc in DEFAULT_SCHEMES)
        print(f"[DB] Seeded {len(DEFAULT_SCHEMES)} certified government schemes.")

    if not s.scalar(select(func.count()).select_from(BusinessBenchmark)):
        s.add_all(BusinessBenchmark(**b) for b in DEFAULT_BENCHMARKS)
        print(f"[DB] Seeded {len(DEFAULT_BENCHMARKS)} sector benchmarks.")

    if not s.scalar(select(func.count()).select_from(GeoState)):
        seen_names, seen_codes = set(), set()
        for st in ALL_INDIA_STATES:
            if st["name"] in seen_names or st["code"] in seen_codes:
                continue
            seen_names.add(st["name"]); seen_codes.add(st["code"])
            s.add(GeoState(name=st["name"], code=st["code"], zone=st.get("zone", ""),
                           capital=st.get("capital", ""), gdp_growth=st.get("gdp_growth", 10.0),
                           primary_industry=st.get("primary_industry", "")))
        print(f"[DB] Seeded {len(seen_names)} Pan-India States and UTs.")

    if not s.scalar(select(func.count()).select_from(GeoDistrict)):
        seen = set()
        for st_name, dist_list in ALL_INDIA_DISTRICTS.items():
            for d_name in dist_list:
                if (st_name, d_name) in seen:
                    continue
                seen.add((st_name, d_name))
                s.add(GeoDistrict(state_name=st_name, name=d_name, tier="Tier 2/3 District",
                                  dic_centre=f"District Industries Centre (DIC) {d_name}, {st_name}",
                                  primary_sector="MSME, Trade & Services"))
        print(f"[DB] Seeded {len(seen)} Pan-India Districts.")

    if not s.scalar(select(func.count()).select_from(GeoSubArea)):
        seen = set()
        for st_name, dist_map in SAMPLE_BLOCKS_AND_VILLAGES.items():
            if not isinstance(dist_map, dict):
                continue
            for d_name, blocks in dist_map.items():
                for b_item in blocks:
                    blk = b_item.get("block", "")
                    btype = b_item.get("type", "rural_gram_panchayat")
                    arch = MICRO_AREA_ARCHETYPES.get(btype, MICRO_AREA_ARCHETYPES["rural_gram_panchayat"])
                    for vill in b_item.get("villages", []):
                        key = (st_name, d_name, blk, vill)
                        if key in seen:
                            continue
                        seen.add(key)
                        s.add(GeoSubArea(state_name=st_name, district_name=d_name, block_name=blk,
                                         village_name=vill, area_type=arch["area_type"],
                                         avg_sqft_rent=arch["avg_sqft_rent"],
                                         daily_wage_rate=arch["daily_wage_rate"],
                                         footfall_index=arch["footfall_index"]))
        print(f"[DB] Seeded {len(seen)} micro-locality and village cluster reference profiles.")


def _apply_migrations(engine) -> None:
    """
    Bring the schema to the latest Alembic revision.
    Fresh database → run migrations. Pre-Alembic database (tables created by the old
    sqlite3 code) → create any missing tables, then stamp it as current.
    """
    from sqlalchemy import inspect
    try:
        from alembic import command
        from alembic.config import Config
    except ImportError:
        Base.metadata.create_all(engine)
        return

    cfg = Config(os.path.join(_BASE_DIR, "alembic.ini"))
    cfg.set_main_option("script_location", os.path.join(_BASE_DIR, "migrations"))
    insp = inspect(engine)
    with engine.begin() as conn:
        cfg.attributes["connection"] = conn
        if not insp.has_table("alembic_version") and insp.has_table("users"):
            Base.metadata.create_all(conn)
            command.stamp(cfg, "head")
        else:
            command.upgrade(cfg, "head")


def init_db():
    """Create/upgrade tables and seed certified baseline data."""
    engine = get_engine()
    _apply_migrations(engine)

    with session_scope() as s:
        _seed_reference_data(s)
        needs_baseline = not s.scalar(select(func.count()).select_from(Analysis))

    if needs_baseline:
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
                save_complete_analysis(form_data, run_full_analysis(form_data), user_id=None)
            print("[DB] Seeded 2 certified baseline analyses.")
        except Exception as e:
            print(f"[DB] Baseline analysis seeding note: {e}")

    print(f"[DB] Database ready: {engine.url.render_as_string(hide_password=True)}")


# ─────────────────────────────────────────────
#  User helpers
# ─────────────────────────────────────────────

def _user_dict(u: User | None) -> dict | None:
    return u.to_dict() if u else None


def get_user_by_id(user_id: int) -> dict | None:
    with session_scope() as s:
        return _user_dict(s.get(User, user_id))


def get_user_by_email(email: str) -> dict | None:
    with session_scope() as s:
        return _user_dict(s.scalar(select(User).where(User.email == email.lower().strip())))


def get_user_by_google_id(google_id: str) -> dict | None:
    with session_scope() as s:
        return _user_dict(s.scalar(select(User).where(User.google_id == google_id)))


def update_last_login(user_id: int):
    """Update last_login_at timestamp for a user."""
    with session_scope() as s:
        u = s.get(User, user_id)
        if u:
            u.last_login_at = datetime.now()


def update_user_profile(user_id: int, name: str, avatar_url: str | None = None) -> dict | None:
    """Update user profile information."""
    with session_scope() as s:
        u = s.get(User, user_id)
        if u:
            u.name = name.strip()
            if avatar_url is not None:
                u.avatar_url = avatar_url
            u.updated_at = datetime.now()
    return get_user_by_id(user_id)


def create_user(name: str, email: str, password_hash: str | None = None,
                google_id: str | None = None, avatar_url: str | None = None,
                role: str = "entrepreneur") -> int:
    """Insert a new user and return its id."""
    with session_scope() as s:
        u = User(name=name, email=email.lower().strip(), password=password_hash,
                 google_id=google_id, avatar_url=avatar_url, role=role,
                 last_login_at=datetime.now())
        s.add(u)
        s.flush()
        return u.id


def upsert_google_user(google_id: str, email: str, name: str,
                       avatar_url: str | None) -> dict:
    """Handle Google authentication: link existing email or create new account."""
    now = datetime.now()
    with session_scope() as s:
        u = s.scalar(select(User).where(User.google_id == google_id))
        if not u:
            u = s.scalar(select(User).where(User.email == email.lower().strip()))
            if u:
                u.google_id = google_id
                u.avatar_url = u.avatar_url or avatar_url
            else:
                u = User(name=name, email=email.lower().strip(), google_id=google_id, avatar_url=avatar_url)
                s.add(u)
        u.last_login_at = now
        s.flush()
        return u.to_dict()


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


def compute_feasibility(analysis_result: dict, biz_name: str, biz_type: str,
                        district: str, state: str, area_type: str) -> dict:
    """Deterministic feasibility score, viability band and verdict for an analysis result."""
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
    return {"feasibility_score": score, "viability_status": viability, "ai_verdict": ai_verdict}


def save_complete_analysis(form_data: dict, analysis_result: dict, user_id: int | None = None) -> dict:
    """
    Atomically saves both the user's input parameters and the certified report
    with cryptographic hash and official certification ID into the database.
    """
    biz_name = form_data.get("business_name") or analysis_result.get("meta", {}).get("business_name", "My Enterprise")
    biz_type = form_data.get("business_type", "other")
    state = form_data.get("state", "")
    district = form_data.get("district", "")
    area_type = form_data.get("area_type", "rural")
    investment = float(form_data.get("total_investment", 100000))
    own_capital = float(form_data.get("own_capital", investment * 0.4))

    verdict = compute_feasibility(analysis_result, biz_name, biz_type, district, state, area_type)
    score = verdict["feasibility_score"]
    cert_no = generate_certificate_number()
    summary_token = f"{biz_name}:{investment}:{score}"

    with session_scope() as s:
        a = Analysis(
            user_id=user_id, business_name=biz_name, business_type=biz_type,
            business_stage=form_data.get("business_stage", "new"), state=state, district=district,
            block=form_data.get("block", ""), village=form_data.get("village", ""), area_type=area_type,
            total_investment=investment, own_capital=own_capital,
            loan_amount=float(form_data.get("loan_amount", max(0, investment - own_capital))),
            loan_required=form_data.get("loan_required", "no"),
            expected_monthly_sales=float(form_data.get("expected_monthly_sales", investment * 0.15)),
            monthly_expenses=float(form_data.get("monthly_expenses", 0)),
            entrepreneur_gender=form_data.get("entrepreneur_gender") or form_data.get("gender", ""),
            caste_category=form_data.get("caste_category") or form_data.get("category", ""),
            education=form_data.get("education", ""), is_shg=form_data.get("is_shg", "no"),
        )
        s.add(a)
        s.flush()
        analysis_id = a.id
        final_hash = generate_verification_hash(cert_no, analysis_id, score, summary_token)
        s.add(CertifiedReport(
            analysis_id=analysis_id, certificate_no=cert_no, verification_hash=final_hash,
            feasibility_score=score, viability_status=verdict["viability_status"],
            ai_verdict=verdict["ai_verdict"],
            market_data_json=json.dumps(analysis_result.get("market", {})),
            financial_data_json=json.dumps(analysis_result.get("financial", {})),
            swot_data_json=json.dumps(analysis_result.get("swot", {})),
            competition_data_json=json.dumps(analysis_result.get("competition", {})),
            schemes_data_json=json.dumps(analysis_result.get("schemes", {})),
            action_plan_json=json.dumps(analysis_result.get("action_plan", {})),
        ))

    return {
        "analysis_id": analysis_id,
        "certificate_no": cert_no,
        "verification_hash": final_hash,
        "feasibility_score": score,
        "viability_status": verdict["viability_status"],
        "ai_verdict": verdict["ai_verdict"],
        "certified_at": datetime.now().strftime("%d %b %Y, %I:%M %p")
    }


_REPORT_FIELDS = (
    "certificate_no", "verification_hash", "feasibility_score", "viability_status", "ai_verdict",
    "market_data_json", "financial_data_json", "swot_data_json", "competition_data_json",
    "schemes_data_json", "action_plan_json", "certifier", "standard_code",
)


def _merge_report(d: dict, r: CertifiedReport | None, fields=_REPORT_FIELDS) -> dict:
    for f in fields:
        d[f] = getattr(r, f) if r else None
    d["report_status"] = r.status if r else None
    d["certified_at"] = r.to_dict()["certified_at"] if r else None
    return d


def get_analysis_owner(analysis_id: int) -> tuple[bool, int | None]:
    """Return (exists, user_id) for an analysis without loading the report."""
    with session_scope() as s:
        a = s.get(Analysis, analysis_id)
        return (a is not None, a.user_id if a else None)


def get_analysis_record(analysis_id: int) -> dict | None:
    """Retrieve an analysis record and its certified report."""
    with session_scope() as s:
        row = s.execute(
            select(Analysis, CertifiedReport)
            .outerjoin(CertifiedReport, CertifiedReport.analysis_id == Analysis.id)
            .where(Analysis.id == analysis_id)
        ).first()
        if not row:
            return None
        d = _merge_report(row[0].to_dict(), row[1])

    for field in ["market_data_json", "financial_data_json", "swot_data_json",
                  "competition_data_json", "schemes_data_json", "action_plan_json"]:
        parsed = _loads(d.get(field), {}) if d.get(field) else {}
        clean_name = field.replace("_data_json", "").replace("_json", "")
        d[clean_name] = parsed
        d[field.replace("_json", "")] = parsed

    return _enrich_analysis_record(d)


def _enrich_analysis_record(d: dict) -> dict:
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
    with session_scope() as s:
        row = s.execute(
            select(Analysis, CertifiedReport)
            .join(CertifiedReport, CertifiedReport.analysis_id == Analysis.id)
            .where(CertifiedReport.certificate_no == cert_no.strip())
        ).first()
        if not row:
            return None
        a, r = row
        d = {k: a.to_dict()[k] for k in ("business_name", "business_type", "state", "district",
                                          "total_investment", "area_type", "created_at")}
        d["analysis_id"] = a.id
        return _merge_report(d, r, fields=("certificate_no", "verification_hash", "feasibility_score",
                                           "viability_status", "ai_verdict", "certifier", "standard_code"))


def get_all_analyses(user_id: int | None = None, limit: int = 50) -> list[dict]:
    """Get list of recent analyses for dashboard display."""
    stmt = (select(Analysis, CertifiedReport)
            .outerjoin(CertifiedReport, CertifiedReport.analysis_id == Analysis.id)
            .order_by(Analysis.id.desc()).limit(limit))
    if user_id:
        stmt = stmt.where(Analysis.user_id == user_id)
    out = []
    with session_scope() as s:
        for a, r in s.execute(stmt).all():
            ad = a.to_dict()
            d = {k: ad[k] for k in ("id", "business_name", "business_type", "state", "district",
                                    "total_investment", "area_type", "created_at")}
            out.append(_merge_report(d, r, fields=("certificate_no", "feasibility_score", "viability_status")))
    return out


def delete_analysis(analysis_id: int, user_id: int | None = None) -> bool:
    """Delete an analysis and cascaded certified report."""
    with session_scope() as s:
        stmt = select(Analysis).where(Analysis.id == analysis_id)
        if user_id:
            stmt = stmt.where(Analysis.user_id == user_id)
        a = s.scalar(stmt)
        if not a:
            return False
        s.execute(delete(CertifiedReport).where(CertifiedReport.analysis_id == a.id))
        s.delete(a)
        return True


def get_all_schemes(category: str | None = None) -> list[dict]:
    """Retrieve all certified government schemes from database."""
    stmt = select(GovernmentScheme).where(GovernmentScheme.active == 1).order_by(GovernmentScheme.subsidy_pct.desc())
    if category:
        stmt = stmt.where(GovernmentScheme.category.contains(category, autoescape=True))
    with session_scope() as s:
        return [g.to_dict() for g in s.scalars(stmt)]


def get_sector_benchmark(sector_key: str) -> dict | None:
    """National benchmark figures for a sector key (e.g. 'grocery')."""
    with session_scope() as s:
        b = s.scalar(select(BusinessBenchmark).where(BusinessBenchmark.sector_key == sector_key))
        return b.to_dict() if b else None


def get_all_benchmarks() -> list[dict]:
    with session_scope() as s:
        return [b.to_dict() for b in s.scalars(select(BusinessBenchmark).order_by(BusinessBenchmark.sector_key))]


def get_platform_stats() -> dict:
    """Live certified platform metrics."""
    with session_scope() as s:
        total_analyses = s.scalar(select(func.count()).select_from(Analysis))
        total_certified = s.scalar(select(func.count()).select_from(CertifiedReport).where(CertifiedReport.status == "CERTIFIED"))
        total_investment = s.scalar(select(func.coalesce(func.sum(Analysis.total_investment), 0)))
        avg_score = s.scalar(select(func.coalesce(func.avg(CertifiedReport.feasibility_score), 74.5)))
        total_users = s.scalar(select(func.count()).select_from(User))

    return {
        "total_analyses": total_analyses,
        "total_certified_reports": total_certified,
        "total_capital_analyzed_inr": float(total_investment),
        "average_feasibility_score": round(float(avg_score), 1),
        "registered_entrepreneurs": total_users,
        "database_integrity_status": "VERIFIED_ACTIVE"
    }


def row_to_dict(row) -> dict | None:
    """Convert a user record to a plain dict that never exposes the password hash."""
    if row is None:
        return None
    d = dict(row)
    d.pop("password", None)
    return d


# ─────────────────────────────────────────────
#  Saved Items, Business Plans & Scenarios CRUD
# ─────────────────────────────────────────────

def _delete_owned(model, obj_id: int, user_id: int | None) -> bool:
    with session_scope() as s:
        stmt = select(model).where(model.id == obj_id)
        if user_id:
            stmt = stmt.where(model.user_id == user_id)
        obj = s.scalar(stmt)
        if not obj:
            return False
        s.delete(obj)
        return True


def _insert(obj) -> int:
    with session_scope() as s:
        s.add(obj)
        s.flush()
        return obj.id


def save_location(user_id: int, name: str, formatted_address: str | None,
                  latitude: float, longitude: float, radius_km: float = 3.0,
                  place_id: str | None = None, notes: str | None = None) -> int:
    """Save an area/location bookmark for a user."""
    return _insert(SavedLocation(user_id=user_id, name=name.strip(), formatted_address=formatted_address,
                                 latitude=latitude, longitude=longitude, radius_km=radius_km,
                                 place_id=place_id, notes=notes))


def get_saved_locations(user_id: int) -> list[dict]:
    """Retrieve all saved locations for a user."""
    with session_scope() as s:
        rows = s.scalars(select(SavedLocation).where(SavedLocation.user_id == user_id)
                         .order_by(SavedLocation.created_at.desc(), SavedLocation.id.desc()))
        return [r.to_dict() for r in rows]


def delete_saved_location(location_id: int, user_id: int) -> bool:
    """Delete a saved location if owned by user."""
    return _delete_owned(SavedLocation, location_id, user_id) if user_id else False


def save_opportunity(user_id: int, category_key: str, category_name: str,
                     priority: int, opportunity_score: float, confidence_score: float,
                     location_name: str, latitude: float | None = None, longitude: float | None = None,
                     radius_km: float = 3.0, reasons: list | None = None, factors: dict | None = None,
                     analysis_id: int | None = None, location_analysis_id: int | None = None) -> int:
    """Save a recommended business opportunity for a user."""
    return _insert(SavedOpportunity(
        user_id=user_id, analysis_id=analysis_id, location_analysis_id=location_analysis_id,
        category_key=category_key, category_name=category_name, priority=priority,
        opportunity_score=opportunity_score, confidence_score=confidence_score,
        location_name=location_name, latitude=latitude, longitude=longitude, radius_km=radius_km,
        reasons_json=json.dumps(reasons or []), factors_json=json.dumps(factors or {}),
    ))


def get_saved_opportunities(user_id: int) -> list[dict]:
    """Retrieve all saved opportunities for a user."""
    with session_scope() as s:
        rows = s.scalars(select(SavedOpportunity).where(SavedOpportunity.user_id == user_id)
                         .order_by(SavedOpportunity.created_at.desc(), SavedOpportunity.id.desc()))
        result = []
        for r in rows:
            d = r.to_dict()
            d["reasons"] = _loads(d.get("reasons_json"), [])
            d["factors"] = _loads(d.get("factors_json"), {})
            result.append(d)
        return result


def delete_saved_opportunity(opp_id: int, user_id: int) -> bool:
    """Delete a saved opportunity if owned by user."""
    return _delete_owned(SavedOpportunity, opp_id, user_id) if user_id else False


def _plan_dict(p: BusinessPlan) -> dict:
    d = p.to_dict()
    d["plan"] = _loads(d.get("plan_json"), {})
    d["roadmap"] = _loads(d.get("roadmap_json"), [])
    return d


def save_business_plan(user_id: int, title: str, category_key: str,
                       location_name: str, investment: float,
                       executive_summary: str, plan_data: dict,
                       roadmap: list | None = None, analysis_id: int | None = None,
                       plan_id: int | None = None) -> int:
    """Save or update an actionable 14-section business plan."""
    with session_scope() as s:
        if plan_id:
            p = s.scalar(select(BusinessPlan).where(BusinessPlan.id == plan_id, BusinessPlan.user_id == user_id))
            if p:
                p.title, p.category_key, p.location_name = title, category_key, location_name
                p.investment, p.executive_summary = investment, executive_summary
                p.plan_json, p.roadmap_json = json.dumps(plan_data), json.dumps(roadmap or [])
                p.updated_at = datetime.now()
            return plan_id
        p = BusinessPlan(user_id=user_id, analysis_id=analysis_id, title=title, category_key=category_key,
                         location_name=location_name, investment=investment,
                         executive_summary=executive_summary, plan_json=json.dumps(plan_data),
                         roadmap_json=json.dumps(roadmap or []))
        s.add(p)
        s.flush()
        return p.id


def get_business_plans(user_id: int) -> list[dict]:
    """Retrieve all business plans for a user."""
    with session_scope() as s:
        rows = s.scalars(select(BusinessPlan).where(BusinessPlan.user_id == user_id)
                         .order_by(BusinessPlan.updated_at.desc(), BusinessPlan.id.desc()))
        return [_plan_dict(p) for p in rows]


def get_business_plan_by_id(plan_id: int, user_id: int | None = None) -> dict | None:
    """Retrieve a single business plan by ID."""
    stmt = select(BusinessPlan).where(BusinessPlan.id == plan_id)
    if user_id is not None:
        stmt = stmt.where(BusinessPlan.user_id == user_id)
    with session_scope() as s:
        p = s.scalar(stmt)
        return _plan_dict(p) if p else None


def delete_business_plan(plan_id: int, user_id: int) -> bool:
    """Delete a business plan owned by user."""
    return _delete_owned(BusinessPlan, plan_id, user_id) if user_id else False


def save_location_analysis(user_id: int | None, location_name: str,
                           formatted_address: str | None, state: str | None,
                           district: str | None, latitude: float, longitude: float,
                           radius_km: float, opportunities: list,
                           market_signals: dict | None = None, boundary_geojson: str | None = None,
                           confidence_score: float = 85.0) -> int:
    """Save a multi-opportunity location analysis run."""
    return _insert(LocationAnalysis(
        user_id=user_id, location_name=location_name, formatted_address=formatted_address,
        state=state, district=district, latitude=latitude, longitude=longitude, radius_km=radius_km,
        boundary_geojson=boundary_geojson, confidence_score=confidence_score,
        opportunities_json=json.dumps(opportunities), market_signals_json=json.dumps(market_signals or {}),
    ))


def _loc_analysis_dict(r: LocationAnalysis) -> dict:
    d = r.to_dict()
    d["opportunities"] = _loads(d.get("opportunities_json"), [])
    d["market_signals"] = _loads(d.get("market_signals_json"), {})
    return d


def get_location_analysis_by_id(loc_analysis_id: int) -> dict | None:
    """Retrieve location analysis by ID."""
    with session_scope() as s:
        r = s.get(LocationAnalysis, loc_analysis_id)
        return _loc_analysis_dict(r) if r else None


def get_all_location_analyses(user_id: int | None = None, limit: int = 20) -> list[dict]:
    """Retrieve recent location analyses."""
    stmt = select(LocationAnalysis).order_by(LocationAnalysis.created_at.desc(), LocationAnalysis.id.desc()).limit(limit)
    if user_id:
        stmt = stmt.where(LocationAnalysis.user_id == user_id)
    with session_scope() as s:
        return [_loc_analysis_dict(r) for r in s.scalars(stmt)]


def delete_location_analysis(loc_analysis_id: int, user_id: int | None = None) -> bool:
    """Delete a location analysis."""
    return _delete_owned(LocationAnalysis, loc_analysis_id, user_id)


def save_scenario_run(user_id: int | None, analysis_id: int | None,
                      scenario_name: str, inputs: dict, outputs: dict) -> int:
    """Save a scenario simulation run."""
    return _insert(ScenarioRun(user_id=user_id, analysis_id=analysis_id, scenario_name=scenario_name,
                               inputs_json=json.dumps(inputs), outputs_json=json.dumps(outputs)))


def get_scenario_runs(analysis_id: int, user_id: int | None = None) -> list[dict]:
    """Retrieve scenario simulation runs for an analysis."""
    stmt = select(ScenarioRun).where(ScenarioRun.analysis_id == analysis_id).order_by(ScenarioRun.created_at.desc(), ScenarioRun.id.desc())
    if user_id:
        stmt = stmt.where(ScenarioRun.user_id == user_id)
    with session_scope() as s:
        result = []
        for r in s.scalars(stmt):
            d = r.to_dict()
            d["inputs"] = _loads(d.get("inputs_json"), {})
            d["outputs"] = _loads(d.get("outputs_json"), {})
            result.append(d)
        return result


# ─────────────────────────────────────────────
#  Geographic & Micro-Location Data Access
# ─────────────────────────────────────────────

def get_all_states() -> list[dict]:
    """Retrieve all 36 Pan-India States and UTs."""
    with session_scope() as s:
        rows = [r.to_dict() for r in s.scalars(select(GeoState).order_by(GeoState.name.asc()))]
    return rows or ALL_INDIA_STATES


def get_districts_by_state(state_query: str) -> list[dict]:
    """Retrieve all districts belonging to a given State or UT."""
    sq = state_query.strip().lower()
    with session_scope() as s:
        rows = s.scalars(select(GeoDistrict).where(_ilike_contains(GeoDistrict.state_name, sq))
                         .order_by(GeoDistrict.name.asc())).all()
        if rows:
            return [r.to_dict() for r in rows]

    for st_name, dists in ALL_INDIA_DISTRICTS.items():
        if st_name.lower() == sq or sq in st_name.lower():
            return [{"state_name": st_name, "name": d, "dic_centre": f"DIC {d}, {st_name}"} for d in dists]
    return []


def get_sub_areas(state_name: str, district_name: str) -> list[dict]:
    """Retrieve sub-districts, blocks, and village areas for a specific district."""
    with session_scope() as s:
        rows = s.scalars(
            select(GeoSubArea)
            .where(_ilike_contains(GeoSubArea.state_name, state_name),
                   _ilike_contains(GeoSubArea.district_name, district_name))
            .order_by(GeoSubArea.block_name.asc(), GeoSubArea.village_name.asc())
        )
        return [r.to_dict() for r in rows]


def search_geo_locations(query: str, limit: int = 25) -> list[dict]:
    """Fast search across states, districts, blocks, and villages."""
    results = []
    with session_scope() as s:
        for r in s.scalars(select(GeoDistrict).where(or_(_ilike_contains(GeoDistrict.name, query),
                                                         _ilike_contains(GeoDistrict.state_name, query))).limit(limit)):
            results.append({
                "type": "district",
                "state": r.state_name,
                "district": r.name,
                "display": f"{r.name}, {r.state_name}",
                "dic_centre": r.dic_centre
            })
        for r in s.scalars(select(GeoSubArea).where(or_(_ilike_contains(GeoSubArea.village_name, query),
                                                        _ilike_contains(GeoSubArea.block_name, query))).limit(limit)):
            results.append({
                "type": "village",
                "state": r.state_name,
                "district": r.district_name,
                "block": r.block_name,
                "village": r.village_name,
                "area_type": r.area_type,
                "display": f"{r.village_name} ({r.block_name}), {r.district_name}, {r.state_name}"
            })
    return results[:limit]


def get_micro_geo_intelligence(state: str, district: str, village: str = "", block: str = "", area_type: str = "rural") -> dict:
    """
    Computes authentic micro-area economic intelligence for the user's exact village/block.
    """
    target_loc = village.strip() or block.strip() or district.strip()
    with session_scope() as s:
        sub_row = None
        if village or block:
            sub_row = s.scalar(
                select(GeoSubArea)
                .where(or_(func.lower(GeoSubArea.village_name) == village.lower(),
                           func.lower(GeoSubArea.block_name) == block.lower()),
                       _ilike_contains(GeoSubArea.district_name, district))
                .limit(1)
            )
            sub_row = sub_row.to_dict() if sub_row else None
        dist_row = s.scalar(select(GeoDistrict).where(_ilike_contains(GeoDistrict.name, district)).limit(1))
        dist_row = dist_row.to_dict() if dist_row else None

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


# ─────────────────────────────────────────────
#  AI tool-call audit log
# ─────────────────────────────────────────────

def log_tool_call(tool_name: str, arguments: dict, ok: bool, user_id: int | None = None,
                  source: str = "api", error: str | None = None, duration_ms: int | None = None) -> int:
    return _insert(AiToolCall(user_id=user_id, tool_name=tool_name, source=source,
                              arguments_json=json.dumps(arguments, default=str), ok=ok,
                              error=(error or None) and error[:2000], duration_ms=duration_ms))


def get_tool_calls(user_id: int | None = None, limit: int = 50) -> list[dict]:
    stmt = select(AiToolCall).order_by(AiToolCall.id.desc()).limit(limit)
    if user_id:
        stmt = stmt.where(AiToolCall.user_id == user_id)
    with session_scope() as s:
        return [r.to_dict() for r in s.scalars(stmt)]
