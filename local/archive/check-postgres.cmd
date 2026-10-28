@echo off
"C:/Users/gauth/Documents/Codex/2026-10-27/you-are-toker-you-re-toker/outputs/bubbablox-local/.local/runtime/postgres/pgsql/bin/postgres.exe" --check -D .local/pgdata4 -c max_connections=100 -c shared_buffers=1000 -c dynamic_shared_memory_type=windows < "nul" > .local/pgcheck.log 2>&1
echo result=%ERRORLEVEL%
