@echo off
cd /d "%~dp0"
python synthesizer.py
start dashboard.html
