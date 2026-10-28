import pathlib,runpy,json,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parent.parent
ctx=runpy.run_path(str(ROOT/'local/inspect-db.py'));sql=ctx['sql']
Client=runpy.run_path(str(ROOT/'local/http-client.py'))['Client'];c=Client()
assert sql('SELECT count(*) FROM user_permission')=='0','Temporary test permissions remain'
cfgpath=ROOT/'Roblox/Roblox.Website/appsettings.json';before=cfgpath.read_bytes();assert json.loads(before)['OwnerUserId']=='0'
accounts=json.loads((ROOT/'.local/test-accounts.json').read_text())
for name,ok in [(accounts['buyer'],True),('Roblox',False)]:
 result=subprocess.run([sys.executable,str(ROOT/'local/set-owner.py'),name,'--check-only'],capture_output=True,text=True,timeout=30)
 assert (result.returncode==0)==ok,result.stdout+result.stderr
assert cfgpath.read_bytes()==before
old=sql('SELECT count(*) FROM "user"');seed=c.call('/local/seed','POST',{});assert seed['seller']==1 and old==sql('SELECT count(*) FROM "user"')
profile=c.call('/apisite/users/v1/users/1');fixture=json.loads((ROOT/'docs/roblox-profile.json').read_text());assert profile['name']=='Roblox' and profile['description']==fixture['description']
with c.http.open('http://127.0.0.1:5080/local',timeout=20) as r:assert r.status==200 and b'Website pages' in r.read()
assert not c.call('/local/state')['loggedIn']
print('PASS: system profile, seed idempotency, dashboard navigation, no retained test privileges, owner-selector validation')
(ROOT/'local/update-verification.json').write_text(json.dumps({'result':'PASS','checks':['exact system profile','seed preserves user 1 without new accounts','dashboard navigation delivered','temporary staff permissions removed','personal owner validation','system account rejected as owner','configuration unchanged by check-only']},indent=2))
