import pathlib,json,subprocess,os
ROOT=pathlib.Path(__file__).resolve().parent.parent
cfg=json.loads((ROOT/'Roblox/Roblox.Website/appsettings.json').read_text())
env=os.environ.copy();env.update(PGPASSWORD=next(v[9:] for v in cfg['Postgres'].split(';') if v.startswith('Password=')),PGGSSENCMODE='disable',PGSSLMODE='disable',PGCONNECT_TIMEOUT='5')
PG=ROOT/'.local/runtime/postgres/pgsql/bin'
def sql(query):
 p=subprocess.run([str(PG/'psql.exe'),'-h','127.0.0.1','-p','15432','-U','postgres','-d','bubbabloxlocal','-X','-A','-t','-v','ON_ERROR_STOP=1','-c',query],env=env,capture_output=True,text=True,timeout=30)
 if p.returncode:raise RuntimeError(p.stderr)
 return p.stdout.strip()
if __name__=='__main__':
 print(sql('SELECT json_agg(t) FROM (SELECT id,username,description FROM "user" ORDER BY id LIMIT 15) t'))
