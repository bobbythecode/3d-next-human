@echo off
setlocal

@REM activate human environment
@REM conda activate human
@REM end

cd /d "%~dp0.."
if not defined HUMAN_API_HOST set "HUMAN_API_HOST=127.0.0.1"
if not defined HUMAN_API_PORT set "HUMAN_API_PORT=8001"
call "%~dp0_human-python.cmd"
if errorlevel 1 exit /b 1
"%HUMAN_PYTHON%" -m service.http_api
