@echo off
cd /d "%~dp0"
call venv\Scripts\activate
start pythonw gui.py