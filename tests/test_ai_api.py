from api import ai_api


def test_tool_catalogue(client):
    r = client.get("/api/tools")
    assert r.status_code == 200
    names = {t["name"] for t in r.get_json()["tools"]}
    assert {"run_feasibility_analysis", "list_government_schemes", "list_my_business_plans"} <= names


def test_run_tool_status_codes(client):
    ok = client.post("/api/tools/list_government_schemes", json={})
    assert ok.status_code == 200 and ok.get_json()["data"]["count"] == 9
    assert client.post("/api/tools/run_feasibility_analysis", json={"business_type": "x"}).status_code == 400
    assert client.post("/api/tools/list_my_business_plans", json={}).status_code == 401
    assert client.post("/api/tools/does_not_exist", json={}).status_code == 404


def test_signed_in_user_tools(user_client):
    r = user_client.post("/api/tools/list_my_analyses", json={"limit": 5})
    assert r.status_code == 200 and r.get_json()["data"]["count"] == 0
    logs = user_client.get("/api/ai/tool_calls").get_json()["tool_calls"]
    assert logs[0]["tool_name"] == "list_my_analyses" and logs[0]["user_id"] == user_client.user["id"]


def test_advisor_uses_rules_without_llm_key(client):
    r = client.post("/api/ai/advisor", json={"message": "is it profitable?", "business_type": "grocery",
                                             "district": "Cuttack", "state": "Odisha", "investment": 300000})
    body = r.get_json()
    assert r.status_code == 200 and body["engine"] == "rules" and body["reply"]
    assert client.post("/api/ai/advisor", json={"message": "  "}).status_code == 400


def test_advisor_uses_llm_when_configured(client, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test")
    monkeypatch.setattr(ai_api.agent, "run_advisor",
                        lambda msg, profile, ctx, history=None: {"reply": "hi", "tools_used": [],
                                                                 "grounding": {"verified": True,
                                                                               "unverified_numbers": []},
                                                                 "model": "fake"})
    body = client.post("/api/ai/advisor", json={"message": "hello"}).get_json()
    assert body["engine"] == "llm" and body["reply"] == "hi"


def test_advisor_falls_back_when_llm_errors(client, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test")

    def boom(*a, **k):
        raise RuntimeError("provider down")

    monkeypatch.setattr(ai_api.agent, "run_advisor", boom)
    body = client.post("/api/ai/advisor", json={"message": "help me"}).get_json()
    assert body["engine"] == "rules_fallback" and body["reply"]


def test_rate_limit(client, monkeypatch):
    monkeypatch.setenv("AI_TOOLS_RATE_LIMIT_PER_MIN", "3")
    codes = [client.post("/api/tools/list_business_types", json={}).status_code for _ in range(4)]
    assert codes == [200, 200, 200, 429]


def test_rate_limiter_forgets_idle_identities():
    lim = ai_api._RateLimiter()
    for i in range(50):
        lim.allow(f"ip{i}", 5, window=60)
    lim._last_sweep -= 120
    for q in lim._hits.values():
        q[-1] -= 120
    lim.allow("fresh", 5, window=60)
    assert list(lim._hits) == ["fresh"]


def test_advisor_rejects_other_users_analysis(user_client, app):
    from analysis_engine import run_full_analysis
    from database import models as db
    other = db.create_user("Other", "other-adv@example.com", "h")
    form = {"business_type": "grocery", "state": "Odisha", "district": "Cuttack", "total_investment": 200000.0}
    aid = db.save_complete_analysis(form, run_full_analysis(form), user_id=other)["analysis_id"]
    r = user_client.post("/api/ai/advisor", json={"message": "profit?", "analysis_id": aid})
    assert r.status_code == 403
    assert user_client.post("/api/ai/advisor", json={"message": "x", "analysis_id": "abc"}).status_code == 400


def test_rate_limit_uses_forwarded_ip_only_when_trusted(client, monkeypatch):
    monkeypatch.setenv("AI_TOOLS_RATE_LIMIT_PER_MIN", "1")
    call = lambda ip: client.post("/api/tools/list_business_types", json={},
                                  headers={"X-Forwarded-For": ip}).status_code
    assert [call("1.1.1.1"), call("2.2.2.2")] == [200, 429]
    monkeypatch.setenv("TRUST_PROXY", "1")
    ai_api._limiter._hits.clear()
    assert [call("1.1.1.1"), call("2.2.2.2"), call("1.1.1.1")] == [200, 200, 429]


def test_forwarded_ip_ignored_from_non_local_peer(client, monkeypatch):
    monkeypatch.setenv("AI_TOOLS_RATE_LIMIT_PER_MIN", "1")
    monkeypatch.setenv("TRUST_PROXY", "1")
    call = lambda ip: client.post("/api/tools/list_business_types", json={}, headers={"X-Forwarded-For": ip},
                                  environ_base={"REMOTE_ADDR": "203.0.113.9"}).status_code
    assert [call("1.1.1.1"), call("2.2.2.2")] == [200, 429]


def test_configured_trusted_proxy_network(client, monkeypatch):
    monkeypatch.setenv("AI_TOOLS_RATE_LIMIT_PER_MIN", "1")
    monkeypatch.setenv("TRUST_PROXY", "1")
    monkeypatch.setenv("TRUSTED_PROXIES", "10.0.0.0/24")
    call = lambda ip: client.post("/api/tools/list_business_types", json={}, headers={"X-Forwarded-For": ip},
                                  environ_base={"REMOTE_ADDR": "10.0.0.5"}).status_code
    assert [call("1.1.1.1"), call("2.2.2.2")] == [200, 200]
