from analysis_engine import run_full_analysis
from database import models as db


def test_reference_data_seeded(app):
    assert len(db.get_all_states()) == 36
    assert len(db.get_all_schemes()) == 9
    assert db.get_sector_benchmark("grocery")["avg_margin_pct"] == 10.0
    assert any(d["name"] == "Cuttack" for d in db.get_districts_by_state("odisha"))


def test_analysis_roundtrip_keeps_engine_numbers(app):
    form = {"business_type": "dairy", "state": "Odisha", "district": "Puri", "total_investment": 400000.0,
            "area_type": "rural", "business_name": "Test Dairy"}
    result = run_full_analysis(form)
    saved = db.save_complete_analysis(form, result)
    rec = db.get_analysis_record(saved["analysis_id"])
    assert rec["certificate_no"] == saved["certificate_no"]
    assert rec["feasibility_score"] == saved["feasibility_score"]
    assert rec["financial"]["monthly_profit"] == result["financial"]["monthly_profit"]
    assert rec["market"] == result["market"]
    assert db.get_certified_report_by_certificate_no(saved["certificate_no"])["analysis_id"] == saved["analysis_id"]


def test_delete_respects_ownership(app):
    owner = db.create_user("Owner", "owner-del@example.com", "hash")
    other = db.create_user("Other", "other-del@example.com", "hash")
    form = {"business_type": "grocery", "state": "Odisha", "district": "Cuttack", "total_investment": 200000.0}
    aid = db.save_complete_analysis(form, run_full_analysis(form), user_id=owner)["analysis_id"]
    assert db.delete_analysis(aid, user_id=other) is False
    assert db.delete_analysis(aid, user_id=owner) is True
    assert db.get_analysis_record(aid) is None


def test_user_lookup_and_password_never_exposed(app):
    uid = db.create_user("Asha", "Asha@Example.com", "bcrypt-hash")
    u = db.get_user_by_email("  asha@example.com ")
    assert u["id"] == uid and u["password"] == "bcrypt-hash"
    assert "password" not in db.row_to_dict(u)
    g = db.upsert_google_user("g-123", "asha@example.com", "Asha", "http://a/img.png")
    assert g["id"] == uid and g["google_id"] == "g-123"


def test_search_treats_wildcards_literally(app):
    assert db.search_geo_locations("%") == []
    assert db.search_geo_locations("cutt")[0]["district"] == "Cuttack"
