"""
Compatibility redirect: google_oauth has been moved to the dedicated 'api/' folder.
This module re-exports all members from api.google_oauth for seamless backward compatibility.
"""

import sys
import os

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_API_DIR = os.path.join(_BASE_DIR, "api")
if _BASE_DIR not in sys.path:
    sys.path.insert(0, _BASE_DIR)
if _API_DIR not in sys.path:
    sys.path.insert(0, _API_DIR)

from api.google_oauth import *
from api.google_oauth import google_bp, oauth, register_google
