@echo off
cd /d "%~dp0.."
set TEMP=%CD%\.local\tmp
set TMP=%CD%\.local\tmp
.local\runtime\postgres\pgsql\bin\initdb.exe -D .local\pgdata2 -U postgres --encoding=UTF8 --locale=C -A scram-sha-256 --pwfile=.local\pg-password.txt --debug --no-sync > .local\initdb-debug.log 2>&1
