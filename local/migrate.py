"""Apply pending api/sql/migrations/*.sql to the local database, after taking a backup.
Usage: python local/migrate.py [--status]"""
import pathlib,subprocess,json,os,sys,time
ROOT=pathlib.Path(__file__).resolve().parent.parent
PG=ROOT/'.local/runtime/postgres/pgsql/bin'
cfg=json.loads((ROOT/'Roblox/Roblox.Website/appsettings.json').read_text())
parts=dict(p.split('=',1) for p in cfg['Postgres'].split(';') if '=' in p)
env=os.environ.copy();env.update(PGPASSWORD=parts['Password'],PGSSLMODE='disable',PGCONNECT_TIMEOUT='10')
base=['-h',parts['Host'],'-p',parts['Port'],'-U',parts['Username'],'-d',parts['Database']]
def psql(*args,check=True):
    p=subprocess.run([str(PG/'psql.exe'),*base,'-X','-q','-A','-t','-v','ON_ERROR_STOP=1',*args],env=env,capture_output=True,text=True)
    if check and p.returncode:raise SystemExit('psql failed: '+p.stderr.strip())
    return p.stdout.strip()
psql('-c','CREATE TABLE IF NOT EXISTS schema_migrations (version text PRIMARY KEY, applied_at timestamptz NOT NULL DEFAULT now())')
applied=set(psql('-c','SELECT version FROM schema_migrations').split())
files=sorted((ROOT/'api/sql/migrations').glob('[0-9][0-9][0-9][0-9]_*.sql'))
pending=[f for f in files if f.stem not in applied]
for f in files:print(('applied ' if f.stem in applied else 'PENDING ')+f.name)
if '--status' in sys.argv or not pending:raise SystemExit(0)
backup=ROOT/'.local/backups'/('before-migrate-'+time.strftime('%Y%m%d-%H%M%S')+'.dump')
backup.parent.mkdir(parents=True,exist_ok=True)
r=subprocess.run([str(PG/'pg_dump.exe'),*base,'-Fc','-f',str(backup)],env=env,capture_output=True,text=True)
if r.returncode:raise SystemExit('Backup failed, nothing applied: '+r.stderr)
print('backup',backup.name)
for f in pending:
    # Each migration and its bookkeeping row commit together or not at all.
    psql('-1','-f',str(f),'-c',"INSERT INTO schema_migrations(version) VALUES ('%s')"%f.stem)
    print('applied',f.name)
