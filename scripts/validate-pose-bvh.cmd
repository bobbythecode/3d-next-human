@echo off
setlocal
cd /d "%~dp0.."
call "%~dp0_human-python.cmd"
if errorlevel 1 exit /b 1
if "%~1"=="" (
  echo Usage: scripts\validate-pose-bvh.cmd path\to\pose.bvh 1>&2
  exit /b 1
)
"%HUMAN_PYTHON%" scripts\validate_pose_bvh.py %*
exit /b %ERRORLEVEL%
