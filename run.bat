@echo off
REM Script para rodar a aplicação com venv ativado
cd /d "%~dp0"
call .venv\Scripts\activate.bat
python mainWindow.py
pause
