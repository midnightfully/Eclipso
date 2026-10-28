@echo off
cd /d "%~dp0..\2016-roblox-main"
set NEXT_TELEMETRY_DISABLED=1
set NEXT_IGNORE_INCORRECT_LOCKFILE=1
node node_modules\next\dist\bin\next dev -H 127.0.0.1 -p 3000 > ..\.local\frontend.log 2>&1
