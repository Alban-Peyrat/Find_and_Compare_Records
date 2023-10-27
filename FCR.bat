@echo off
cd %~dp0
where py >nul 2>nul
if %errorlevel% neq 0 (
    python main_gui.py
) else (
    py main_gui.py
)