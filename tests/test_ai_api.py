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
