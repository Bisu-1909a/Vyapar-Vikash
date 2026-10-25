import json

from analysis_engine import run_full_analysis
from ai import tools as T
from database import models as db


def test_every_tool_has_valid_schema():
    specs = T.openai_tool_specs()
    assert len(specs) == len(T.TOOLS) >= 10
    for s in specs:
        params = s["function"]["parameters"]
        assert params["type"] == "object"
        assert "$ref" not in json.dumps(params) and "$defs" not in params


def test_feasibility_tool_returns_engine_numbers_exactly(app):
    args = {"business_type": "grocery", "state": "Odisha", "district": "Cuttack", "total_investment": 300000}
    res = T.execute("run_feasibility_analysis", args, T.ToolContext())
    assert res["ok"], res
    engine = run_full_analysis({**args, "area_type": "rural", "business_stage": "new"})
    fin = res["data"]["financial"]
    for key in ("monthly_revenue", "monthly_profit", "annual_profit", "break_even_months", "roi_pct", "emi"):
        assert fin[key] == engine["financial"][key]
    assert res["data"]["schemes"]["estimated_subsidy"] == engine["schemes"]["estimated_subsidy"]


def test_validation_rejects_bad_and_extra_arguments(app):
    res = T.execute("run_feasibility_analysis",
                    {"business_type": "casino", "state": "Odisha", "district": "X", "total_investment": -1,
                     "user_id": 1}, T.ToolContext())
    assert not res["ok"] and res["error_type"] == "validation_error"
    fields = {e["field"] for e in res["error"]}
    assert {"business_type", "total_investment", "user_id"} <= fields


def test_invalid_json_and_unknown_tool(app):
    assert T.execute("run_feasibility_analysis", "{not json", T.ToolContext())["error_type"] == "validation_error"
    assert T.execute("drop_tables", {}, T.ToolContext())["error_type"] == "not_found"


def test_user_scoped_tools_require_auth_and_isolate_users(app):
    assert T.execute("list_my_analyses", {}, T.ToolContext())["error_type"] == "auth_required"
    a = db.create_user("A", "a-tools@example.com", "h")
    b = db.create_user("B", "b-tools@example.com", "h")
    form = {"business_type": "bakery", "state": "Odisha", "district": "Puri", "total_investment": 250000.0}
    aid = db.save_complete_analysis(form, run_full_analysis(form), user_id=a)["analysis_id"]

    mine = T.execute("list_my_analyses", {}, T.ToolContext(user_id=a))
    assert [r["id"] for r in mine["data"]["analyses"]] == [aid]
    assert T.execute("list_my_analyses", {}, T.ToolContext(user_id=b))["data"]["count"] == 0

    assert T.execute("get_analysis", {"analysis_id": aid}, T.ToolContext(user_id=a))["ok"]
    assert T.execute("get_analysis", {"analysis_id": aid}, T.ToolContext(user_id=b))["error_type"] == "forbidden"
    assert T.execute("get_analysis", {"analysis_id": aid}, T.ToolContext())["error_type"] == "forbidden"


def test_every_call_is_audited(app):
    uid = db.create_user("Audit", "audit@example.com", "h")
    T.execute("list_government_schemes", {"category": "Credit"}, T.ToolContext(user_id=uid, source="llm"))
    T.execute("search_locations", {"query": "x"}, T.ToolContext(user_id=uid))
    logs = db.get_tool_calls(user_id=uid)
    assert [(l["tool_name"], l["ok"]) for l in logs] == [("search_locations", False), ("list_government_schemes", True)]
    assert logs[1]["source"] == "llm"


def test_read_only_tools_cover_main_engines(app):
    ctx = T.ToolContext()
    assert T.execute("discover_opportunities", {"state": "Odisha", "district": "Cuttack"}, ctx)["data"]["top_opportunities"]
    sim = T.execute("simulate_scenario", {"category_key": "grocery", "state": "Odisha", "district": "Cuttack",
                                          "rent_delta_pct": 20}, ctx)
    assert sim["ok"] and "scenario_score" in sim["data"]
    plan = T.execute("generate_business_plan", {"category_key": "cafe", "location_name": "Cuttack",
                                                "investment": 400000}, ctx)
    assert plan["ok"] and plan["data"]["financial_summary"]
    intel = T.execute("get_location_intelligence", {"state": "Odisha", "district": "Cuttack"}, ctx)
    assert intel["ok"] and intel["data"]["district"] == "Cuttack"
