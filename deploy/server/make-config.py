#!/usr/bin/env python3
"""Render /etc/eclipso/appsettings.json on the server (run as root).

Starts from the release's appsettings.example.json (no secrets), generates every secret randomly ONCE into
/etc/eclipso/secrets.json (root:eclipso 640; never copied off the server), and applies the production settings.
Usage: make-config.py --release DIR --site https://staging.eclipso.lol [--owner-user-id N]
"""
import argparse, json, os, secrets, pathlib, grp

ap = argparse.ArgumentParser()
ap.add_argument('--release', required=True)
ap.add_argument('--site', required=True)
ap.add_argument('--owner-user-id', type=int, default=None)
a = ap.parse_args()
ETC = pathlib.Path('/etc/eclipso'); REL = pathlib.Path(a.release)
gid = grp.getgrnam('eclipso').gr_gid

def write_private(path, text):
    tmp = path.with_suffix('.tmp'); tmp.write_text(text); os.chown(tmp, 0, gid); os.chmod(tmp, 0o640); os.replace(tmp, path)

sec_path = ETC / 'secrets.json'
sec = json.loads(sec_path.read_text()) if sec_path.exists() else {}
for k in ['JwtSessions', 'Authorization', 'IPSalt', 'GameServerAuthorization', 'RenderAuthorization', 'BotAuthorization',
          'RccAuthorization', 'AssetValidationAuthorization', 'DiscordKey', 'BubbamonsApiKey', 'UserAgentBypass', 'Verification']:
    sec.setdefault(k, secrets.token_urlsafe(48))
write_private(sec_path, json.dumps(sec, indent=2))

prev = {}
cfg_path = ETC / 'appsettings.json'
if cfg_path.exists():
    prev = json.loads(cfg_path.read_text())
c = json.loads((REL / 'website' / 'appsettings.example.json').read_text())
site = a.site.rstrip('/')
host = site.split('://', 1)[1]
dbpw = (ETC / 'db-password').read_text().strip()
cur = '/opt/eclipso/current'
c.update({
    'Urls': 'http://127.0.0.1:5080',
    'AllowedHosts': f'{host};127.0.0.1;localhost',
    'BaseUrl': site, 'AssetUrl': site, 'CdnBaseUrl': '',
    'Postgres': f'Host=127.0.0.1;Port=5432;Database=eclipso;Username=eclipso;Password={dbpw};Maximum Pool Size=40',
    'Redis': '127.0.0.1:6379,abortConnect=false',
    'Authorization': sec['Authorization'], 'IPSalt': sec['IPSalt'], 'IPHubApiKey': '',
    'GameServerAuthorization': sec['GameServerAuthorization'], 'BotAuthorization': sec['BotAuthorization'],
    'RccAuthorization': sec['RccAuthorization'], 'DiscordKey': sec['DiscordKey'], 'BubbamonsApiKey': sec['BubbamonsApiKey'],
    'DiscordClientID': '', 'DiscordClientSecret': '', 'Webhook': '', 'SignupWebhook': '',
    'LocalDevelopment': False,
    'Development': {'EnableLocalTestEndpoints': False},
    'Security': {'AllowUntrustedContentProcessing': False, 'ExternalIpLookup': False, 'SecureCookies': True,
                 'TrustedProxyClientIpHeader': 'X-Eclipso-Client-IP'},
    'Features': {'RequireSignupApproval': False, 'DailyStipend': False},
    'Secrets': {'UserAgentBypass': sec['UserAgentBypass'], 'Verification': sec['Verification']},
    'OwnerUserId': str(a.owner_user_id if a.owner_user_id is not None else prev.get('OwnerUserId', '0')),
    'PackageShirtAssetId': -1, 'PackagePantsAssetId': -1, 'PackageLeftArmAssetId': -1, 'PackageRightArmAssetId': -1,
    'PackageLeftLegAssetId': -1, 'PackageRightLegAssetId': -1, 'PackageTorsoAssetId': -1,
    'SignupAssetIdsMan': [], 'SignupAssetIdsFemale': [], 'SignupAvatarAssetIdsMan': [], 'SignupAvatarAssetIdsFemale': [],
    'GSIPAddress': '127.0.0.1',
    'Logging': {'LogLevel': {'Default': 'Warning', 'Microsoft.AspNetCore': 'Warning'}},
})
c.setdefault('Jwt', {})['Sessions'] = sec['JwtSessions']
c.setdefault('Render', {}).update({'BaseUrl': 'ws://127.0.0.1:9', 'Authorization': sec['RenderAuthorization']})
c.setdefault('AssetValidation', {}).update({'BaseUrl': 'http://127.0.0.1:9', 'Authorization': sec['AssetValidationAuthorization']})
c.setdefault('GameServer', {})['AllowedNetworkPorts'] = []
c['Directories'] = {
    'Storage': '/var/lib/eclipso/storage/', 'Asset': '/var/lib/eclipso/storage/asset/',
    'Public': f'{cur}/public/', 'Thumbnails': '/var/lib/eclipso/thumbnails/', 'GroupIcons': '/var/lib/eclipso/groups/',
    'XmlTemplates': f'{cur}/libraries/Templates/', 'JsonData': f'{cur}/libraries/Json/', 'AdminBundle': f'{cur}/admin/',
    'EconomyChatBundle': '/var/lib/eclipso/chat/', 'LuaScripts': f'{cur}/libraries/internalscripts/',
    'RccServicePath': '/nonexistent/', 'RccService2015Path': '/nonexistent/', 'RccService2017Path': '/nonexistent/',
    'RccService2018Path': '/nonexistent/', 'RccService2020Path': '/nonexistent/',
}
c.pop('InfluxDB', None)
write_private(cfg_path, json.dumps(c, indent=2))
write_private(ETC / 'game-servers.json', json.dumps({'GameServers': []}, indent=2))

front = {'serverRuntimeConfig': {'backend': {'csrfKey': ''}},
         'publicRuntimeConfig': json.loads((REL / 'frontend' / 'config.example.json').read_text())['publicRuntimeConfig']}
front['publicRuntimeConfig']['backend'].update({'baseUrl': site + '/', 'apiFormat': site + '/apisite/{0}{1}'})
(REL / 'frontend' / 'config.json').write_text(json.dumps(front, indent=2))
print('make-config: OK (owner user id = %s)' % c['OwnerUserId'])
