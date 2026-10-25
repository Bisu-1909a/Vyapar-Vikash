"""
Compatibility redirect: models has been moved to the dedicated 'database/' folder.
This module re-exports all members from database.models for backward compatibility.
"""

import sys
import os

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)

from database.models import *  # noqa: F401,F403
