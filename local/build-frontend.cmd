@echo off
rem Production build of the Next.js frontend into 2016-roblox-main\.next-prod (served by Start Website.cmd).
rem Run after changing anything in 2016-roblox-main, then restart the website.
cd /d "%~dp0..\2016-roblox-main"
set NEXT_BUILD_DIR=.next-prod
set NEXT_TELEMETRY_DISABLED=1
"C:\Program Files\nodejs\node.exe" node_modules\next\dist\bin\next build > ..\.local\frontend-prod-build.log 2>&1
if errorlevel 1 (echo Frontend build FAILED - see .local\frontend-prod-build.log & exit /b 1)
echo Frontend build complete.
