"""
tools.py – Typed tool registry shared by the REST API (/api/tools/<name>) and the LLM agent.

Each tool has a Pydantic input model (validated before anything runs), a short
description the LLM sees, and a function that calls the existing deterministic
engines / ORM data layer. Tools never accept a user id from the caller: the
signed-in user comes from the Flask session via ToolContext, so the LLM cannot
read another user's data. All tools are read-only; nothing here writes business
data (only the audit log row for each call).
"""

from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_BASE_DIR, os.path.join(_BASE_DIR, "backend"), os.path.join(_BASE_DIR, "database")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from analysis_engine import BUSINESS_DATA, run_full_analysis
from opportunity_engine import (
    OPPORTUNITY_CATALOGUE, evaluate_location_opportunities, generate_business_plan, simulate_scenario,
)
from geo_data import MICRO_AREA_ARCHETYPES
from database import models as db


BusinessType = Enum("BusinessType", {k: k for k in BUSINESS_DATA}, type=str)
OpportunityCategory = Enum("OpportunityCategory", {k: k for k in OPPORTUNITY_CATALOGUE}, type=str)

_AREA_TYPES = sorted({"rural", "semi_urban", "urban"}
                     | {a.get("area_type", "") for a in MICRO_AREA_ARCHETYPES.values()} - {""})
AreaType = Enum("AreaType", {k: k for k in _AREA_TYPES}, type=str)

MAX_INVESTMENT = 100_000_000  # ₹10 crore – upper bound for micro/small enterprises


class AuthRequired(Exception):
    pass


class ToolNotFound(Exception):
    pass


class Forbidden(Exception):
    pass


@dataclass
class ToolContext:
    user_id: Optional[int] = None
    source: str = "api"  # "api" | "llm"


class _In(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


Name = Field(min_length=1, max_length=120)


# ─────────────────────────────────────────────
#  Input models
# ─────────────────────────────────────────────

class NoInput(_In):
    pass


class FeasibilityInput(_In):
    business_type: BusinessType = Field(description="Business type key (see list_business_types).")
    state: str = Field(min_length=1, max_length=120, description="Indian state or UT, e.g. 'Odisha'.")
    district: str = Field(min_length=1, max_length=120, description="District, e.g. 'Cuttack'.")
    area_type: AreaType = Field(AreaType("rural"), description="Area type of the business location.")
    total_investment: float = Field(gt=0, le=MAX_INVESTMENT, description="Total project investment in INR.")
    own_capital: Optional[float] = Field(None, ge=0, le=MAX_INVESTMENT, description="Promoter's own capital in INR.")
    expected_monthly_sales: Optional[float] = Field(None, ge=0, le=MAX_INVESTMENT, description="Expected monthly sales in INR.")
    monthly_expenses: Optional[float] = Field(None, ge=0, le=MAX_INVESTMENT, description="Expected monthly expenses in INR.")
    business_name: Optional[str] = Field(None, max_length=120)
    block: Optional[str] = Field(None, max_length=120)
    village: Optional[str] = Field(None, max_length=120)
    business_stage: Optional[str] = Field("new", pattern=r"^(new|existing|expansion)$")
    entrepreneur_gender: Optional[str] = Field(None, pattern=r"^(male|female|other)$")
    caste_category: Optional[str] = Field(None, pattern=r"^(general|obc|sc|st|minority)$")

    @field_validator("own_capital")
    @classmethod
    def _own_capital_le_investment(cls, v, info):
        inv = info.data.get("total_investment")
        if v is not None and inv is not None and v > inv:
            raise ValueError("own_capital cannot exceed total_investment")
        return v


class AnalysisIdInput(_In):
    analysis_id: int = Field(gt=0, description="ID of a saved certified analysis.")


class LimitInput(_In):
    limit: int = Field(10, ge=1, le=20)


class SchemesInput(_In):
    category: Optional[str] = Field(None, max_length=80, description="Optional category filter, e.g. 'Credit'.")


class BenchmarkInput(_In):
    sector_key: Optional[str] = Field(None, max_length=60, description="Sector key, e.g. 'grocery'. Omit for all sectors.")


class DiscoverInput(_In):
    state: str = Field(min_length=1, max_length=120)
    district: str = Field(min_length=1, max_length=120)
    area_type: AreaType = AreaType("semi_urban")
    radius_km: float = Field(3.0, ge=0.5, le=50)
    investment_budget: float = Field(0, ge=0, le=MAX_INVESTMENT, description="Budget in INR; 0 = no budget filter.")
    top_n: int = Field(5, ge=1, le=5, description="How many ranked opportunities to return (engine ranks the top 5).")


class ScenarioInput(_In):
    category_key: OpportunityCategory
    state: str = Field(min_length=1, max_length=120)
    district: str = Field(min_length=1, max_length=120)
    area_type: AreaType = AreaType("semi_urban")
    radius_km: float = Field(3.0, ge=0.5, le=50)
    investment: float = Field(250000, gt=0, le=MAX_INVESTMENT)
    rent_delta_pct: float = Field(0, ge=-90, le=500, description="Change in rent, percent.")
    demand_delta_pct: float = Field(0, ge=-90, le=500, description="Change in demand, percent.")
    competitor_influx: int = Field(0, ge=0, le=50, description="Number of new competitors opening nearby.")


class PlanInput(_In):
    category_key: OpportunityCategory
    location_name: str = Field(min_length=1, max_length=200)
    investment: float = Field(gt=0, le=MAX_INVESTMENT)
    area_type: AreaType = AreaType("semi_urban")


class LocationIntelInput(_In):
    state: str = Field(min_length=1, max_length=120)
    district: str = Field(min_length=1, max_length=120)
    village: str = Field("", max_length=120)
    block: str = Field("", max_length=120)
    area_type: AreaType = AreaType("rural")


class SearchInput(_In):
    query: str = Field(min_length=2, max_length=80)
    limit: int = Field(10, ge=1, le=25)


# ─────────────────────────────────────────────
#  Output shaping – keep only fields the LLM needs, so answers stay grounded
# ─────────────────────────────────────────────

_FIN_KEYS = ("investment", "own_capital", "loan_amount", "monthly_revenue", "monthly_fixed_cost",
             "monthly_profit", "annual_profit", "break_even_revenue", "break_even_months",
             "break_even_display", "net_profit_margin_pct", "gross_margin_pct", "roi_pct", "emi", "tenure_months")


def _pick(d: dict, keys) -> dict:
    return {k: d.get(k) for k in keys if k in (d or {})}


def _summarise_analysis(result: dict, feasibility: dict) -> dict:
    fin = result.get("financial") or {}
    mkt = result.get("market") or {}
    comp = result.get("competition") or {}
    sch = result.get("schemes") or {}
    meta = result.get("meta") or {}
    return {
        "business": _pick(meta, ("business_name", "business_type", "business_label", "sector",
                                 "full_location_display", "area_type", "area_label", "stage")),
        "feasibility": _pick(feasibility, ("feasibility_score", "viability_status")),
        "financial": {
            **_pick(fin, _FIN_KEYS),
            "startup_costs": [_pick(c, ("name", "amount")) for c in fin.get("startup_costs") or []],
        },
        "market": _pick(mkt, ("market_size_cr", "growth_rate_pct", "demand_score", "catchment_population",
                              "catchment_radius_km")),
        "competition": _pick(comp, ("competition_density", "total_competitors_estimate", "market_gap")),
        "schemes": {
            "total_matched": sch.get("total_matched"),
            "estimated_subsidy": sch.get("estimated_subsidy"),
            "matched": [_pick(s, ("key", "name", "subsidy", "calculated_subsidy_amount", "portal_url"))
                        for s in sch.get("schemes") or []],
        },
    }


# ─────────────────────────────────────────────
#  Tool implementations
# ─────────────────────────────────────────────

def _list_business_types(_: NoInput, ctx: ToolContext) -> dict:
    return {
        "feasibility_business_types": [{"key": k, "label": v.get("label")} for k, v in BUSINESS_DATA.items()],
        "opportunity_categories": [{"key": k, "name": v.get("name")} for k, v in OPPORTUNITY_CATALOGUE.items()],
        "area_types": _AREA_TYPES,
    }


def _run_feasibility(inp: FeasibilityInput, ctx: ToolContext) -> dict:
    form = inp.model_dump(exclude_none=True, mode="json")
    result = run_full_analysis(form)
    biz_name = form.get("business_name") or result.get("meta", {}).get("business_name", "My Enterprise")
    feas = db.compute_feasibility(result, biz_name, form["business_type"], form["district"], form["state"],
                                  form["area_type"])
    out = _summarise_analysis(result, feas)
    out["note"] = "Computed live by the Vyapaar Vikash analysis engine; not saved."
    return out


def _get_analysis(inp: AnalysisIdInput, ctx: ToolContext) -> dict:
    exists, owner = db.get_analysis_owner(inp.analysis_id)
    if not exists:
        raise LookupError(f"Analysis #{inp.analysis_id} not found.")
    if owner is not None and owner != ctx.user_id:
        raise Forbidden("This analysis belongs to another user.")
    rec = db.get_analysis_record(inp.analysis_id)
    out = _summarise_analysis({**rec, "meta": rec.get("meta", {})}, rec)
    out["analysis_id"] = rec["id"]
    out["certificate_no"] = rec.get("certificate_no")
    out["created_at"] = rec.get("created_at")
    return out


def _list_my_analyses(inp: LimitInput, ctx: ToolContext) -> dict:
    rows = db.get_all_analyses(user_id=ctx.user_id, limit=inp.limit)
    return {"analyses": rows, "count": len(rows)}


def _list_schemes(inp: SchemesInput, ctx: ToolContext) -> dict:
    rows = db.get_all_schemes(category=inp.category)
    return {"schemes": [{k: v for k, v in r.items() if k not in ("id", "active")} for r in rows], "count": len(rows)}


def _get_benchmark(inp: BenchmarkInput, ctx: ToolContext) -> dict:
    if inp.sector_key:
        b = db.get_sector_benchmark(inp.sector_key)
        if not b:
            raise LookupError(f"No benchmark for sector '{inp.sector_key}'.")
        return {"benchmark": b}
    return {"benchmarks": db.get_all_benchmarks()}


def _discover(inp: DiscoverInput, ctx: ToolContext) -> dict:
    res = evaluate_location_opportunities(state=inp.state, district=inp.district, area_type=inp.area_type.value,
                                          radius_km=inp.radius_km, investment_budget=inp.investment_budget,
                                          location_name=f"{inp.district}, {inp.state}")
    top = []
    for o in (res.get("top_opportunities") or [])[: inp.top_n]:
        top.append({
            **_pick(o, ("category_key", "category_name", "sector", "opportunity_score", "confidence_score",
                        "avg_margin_pct", "break_even_months", "national_cagr_pct", "min_investment",
                        "max_investment", "priority")),
            "market_signals": o.get("market_signals"),
            "factor_scores": {k: _pick(v, ("score", "weight_pct", "interpretation"))
                              for k, v in (o.get("factor_scores") or {}).items()},
        })
    return {"location": _pick(res.get("location") or {}, ("name", "state", "district", "area_type", "radius_km")),
            "top_opportunities": top}


def _simulate(inp: ScenarioInput, ctx: ToolContext) -> dict:
    args = inp.model_dump(mode="json")
    res = simulate_scenario(**args)
    return {k: v for k, v in res.items() if k not in ("base_factors", "scenario_factors", "icon")}


def _plan(inp: PlanInput, ctx: ToolContext) -> dict:
    p = generate_business_plan(category_key=inp.category_key.value, location_name=inp.location_name,
                               investment=inp.investment, user_context={"area_type": inp.area_type.value})
    return {
        **_pick(p, ("title", "category_name", "location_name", "investment", "executive_summary", "financial_summary")),
        "section_titles": [s.get("title") for s in p.get("sections") or [] if isinstance(s, dict)],
        "roadmap": [_pick(r, ("step", "title", "timeline", "duration")) for r in p.get("roadmap") or []
                    if isinstance(r, dict)],
        "note": "Generated live; not saved. Users can save plans from the Plans page.",
    }


def _location_intel(inp: LocationIntelInput, ctx: ToolContext) -> dict:
    return db.get_micro_geo_intelligence(state=inp.state, district=inp.district, village=inp.village,
                                         block=inp.block, area_type=inp.area_type.value)


def _search_locations(inp: SearchInput, ctx: ToolContext) -> dict:
    return {"results": db.search_geo_locations(inp.query, limit=inp.limit)}


def _list_my_plans(inp: LimitInput, ctx: ToolContext) -> dict:
    plans = db.get_business_plans(ctx.user_id)[: inp.limit]
    keys = ("id", "title", "category_key", "location_name", "investment", "status", "executive_summary", "updated_at")
    return {"plans": [_pick(p, keys) for p in plans], "count": len(plans)}


def _list_my_saved_opportunities(inp: LimitInput, ctx: ToolContext) -> dict:
    opps = db.get_saved_opportunities(ctx.user_id)[: inp.limit]
    keys = ("id", "category_key", "category_name", "priority", "opportunity_score", "confidence_score",
            "location_name", "created_at")
    return {"saved_opportunities": [_pick(o, keys) for o in opps], "count": len(opps)}


# ─────────────────────────────────────────────
#  Registry
# ─────────────────────────────────────────────

@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    input_model: type[BaseModel]
    fn: Callable[[Any, ToolContext], dict]
    requires_auth: bool = False

    def json_schema(self) -> dict:
        return _inline_refs(self.input_model.model_json_schema())

    def openai_spec(self) -> dict:
        return {"type": "function",
                "function": {"name": self.name, "description": self.description, "parameters": self.json_schema()}}


def _inline_refs(schema: dict) -> dict:
    defs = schema.pop("$defs", {})

    def resolve(node):
        if isinstance(node, dict):
            if "$ref" in node:
                target = dict(defs[node["$ref"].split("/")[-1]])
                extra = {k: v for k, v in node.items() if k != "$ref"}
                return resolve({**target, **extra})
            if "allOf" in node and len(node["allOf"]) == 1:
                extra = {k: v for k, v in node.items() if k != "allOf"}
                return resolve({**node["allOf"][0], **extra})
            return {k: resolve(v) for k, v in node.items() if k != "title"}
        if isinstance(node, list):
            return [resolve(v) for v in node]
        return node

    out = resolve(schema)
    out.setdefault("properties", {})
    out["type"] = "object"
    return out


TOOLS: dict[str, Tool] = {t.name: t for t in [
    Tool("list_business_types", "List valid business type keys, opportunity category keys and area types.",
         NoInput, _list_business_types),
    Tool("run_feasibility_analysis",
         "Run the certified feasibility engine for a business idea: feasibility score, monthly revenue/profit, "
         "break-even, ROI, EMI, market size, competition and matched government schemes with subsidy amounts.",
         FeasibilityInput, _run_feasibility),
    Tool("get_analysis", "Fetch a saved certified analysis by id (only the user's own or public sample records).",
         AnalysisIdInput, _get_analysis),
    Tool("list_my_analyses", "List the signed-in user's saved analyses with feasibility scores.",
         LimitInput, _list_my_analyses, requires_auth=True),
    Tool("list_government_schemes", "List government schemes (subsidy %, max subsidy, max loan, interest rate, "
         "eligibility, portal) from the database.", SchemesInput, _list_schemes),
    Tool("get_sector_benchmark", "National sector benchmarks: average margin, fixed-cost %, break-even months, "
         "CAGR, risk level.", BenchmarkInput, _get_benchmark),
    Tool("discover_opportunities", "Rank the best business categories for a location with opportunity and "
         "confidence scores and factor breakdown.", DiscoverInput, _discover),
    Tool("simulate_scenario", "What-if simulation: change rent %, demand % or add competitors and see the "
         "score and profit impact for a category at a location.", ScenarioInput, _simulate),
    Tool("generate_business_plan", "Generate a business plan outline (summary, financial summary, roadmap) for a "
         "category, location and investment.", PlanInput, _plan),
    Tool("get_location_intelligence", "Micro-area economics for a state/district/block/village: rent per sqft, "
         "daily wage, footfall index, catchment, nearest District Industries Centre.",
         LocationIntelInput, _location_intel),
    Tool("search_locations", "Search Indian districts, blocks and villages by name.", SearchInput, _search_locations),
    Tool("list_my_business_plans", "List the signed-in user's saved business plans.",
         LimitInput, _list_my_plans, requires_auth=True),
    Tool("list_my_saved_opportunities", "List opportunities the signed-in user bookmarked.",
         LimitInput, _list_my_saved_opportunities, requires_auth=True),
]}


def list_tools() -> list[dict]:
    return [{"name": t.name, "description": t.description, "requires_auth": t.requires_auth,
             "input_schema": t.json_schema()} for t in TOOLS.values()]


def openai_tool_specs() -> list[dict]:
    return [t.openai_spec() for t in TOOLS.values()]


def execute(name: str, arguments: Any, ctx: ToolContext) -> dict:
    """
    Validate and run one tool. Always returns a JSON-safe dict:
      {"ok": True, "tool": name, "data": {...}}  or
      {"ok": False, "tool": name, "error_type": "...", "error": "..."}
    and writes one row to ai_tool_calls.
    """
    started = time.monotonic()
    args: Any = arguments
    result: dict
    try:
        if isinstance(arguments, str):
            args = json.loads(arguments or "{}")
        if args is None:
            args = {}
        if not isinstance(args, dict):
            raise ValueError("Tool arguments must be a JSON object.")
        tool = TOOLS.get(name)
        if not tool:
            raise ToolNotFound(f"Unknown tool '{name}'.")
        if tool.requires_auth and not ctx.user_id:
            raise AuthRequired("Sign in to use this tool.")
        inp = tool.input_model.model_validate(args)
        data = json.loads(json.dumps(tool.fn(inp, ctx), default=str))
        result = {"ok": True, "tool": name, "data": data}
    except ValidationError as e:
        errs = [{"field": ".".join(str(p) for p in err["loc"]), "message": err["msg"]} for err in e.errors()]
        result = {"ok": False, "tool": name, "error_type": "validation_error", "error": errs}
    except json.JSONDecodeError:
        result = {"ok": False, "tool": name, "error_type": "validation_error", "error": "Arguments are not valid JSON."}
    except ToolNotFound as e:
        result = {"ok": False, "tool": name, "error_type": "not_found", "error": str(e)}
    except AuthRequired as e:
        result = {"ok": False, "tool": name, "error_type": "auth_required", "error": str(e)}
    except Forbidden as e:
        result = {"ok": False, "tool": name, "error_type": "forbidden", "error": str(e)}
    except (LookupError, ValueError) as e:
        result = {"ok": False, "tool": name, "error_type": "invalid_request", "error": str(e)}
    except Exception as e:  # engine failure – never leak internals to the caller
        print(f"[AI Tools] {name} failed: {e!r}")
        result = {"ok": False, "tool": name, "error_type": "internal_error", "error": "Tool failed to run."}

    try:
        db.log_tool_call(
            tool_name=name[:100], arguments=args if isinstance(args, dict) else {"raw": str(args)[:500]},
            ok=result["ok"], user_id=ctx.user_id, source=ctx.source,
            error=None if result["ok"] else json.dumps(result.get("error"), default=str),
            duration_ms=int((time.monotonic() - started) * 1000),
        )
    except Exception as e:
        print(f"[AI Tools] audit log write failed: {e!r}")
    return result
