"""
auth.py – Email/password registration, login, logout & session check routes.
All routes return JSON so the frontend can call them via fetch().
"""

import os
import sys

# Ensure project root, database, and backend directories are in sys.path
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_BASE_DIR = os.path.dirname(_THIS_DIR)
for _p in [_BASE_DIR, os.path.join(_BASE_DIR, "database"), os.path.join(_BASE_DIR, "backend")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from flask import Blueprint, request, session, jsonify
from flask_bcrypt import Bcrypt

try:
    from database.models import (
        get_user_by_email, create_user, get_user_by_id, row_to_dict,
        update_user_profile, update_last_login,
        save_location, get_saved_locations, delete_saved_location,
        save_opportunity, get_saved_opportunities, delete_saved_opportunity,
        save_business_plan, get_business_plans, get_business_plan_by_id, delete_business_plan,
        get_all_analyses
    )
except ImportError:
    from models import (
        get_user_by_email, create_user, get_user_by_id, row_to_dict,
        update_user_profile, update_last_login,
        save_location, get_saved_locations, delete_saved_location,
        save_opportunity, get_saved_opportunities, delete_saved_opportunity,
        save_business_plan, get_business_plans, get_business_plan_by_id, delete_business_plan,
        get_all_analyses
    )

auth_bp = Blueprint("auth", __name__)
bcrypt  = Bcrypt()   # initialised properly in app.py via bcrypt.init_app(app)


# ─────────────────────────────────────────────
#  POST /api/register
# ─────────────────────────────────────────────

@auth_bp.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    name     = (data.get("name")     or "").strip()
    email    = (data.get("email")    or "").strip().lower()
    password = (data.get("password") or "").strip()

    # ── Validation ──────────────────────────────
    if not name or not email or not password:
        return jsonify({"error": "Name, email and password are required."}), 400

    if "@" not in email or "." not in email.split("@")[-1]:
        return jsonify({"error": "Please enter a valid email address."}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    if get_user_by_email(email):
        return jsonify({"error": "An account with this email already exists. Please sign in."}), 409

    # ── Create account ───────────────────────────
    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    user_id = create_user(name=name, email=email, password_hash=pw_hash)

    # Auto-login after registration
    session["user_id"] = user_id
    session.permanent = True

    user = get_user_by_id(user_id)
    return jsonify({
        "message": "Account created successfully!",
        "user": row_to_dict(user)
    }), 201


# ─────────────────────────────────────────────
#  POST /api/login
# ─────────────────────────────────────────────

@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email    = (data.get("email")    or "").strip().lower()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    user = get_user_by_email(email)

    # User not found OR Google-only account (no password set)
    if not user or not user["password"]:
        return jsonify({"error": "Invalid email or password."}), 401

    if not bcrypt.check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid email or password."}), 401

    # ── Start session ────────────────────────────
    update_last_login(user["id"])
    session["user_id"] = user["id"]
    session.permanent  = True

    updated_user = get_user_by_id(user["id"])
    return jsonify({
        "message": "Login successful!",
        "user": row_to_dict(updated_user)
    }), 200


# ─────────────────────────────────────────────
#  GET /api/logout
# ─────────────────────────────────────────────

@auth_bp.route("/api/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully."}), 200


# ─────────────────────────────────────────────
#  GET /api/me  – return current user or 401
# ─────────────────────────────────────────────

@auth_bp.route("/api/me", methods=["GET"])
def me():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    user = get_user_by_id(user_id)
    if not user:
        session.clear()
        return jsonify({"error": "User not found."}), 401

    user_dict = row_to_dict(user)
    # Enrich with workspace counts
    saved_locs = get_saved_locations(user_id)
    saved_opps = get_saved_opportunities(user_id)
    plans = get_business_plans(user_id)
    analyses = get_all_analyses(user_id=user_id)

    user_dict["counts"] = {
        "saved_locations": len(saved_locs),
        "saved_opportunities": len(saved_opps),
        "business_plans": len(plans),
        "analyses": len(analyses)
    }

    return jsonify({"user": user_dict}), 200


# ─────────────────────────────────────────────
#  PUT /api/me  – update profile
# ─────────────────────────────────────────────

@auth_bp.route("/api/me", methods=["PUT"])
def update_profile():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    avatar_url = data.get("avatar_url")

    if not name:
        return jsonify({"error": "Name cannot be empty."}), 400

    updated = update_user_profile(user_id, name, avatar_url)
    return jsonify({"message": "Profile updated successfully.", "user": row_to_dict(updated)}), 200


# ─────────────────────────────────────────────
#  Saved Locations Endpoints
# ─────────────────────────────────────────────

@auth_bp.route("/api/user/saved_locations", methods=["GET"])
def list_saved_locations():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401
    return jsonify({"status": "success", "locations": get_saved_locations(user_id)}), 200


@auth_bp.route("/api/user/saved_locations", methods=["POST"])
def add_saved_location():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    lat = data.get("latitude")
    lng = data.get("longitude")

    if not name or lat is None or lng is None:
        return jsonify({"error": "Location name, latitude and longitude are required."}), 400

    loc_id = save_location(
        user_id=user_id,
        name=name,
        formatted_address=data.get("formatted_address"),
        latitude=float(lat),
        longitude=float(lng),
        radius_km=float(data.get("radius_km") or 3.0),
        place_id=data.get("place_id"),
        notes=data.get("notes")
    )
    return jsonify({"status": "success", "location_id": loc_id, "message": "Location saved successfully."}), 201


@auth_bp.route("/api/user/saved_locations/<int:loc_id>", methods=["DELETE"])
def remove_saved_location(loc_id: int):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    success = delete_saved_location(loc_id, user_id)
    if not success:
        return jsonify({"error": "Location not found or not owned by user."}), 404
    return jsonify({"status": "success", "message": "Saved location removed."}), 200


# ─────────────────────────────────────────────
#  Saved Opportunities Endpoints
# ─────────────────────────────────────────────

@auth_bp.route("/api/user/saved_opportunities", methods=["GET"])
def list_saved_opps():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401
    return jsonify({"status": "success", "opportunities": get_saved_opportunities(user_id)}), 200


@auth_bp.route("/api/user/saved_opportunities", methods=["POST"])
def add_saved_opp():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    data = request.get_json(silent=True) or {}
    cat_key = data.get("category_key")
    cat_name = data.get("category_name")
    loc_name = data.get("location_name")

    if not cat_key or not cat_name or not loc_name:
        return jsonify({"error": "Category key, category name, and location name are required."}), 400

    opp_id = save_opportunity(
        user_id=user_id,
        category_key=cat_key,
        category_name=cat_name,
        priority=int(data.get("priority") or 1),
        opportunity_score=float(data.get("opportunity_score") or 80.0),
        confidence_score=float(data.get("confidence_score") or 85.0),
        location_name=loc_name,
        latitude=float(data["latitude"]) if data.get("latitude") is not None else None,
        longitude=float(data["longitude"]) if data.get("longitude") is not None else None,
        radius_km=float(data.get("radius_km") or 3.0),
        reasons=data.get("reasons"),
        factors=data.get("factors"),
        analysis_id=data.get("analysis_id"),
        location_analysis_id=data.get("location_analysis_id")
    )
    return jsonify({"status": "success", "opportunity_id": opp_id, "message": "Opportunity saved to workspace."}), 201


@auth_bp.route("/api/user/saved_opportunities/<int:opp_id>", methods=["DELETE"])
def remove_saved_opp(opp_id: int):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    success = delete_saved_opportunity(opp_id, user_id)
    if not success:
        return jsonify({"error": "Opportunity not found or not owned by user."}), 404
    return jsonify({"status": "success", "message": "Saved opportunity removed."}), 200


# ─────────────────────────────────────────────
#  Business Plans Endpoints
# ─────────────────────────────────────────────

@auth_bp.route("/api/user/business_plans", methods=["GET"])
def list_user_plans():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401
    return jsonify({"status": "success", "plans": get_business_plans(user_id)}), 200


@auth_bp.route("/api/user/business_plans/<int:plan_id>", methods=["GET"])
def get_user_plan(plan_id: int):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    plan = get_business_plan_by_id(plan_id, user_id=user_id)
    if not plan:
        return jsonify({"error": "Business plan not found."}), 404
    return jsonify({"status": "success", "plan": plan}), 200


@auth_bp.route("/api/user/business_plans", methods=["POST"])
def save_user_plan():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    data = request.get_json(silent=True) or {}
    title = data.get("title") or "Business Opportunity Plan"
    cat_key = data.get("category_key") or "general"
    loc_name = data.get("location_name") or "Local Catchment"
    investment = float(data.get("investment") or 250000.0)

    plan_id = save_business_plan(
        user_id=user_id,
        title=title,
        category_key=cat_key,
        location_name=loc_name,
        investment=investment,
        executive_summary=data.get("executive_summary") or "",
        plan_data=data.get("plan_data") or {},
        roadmap=data.get("roadmap") or [],
        analysis_id=data.get("analysis_id"),
        plan_id=data.get("plan_id")
    )
    return jsonify({"status": "success", "plan_id": plan_id, "message": "Business plan saved successfully."}), 201


@auth_bp.route("/api/user/business_plans/<int:plan_id>", methods=["DELETE"])
def remove_user_plan(plan_id: int):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not authenticated."}), 401

    success = delete_business_plan(plan_id, user_id)
    if not success:
        return jsonify({"error": "Plan not found or not owned by user."}), 404
    return jsonify({"status": "success", "message": "Business plan removed."}), 200
