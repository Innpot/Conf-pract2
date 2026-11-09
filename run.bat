@echo off
setlocal
pushd "%~dp0"
if not defined PYTHON set "PYTHON=python"
"%PYTHON%" -m src.main %*
set "result=%errorlevel%"
popd
exit /b %result%
