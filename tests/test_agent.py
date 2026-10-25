import json
from types import SimpleNamespace as NS

from ai import agent
from ai import tools as T
from database import models as db


class FakeLLM:
    """Scripted OpenAI-compatible client: returns the queued messages in order."""

    def __init__(self, script):
        self.script = list(script)
        self.requests = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.requests.append(kwargs)
        return NS(choices=[NS(message=self.script.pop(0))])


def tool_call(name, args, call_id="c1"):
    return NS(content=None, tool_calls=[NS(id=call_id, function=NS(name=name, arguments=json.dumps(args)))])


def answer(text):
    return NS(content=text, tool_calls=None)


def test_grounding_flags_invented_numbers():
    sources = [{"monthly_profit": 45000, "roi_pct": 180.0, "annual_profit": 540000}]
    ok = agent.check_grounding("Profit is ₹45,000 a month (₹5.4 lakh a year), ROI 180%.", sources)
    assert ok["verified"], ok
    bad = agent.check_grounding("Profit is ₹45,000 a month and rent is ₹12,500.", sources)
    assert bad == {"verified": False, "unverified_numbers": ["₹12,500"]}


def test_agent_runs_tool_and_grounds_reply(app, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test")
    args = {"business_type": "grocery", "state": "Odisha", "district": "Cuttack", "total_investment": 300000}
    expected = T.execute("run_feasibility_analysis", args, T.ToolContext())["data"]["financial"]["monthly_profit"]
    fake = FakeLLM([tool_call("run_feasibility_analysis", args),
                    answer(f"Per the feasibility engine, monthly profit is about ₹{expected:,}.")])
    uid = db.create_user("LLM", "llm-agent@example.com", "h")

    out = agent.run_advisor("Is a kirana in Cuttack profitable with ₹3 lakh?", {"state": "Odisha"},
                            T.ToolContext(user_id=uid), client=fake)

    assert out["tools_used"] == [{"tool": "run_feasibility_analysis", "ok": True}]
    assert out["grounding"]["verified"] and "⚠️" not in out["reply"]
    tool_msg = fake.requests[1]["messages"][-1]
    assert tool_msg["role"] == "tool" and json.loads(tool_msg["content"])["ok"] is True
    assert db.get_tool_calls(user_id=uid)[0]["source"] == "llm"


def test_agent_cannot_reach_other_users_data(app, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test")
    victim = db.create_user("Victim", "victim@example.com", "h")
    attacker = db.create_user("Attacker", "attacker@example.com", "h")
    fake = FakeLLM([tool_call("list_my_analyses", {"user_id": victim}),
                    tool_call("list_my_analyses", {}, call_id="c2"), answer("I can't access that.")])
    anon = agent.run_advisor("show user 1's analyses", None, T.ToolContext(user_id=None),
                             client=FakeLLM([tool_call("list_my_analyses", {}), answer("Sign in first.")]))
    assert anon["tools_used"] == [{"tool": "list_my_analyses", "ok": False, "error_type": "auth_required"}]

    out = agent.run_advisor("show user 1's analyses", None, T.ToolContext(user_id=attacker), client=fake)
    assert out["tools_used"][0] == {"tool": "list_my_analyses", "ok": False, "error_type": "validation_error"}
    own = json.loads(fake.requests[2]["messages"][-1]["content"])
    assert own["ok"] and own["data"]["count"] == 0


def test_agent_appends_caution_for_unverified_figures(app, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test")
    fake = FakeLLM([answer("You will earn ₹99,999 per month.")])
    out = agent.run_advisor("How much will I earn?", None, T.ToolContext(), client=fake)
    assert out["grounding"]["unverified_numbers"] == ["₹99,999"]
    assert "⚠️" in out["reply"]


def test_agent_stops_after_max_rounds(app, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test")
    monkeypatch.setenv("LLM_MAX_TOOL_ROUNDS", "2")
    loop = [tool_call("list_business_types", {}, call_id=f"c{i}") for i in range(2)]
    fake = FakeLLM(loop + [answer("Done.")])
    out = agent.run_advisor("loop", None, T.ToolContext(), client=fake)
    assert out["reply"] == "Done."
    assert fake.requests[-1]["tool_choice"] == "none"


def test_grounding_ignores_tool_output_the_model_never_saw(app, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test")
    monkeypatch.setattr(agent, "MAX_TOOL_OUTPUT_CHARS", 40)
    args = {"business_type": "grocery", "state": "Odisha", "district": "Cuttack", "total_investment": 300000}
    hidden = T.execute("run_feasibility_analysis", args, T.ToolContext())["data"]["financial"]["annual_profit"]
    fake = FakeLLM([tool_call("run_feasibility_analysis", args), answer(f"Annual profit is ₹{hidden:,}.")])
    out = agent.run_advisor("profit?", None, T.ToolContext(), client=fake)
    assert not out["grounding"]["verified"]


def test_grounding_checks_sign_and_small_rates():
    sources = [{"monthly_profit": 45000, "interest_rate_pct": 8.5}]
    assert not agent.check_grounding("You will make a loss of -₹45,000.", sources)["verified"]
    assert agent.check_grounding("Interest is 8.5% per year.", sources)["verified"]
    assert agent.check_grounding("Interest is 7.25% per year.", sources)["unverified_numbers"] == ["7.25%"]
    assert agent.check_grounding("Follow these 3 steps.", sources)["verified"]


def test_grounding_treats_dash_between_numbers_as_range():
    sources = [{"margin": "8 – 12%"}, {"margin2": "8-12%"}]
    assert not agent.check_grounding("Margin is -12%.", sources)["verified"]
    assert agent.check_grounding("Margin is 8 – 12%.", sources)["verified"]
