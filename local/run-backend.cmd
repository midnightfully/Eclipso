@echo off
cd /d "%~dp0..\Roblox\Roblox.Website"
set DOTNET_CLI_HOME=%CD%\..\..\.local\dotnet-home
set ASPNETCORE_ENVIRONMENT=Development
dotnet bin\Debug\net10.0\Roblox.Website.dll > ..\..\.local\website.log 2>&1
