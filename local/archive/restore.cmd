@echo off
cd /d "%~dp0.."
set DOTNET_CLI_HOME=%CD%\.local\dotnet-home
set NUGET_PACKAGES=%CD%\.local\nuget
set MSBuildEnableWorkloadResolver=false
set DOTNET_CLI_WORKLOAD_UPDATE_NOTIFY_DISABLE=true
set DOTNET_CLI_TELEMETRY_OPTOUT=1
set DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1
set APPDATA=%CD%\.local\appdata
set NUGET_HTTP_CACHE_PATH=%CD%\.local\nuget-http
set NUGET_PLUGINS_CACHE_PATH=%CD%\.local\nuget-plugins
set TEMP=%CD%\.local\tmp
set TMP=%CD%\.local\tmp
dotnet restore Roblox\Roblox.Website\Roblox.Website.csproj --disable-parallel --verbosity diagnostic -m:1 /nr:false > .local\restore.log 2>&1
