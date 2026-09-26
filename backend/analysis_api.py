"""
Compatibility redirect: analysis_api has been moved to the dedicated 'api/' folder.
This module re-exports all members from api.analysis_api for seamless backward compatibility.
"""

import sys
import os

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_API_DIR = os.path.join(_BASE_DIR, "api")
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)
if _API_DIR not in sys.path:
    sys.path.insert(0, _API_DIR)

from api.analysis_api import *
from api.analysis_api import analysis_bp
