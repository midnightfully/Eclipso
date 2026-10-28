@echo off
cd /d "%~dp0.."
set npm_config_cache=%CD%\.local\npm-cache
set NEXT_TELEMETRY_DISABLED=1
cd 2016-roblox-main
set npm_config_fetch_retries=1
set npm_config_maxsockets=5
call npm install --package-lock=false --omit=dev --ignore-scripts --legacy-peer-deps --no-audit --no-fund > ..\.local\frontend-install.log 2>&1
exit /b %ERRORLEVEL%
