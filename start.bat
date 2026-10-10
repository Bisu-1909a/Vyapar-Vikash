@echo off
title Vyapaar Vikash MSME Platform
echo ========================================================
echo   Starting Vyapaar Vikash Server...
echo   Open in Browser: http://localhost:5000/pages/analyse.html
echo ========================================================
start "" "http://localhost:5000/pages/analyse.html"
python run.py
pause
