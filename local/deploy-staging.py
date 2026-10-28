"""Build, package and deploy the current commit to staging.eclipso.lol (Hostinger VPS).

Usage:  python local/deploy-staging.py            build + upload + activate
        python local/deploy-staging.py --provision also run the one-time server setup first
Requires: SSH key unlocked in Windows ssh-agent (ssh-add), user kindmops with sudo on the VPS.
Never packages private config (appsettings.json, game-servers.json), native .exe tools or user uploads.
"""
import pathlib, subprocess, sys, tarfile, shutil, os, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
HOST = 'kindmops@2.24.48.245'
SITE = 'https://staging.eclipso.lol'
SSH = [r'C:\Windows\System32\OpenSSH\ssh.exe', '-o', 'BatchMode=yes', HOST]
DOTNET = r'C:\Program Files\dotnet\dotnet.exe'

def run(cmd, **kw):
    print('>', cmd if isinstance(cmd, str) else ' '.join(map(str, cmd))[:160], flush=True)
    subprocess.run(cmd, check=True, **kw)

rev = subprocess.run(['git', 'rev-parse', '--short=8', 'HEAD'], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
dirty = subprocess.run(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=ROOT, capture_output=True, text=True).stdout.strip()
if dirty:
    sys.exit('Commit your changes first; a deployed release must match a commit.\n' + dirty)
release = f'{time.strftime("%Y%m%d-%H%M%S")}-{rev}'
print('release', release)

# 1. Build
env = dict(os.environ, DOTNET_CLI_HOME=str(ROOT / '.local/dotnet-home'), NUGET_PACKAGES=str(ROOT / '.local/nuget'), DOTNET_CLI_TELEMETRY_OPTOUT='1')
pub = ROOT / '.local/publish/website'
shutil.rmtree(pub, ignore_errors=True)
run([DOTNET, 'publish', str(ROOT / 'Roblox/Roblox.Website/Roblox.Website.csproj'), '-c', 'Release', '-o', str(pub), '--nologo', '-p:UseSharedCompilation=false'], env=env, stdout=subprocess.DEVNULL)
run(['cmd', '/c', str(ROOT / 'local/build-frontend.cmd')])

# 2. Assemble the package
stage = ROOT / '.local/release' / release
shutil.rmtree(stage, ignore_errors=True)
def copy(src, dst, ignore=None):
    shutil.copytree(src, stage / dst, ignore=ignore, dirs_exist_ok=True)
copy(pub, 'website', shutil.ignore_patterns('appsettings.json', 'game-servers.json', 'package-lock.json', '*.pdb', '*.exe'))
fe = ROOT / '2016-roblox-main'
copy(fe / '.next-prod', 'frontend/.next-prod', shutil.ignore_patterns('cache'))
copy(fe / 'public', 'frontend/public')
for f in ['package.json', 'package-lock.json', 'next.config.js', 'config.example.json']:
    shutil.copy2(fe / f, stage / 'frontend' / f)
copy(ROOT / 'api/public', 'public', shutil.ignore_patterns('*.exe', 'rbxmk', 'groups', 'thumbnails', 'Thumbs.db'))
copy(ROOT / 'Roblox/Roblox.Libraries/Templates', 'libraries/Templates')
copy(ROOT / 'Roblox/Roblox.Libraries/Json', 'libraries/Json')
copy(ROOT / 'Roblox/Roblox.Services/Games/internalscripts', 'libraries/internalscripts')
copy(ROOT / 'admin/public', 'admin', shutil.ignore_patterns('Thumbs.db'))
(stage / 'sql').mkdir(parents=True, exist_ok=True)
shutil.copy2(ROOT / 'api/sql/schema.sql', stage / 'sql/schema.sql')
copy(ROOT / 'api/sql/migrations', 'sql/migrations')
copy(ROOT / 'deploy/server', 'deploy')
(stage / 'REVISION').write_text(rev + '\n')
for bad in ['appsettings.json', 'game-servers.json', 'secrets.json']:
    assert not list(stage.rglob(bad)), 'private file in package: ' + bad
assert not list(stage.rglob('*.exe')), 'native executable in package'

tgz = ROOT / '.local/release' / (release + '.tgz')
with tarfile.open(tgz, 'w:gz') as t:
    t.add(stage, arcname=release)
print('package', tgz.name, round(tgz.stat().st_size / 1e6, 1), 'MB')

# 3. Upload and activate
with open(tgz, 'rb') as f:
    run(SSH + [f'cat > /tmp/{release}.tgz'], stdin=f)
remote = f'''set -e
sudo tar -xzf /tmp/{release}.tgz -C /opt/eclipso/releases && rm /tmp/{release}.tgz
R=/opt/eclipso/releases/{release}
{"sudo bash $R/deploy/provision.sh" if "--provision" in sys.argv else "true"}
sudo bash $R/deploy/activate-release.sh $R {SITE}
ls -1dt /opt/eclipso/releases/*/ | tail -n +6 | xargs -r sudo rm -rf   # keep the 5 newest releases for rollback
'''
run(SSH + ['bash -s'], input=remote.encode())
print('DEPLOYED', release, 'to', SITE)
