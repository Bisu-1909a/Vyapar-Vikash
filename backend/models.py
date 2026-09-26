"""
Compatibility redirect: models has been moved to the dedicated 'database/' folder.
This module re-exports all members from database.models for seamless backward compatibility.
"""

import sys
import os

# Ensure project root and database directories are in sys.path
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DB_DIR = os.path.join(_BASE_DIR, "database")
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)
if _DB_DIR not in sys.path:
    sys.path.insert(0, _DB_DIR)

from database.models import *
from database.models import (
    DATABASE_PATH,
    get_db,
    init_db,
    SCHEMA,
    create_user,
    get_user_by_email,
    get_user_by_id,
    verify_user_password,
    upsert_google_user,
    update_last_login,
    save_complete_analysis,
    get_analysis_record,
    get_all_analyses,
    delete_analysis,
    save_certified_report,
    get_certified_report_by_certificate_no,
    get_all_schemes,
    get_platform_stats,
    get_all_states,
    get_districts_by_state,
    get_sub_areas,
    search_geo_locations,
    get_micro_geo_intelligence,
    save_location_analysis,
    get_location_analysis_by_id,
    get_all_location_analyses,
    delete_location_analysis,
    save_business_plan,
    get_business_plans,
    get_business_plan_by_id,
    delete_business_plan,
    save_location,
    get_saved_locations,
    delete_saved_location,
    save_opportunity,
    get_saved_opportunities,
    delete_saved_opportunity,
    save_scenario_run,
    get_scenario_runs,
    row_to_dict
)
