@echo off
setlocal
cd /d "%~dp0.."
call "%~dp0_human-python.cmd"
if errorlevel 1 exit /b 1
"%HUMAN_PYTHON%" -m service.pose_pairs %*
exit /b %ERRORLEVEL%
