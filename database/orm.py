"""
orm.py – SQLAlchemy engine, session and table models for Vyapaar Vikash.

The database is chosen by environment:
  • DATABASE_URL  – e.g. postgresql+psycopg://user:pass@host:5432/vyapar  (production)
  • DATABASE_PATH – SQLite file used when DATABASE_URL is not set (local development)

All application data access goes through these models; no raw SQL strings.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from datetime import datetime
from typing import Iterator

from sqlalchemy import (
    Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint,
    create_engine, event, func,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE_DIR = os.path.dirname(_THIS_DIR)


def _resolve_sqlite_path() -> str:
    env_path = os.getenv("DATABASE_PATH")
    if env_path and os.path.isabs(env_path):
        return env_path
    if env_path and env_path not in ("db.sqlite3", "database/db.sqlite3"):
        return os.path.abspath(os.path.join(_BASE_DIR, env_path))
    return os.path.join(_THIS_DIR, "db.sqlite3")


def resolve_database_url() -> str:
    url = (os.getenv("DATABASE_URL") or "").strip()
    if not url:
        return f"sqlite:///{_resolve_sqlite_path()}"
    if url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    return url


_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def get_engine() -> Engine:
    global _engine, _SessionLocal
    if _engine is None:
        url = resolve_database_url()
        if url.startswith("sqlite"):
            _engine = create_engine(url, connect_args={"check_same_thread": False})
            event.listen(_engine, "connect", _sqlite_pragmas)
        else:
            _engine = create_engine(url, pool_pre_ping=True)
        _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False)
    return _engine


def reset_engine() -> None:
    """Dispose the current engine so the next call re-reads DATABASE_URL / DATABASE_PATH."""
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionLocal = None


def _sqlite_pragmas(dbapi_conn, _record):
    cur = dbapi_conn.cursor()
    cur.execute("PRAGMA foreign_keys=ON")
    cur.execute("PRAGMA journal_mode=WAL")
    cur.close()


@contextmanager
def session_scope() -> Iterator[Session]:
    """Transactional session: commits on success, rolls back on error."""
    get_engine()
    assert _SessionLocal is not None
    session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


class Base(DeclarativeBase):
    def to_dict(self) -> dict:
        out = {}
        for col in self.__table__.columns:
            val = getattr(self, col.key)
            if isinstance(val, datetime):
                val = val.strftime("%Y-%m-%d %H:%M:%S")
            out[col.name] = val
        return out


_now = func.current_timestamp()


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    password: Mapped[str | None] = mapped_column(Text)
    google_id: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    avatar_url: Mapped[str | None] = mapped_column(Text)
    role: Mapped[str | None] = mapped_column(String(50), default="entrepreneur")
    subscription_status: Mapped[str | None] = mapped_column(String(50), default="free")
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=_now)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=_now)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime)


class Analysis(Base):
    __tablename__ = "analyses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    business_name: Mapped[str] = mapped_column(Text, nullable=False)
    business_type: Mapped[str] = mapped_column(String(100), nullable=False)
    business_stage: Mapped[str | None] = mapped_column(String(50), default="new")
    state: Mapped[str | None] = mapped_column(Text)
    district: Mapped[str | None] = mapped_column(Text)
    block: Mapped[str | None] = mapped_column(Text)
    village: Mapped[str | None] = mapped_column(Text)
    area_type: Mapped[str | None] = mapped_column(String(50), default="rural")
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    radius_km: Mapped[float | None] = mapped_column(Float, default=3.0)
    formatted_address: Mapped[str | None] = mapped_column(Text)
    total_investment: Mapped[float] = mapped_column(Float, nullable=False, default=100000)
    own_capital: Mapped[float | None] = mapped_column(Float, default=0)
    loan_amount: Mapped[float | None] = mapped_column(Float, default=0)
    loan_required: Mapped[str | None] = mapped_column(String(10), default="no")
    expected_monthly_sales: Mapped[float | None] = mapped_column(Float, default=0)
    monthly_expenses: Mapped[float | None] = mapped_column(Float, default=0)
    entrepreneur_gender: Mapped[str | None] = mapped_column(String(50))
    caste_category: Mapped[str | None] = mapped_column(String(50))
    education: Mapped[str | None] = mapped_column(String(100))
    is_shg: Mapped[str | None] = mapped_column(String(10), default="no")
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=_now)


class CertifiedReport(Base):
    __tablename__ = "certified_reports"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    certificate_no: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    verification_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    feasibility_score: Mapped[int] = mapped_column(Integer, nullable=False)
    viability_status: Mapped[str] = mapped_column(Text, nullable=False)
    ai_verdict: Mapped[str] = mapped_column(Text, nullable=False)
    market_data_json: Mapped[str] = mapped_column(Text, nullable=False)
    financial_data_json: Mapped[str] = mapped_column(Text, nullable=False)
    swot_data_json: Mapped[str] = mapped_column(Text, nullable=False)
    competition_data_json: Mapped[str] = mapped_column(Text, nullable=False)
    schemes_data_json: Mapped[str] = mapped_column(Text, nullable=False)
    action_plan_json: Mapped[str] = mapped_column(Text, nullable=False)
    certifier: Mapped[str | None] = mapped_column(Text, default="National Rural MSME Intelligence & Assessment Board")
    standard_code: Mapped[str | None] = mapped_column(Text, default="ISO/IEC 27001 & MSME-NIESBUD Certified Protocol")
    status: Mapped[str | None] = mapped_column(String(32), default="CERTIFIED")
    certified_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=_now)


class LocationAnalysis(Base):
    __tablename__ = "location_analyses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    location_name: Mapped[str] = mapped_column(Text, nullable=False)
    formatted_address: Mapped[str | None] = mapped_column(Text)
    state: Mapped[str | None] = mapped_column(Text)
    district: Mapped[str | None] = mapped_column(Text)
    country: Mapped[str | None] = mapped_column(String(100), default="India")
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    radius_km: Mapped[float] = mapped_column(Float, nullable=False, default=3.0)
    boundary_geojson: Mapped[str | None] = mapped_column(Text)
    data_freshness: Mapped[str | None] = mapped_column(String(32), default="live")
    confidence_score: Mapped[float | None] = mapped_column(Float, default=85.0)
    opportunities_json: Mapped[str] = mapped_column(Text, nullable=False)
    market_signals_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=_now)


class SavedLocation(Base):
    __tablename__ = "saved_locations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    formatted_address: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    radius_km: Mapped[float | None] = mapped_column(Float, default=3.0)
    place_id: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=_now)


class SavedOpportunity(Base):
    __tablename__ = "saved_opportunities"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    analysis_id: Mapped[int | None] = mapped_column(Integer)
    location_analysis_id: Mapped[int | None] = mapped_column(Integer)
    category_key: Mapped[str] = mapped_column(String(100), nullable=False)
    category_name: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False)
    opportunity_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    location_name: Mapped[str] = mapped_column(Text, nullable=False)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    radius_km: Mapped[float | None] = mapped_column(Float, default=3.0)
    reasons_json: Mapped[str | None] = mapped_column(Text)
    factors_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=_now)


class BusinessPlan(Base):
    __tablename__ = "business_plans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    analysis_id: Mapped[int | None] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    category_key: Mapped[str] = mapped_column(String(100), nullable=False)
    location_name: Mapped[str] = mapped_column(Text, nullable=False)
    investment: Mapped[float] = mapped_column(Float, nullable=False)
    executive_summary: Mapped[str | None] = mapped_column(Text)
    plan_json: Mapped[str] = mapped_column(Text, nullable=False)
    roadmap_json: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str | None] = mapped_column(String(32), default="draft")
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=_now)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=_now)


class ScenarioRun(Base):
    __tablename__ = "scenario_runs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    analysis_id: Mapped[int | None] = mapped_column(Integer)
    scenario_name: Mapped[str] = mapped_column(Text, nullable=False)
    inputs_json: Mapped[str] = mapped_column(Text, nullable=False)
    outputs_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=_now)


class GovernmentScheme(Base):
    __tablename__ = "government_schemes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    category: Mapped[str] = mapped_column(Text, nullable=False)
    subsidy_pct: Mapped[float | None] = mapped_column(Float, default=0)
    max_subsidy_amount: Mapped[float | None] = mapped_column(Float, default=0)
    max_loan_amount: Mapped[float | None] = mapped_column(Float, default=0)
    interest_rate_pct: Mapped[float | None] = mapped_column(Float, default=0)
    eligibility: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    nodal_agency: Mapped[str | None] = mapped_column(Text)
    portal_url: Mapped[str | None] = mapped_column(Text)
    active: Mapped[int | None] = mapped_column(Integer, default=1)


class BusinessBenchmark(Base):
    __tablename__ = "business_benchmarks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sector_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    sector_name: Mapped[str] = mapped_column(Text, nullable=False)
    avg_margin_pct: Mapped[float] = mapped_column(Float, nullable=False)
    monthly_fixed_cost_pct: Mapped[float] = mapped_column(Float, nullable=False)
    break_even_months: Mapped[int] = mapped_column(Integer, nullable=False)
    national_cagr_pct: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(50), nullable=False)


class GeoState(Base):
    __tablename__ = "geo_states"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    zone: Mapped[str | None] = mapped_column(Text)
    capital: Mapped[str | None] = mapped_column(Text)
    gdp_growth: Mapped[float | None] = mapped_column(Float, default=10.0)
    primary_industry: Mapped[str | None] = mapped_column(Text)


class GeoDistrict(Base):
    __tablename__ = "geo_districts"
    __table_args__ = (UniqueConstraint("state_name", "name"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    state_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    tier: Mapped[str | None] = mapped_column(Text, default="Tier 3 / Rural")
    dic_centre: Mapped[str | None] = mapped_column(Text)
    primary_sector: Mapped[str | None] = mapped_column(Text)


class GeoSubArea(Base):
    __tablename__ = "geo_sub_areas"
    __table_args__ = (UniqueConstraint("state_name", "district_name", "block_name", "village_name"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    state_name: Mapped[str] = mapped_column(String(200), nullable=False)
    district_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    block_name: Mapped[str] = mapped_column(String(200), nullable=False)
    village_name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    area_type: Mapped[str | None] = mapped_column(String(50), default="rural")
    avg_sqft_rent: Mapped[float | None] = mapped_column(Float, default=15.0)
    daily_wage_rate: Mapped[float | None] = mapped_column(Float, default=380.0)
    footfall_index: Mapped[float | None] = mapped_column(Float, default=6.5)


class AiToolCall(Base):
    """Audit log of every tool invocation made through the AI tool layer."""
    __tablename__ = "ai_tool_calls"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    tool_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(16), nullable=False, default="api")
    arguments_json: Mapped[str] = mapped_column(Text, nullable=False, default="{}")
    ok: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    error: Mapped[str | None] = mapped_column(Text)
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=_now)
