import runpy,pathlib,json,datetime,subprocess
ROOT=pathlib.Path(__file__).resolve().parent.parent
ctx=runpy.run_path(str(ROOT/'local/inspect-db.py'));sql=ctx['sql']
profile=json.loads((ROOT/'docs/roblox-profile.json').read_text())
current=json.loads(sql('SELECT row_to_json(t) FROM (SELECT id,username,description FROM "user" WHERE id=1) t'))
assert current['username'] in ['LocalCatalog','Roblox'], 'User 1 is unexpected; no changes made'
assert sql("SELECT count(*) FROM \"user\" WHERE lower(username)='roblox' AND id<>1")=='0'
backup=ROOT/'.local/backups';backup.mkdir(exist_ok=True)
filename=backup/('before-profile-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.dump')
subprocess.run([str(ctx['PG']/'pg_dump.exe'),'-h','127.0.0.1','-p','15432','-U','postgres','-d','bubbabloxlocal','-Fc','-f',str(filename)],env=ctx['env'],check=True,timeout=120)
quote=lambda s:"'"+s.replace("'","''")+"'"
sql('BEGIN; UPDATE "user" SET username='+quote(profile['username'])+',description='+quote(profile['description'])+' WHERE id=1; COMMIT;')
updated=json.loads(sql('SELECT row_to_json(t) FROM (SELECT id,username,description FROM "user" WHERE id=1) t'))
assert updated==profile
print('PASS: user 1 is Roblox with the exact requested biography. Database backup saved.')
