@echo off
cd /d "%~dp0.."
set PG_RESTRICT_EXEC=1
.local\runtime\postgres\pgsql\bin\initdb.exe -D .local\pgdata-ready -U postgres --encoding=UTF8 --locale=C -A scram-sha-256 --pwfile=.local\pg-password.txt > .local\initdb.log 2>&1
