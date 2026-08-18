@echo off
if defined HUMAN_PYTHON exit /b 0
if /I "%CONDA_DEFAULT_ENV%"=="human" if exist "%CONDA_PREFIX%\python.exe" (
  set "HUMAN_PYTHON=%CONDA_PREFIX%\python.exe"
  exit /b 0
)
if exist "%USERPROFILE%\miniconda3\envs\human\python.exe" (
  set "HUMAN_PYTHON=%USERPROFILE%\miniconda3\envs\human\python.exe"
  exit /b 0
)
if exist "%USERPROFILE%\anaconda3\envs\human\python.exe" (
  set "HUMAN_PYTHON=%USERPROFILE%\anaconda3\envs\human\python.exe"
  exit /b 0
)
where python >nul 2>&1
if errorlevel 1 (
  echo HUMAN_PYTHON not set and conda env human was not found. 1>&2
  exit /b 1
)
set "HUMAN_PYTHON=python"
exit /b 0
