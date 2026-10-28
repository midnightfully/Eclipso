@echo off
cd /d "%~dp0"
C:\Users\gauth\AppData\Local\Programs\Python\Python314\python.exe local\servers.py stop
if errorlevel 1 pause
