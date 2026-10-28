"""Local website supervisor. All listeners bind only to 127.0.0.1."""
import pathlib,subprocess,os,json,socket,time,sys,urllib.request
ROOT=pathlib.Path(__file__).resolve().parent.parent
STATE=ROOT/'.local'; PG=STATE/'runtime/postgres/pgsql/bin'
GARNET=STATE/'runtime/garnet/net10.0/GarnetServer.exe'
FLAGS=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
os.chdir(ROOT)
ENV=os.environ.copy()
ENV.update(DOTNET_CLI_HOME=str(STATE/'dotnet-home'),NUGET_PACKAGES=str(STATE/'nuget'),TEMP=str(STATE/'tmp'),TMP=str(STATE/'tmp'),NEXT_TELEMETRY_DISABLED='1',NEXT_IGNORE_INCORRECT_LOCKFILE='1',ASPNETCORE_ENVIRONMENT='Development',PGGSSENCMODE='disable',PGSSLMODE='disable',PGCONNECT_TIMEOUT='5')
config=json.loads((ROOT/'Roblox/Roblox.Website/appsettings.json').read_text())
ENV['PGPASSWORD']=next(x[9:] for x in config['Postgres'].split(';') if x.startswith('Password='))
children={};logs=[]
def status(state,message):
 data={'state':state,'message':message,'updated':time.time(),'pid':os.getpid()}
 tmp=STATE/'status.tmp';tmp.write_text(json.dumps(data));tmp.replace(STATE/'status.json')
def alive(port):
 try:
  with socket.create_connection(('127.0.0.1',port),1):return True
 except OSError:return False
def ready():
 try:
  req=urllib.request.Request('http://127.0.0.1:5080/local/state',headers={'User-Agent':'BubbabloxLocalLauncher/1.0'})
  with urllib.request.urlopen(req,timeout=2) as r:return r.status==200 and 'loggedIn' in json.load(r)
 except Exception:return False
def background(name,args,cwd):
 log=open(STATE/(name+'.log'),'ab',buffering=0);logs.append(log)
 children[name]=subprocess.Popen([str(a) for a in args],cwd=cwd,env=ENV,stdout=log,stderr=log,stdin=subprocess.DEVNULL,creationflags=FLAGS)
def wait_for(test,message,seconds=240):
 for _ in range(seconds):
  status('starting',message)
  if (STATE/'stop.request').exists():raise InterruptedError('Startup cancelled')
  for name,p in children.items():
   if p.poll() is not None:raise RuntimeError(name+' exited; see .local/'+name+'.log')
  if test():return
  time.sleep(1)
 raise RuntimeError(message+' timed out; see .local logs')
def pg_ready():
 p=subprocess.run([str(PG/'pg_isready.exe'),'-h','127.0.0.1','-p','15432','-U','postgres','-d','postgres','-q','-t','1'],env=ENV,creationflags=FLAGS,capture_output=True)
 return p.returncode==0
def shutdown():
 for name in ['website','frontend','cache']:
  p=children.get(name)
  if p and p.poll() is None:p.terminate();p.wait(timeout=15)
 p=children.get('postgres')
 if p and p.poll() is None:
  result=subprocess.run([str(PG/'pg_ctl.exe'),'-D',str(STATE/'pgdata-ready'),'-m','fast','-w','-t','90','stop'],env=ENV,creationflags=FLAGS,capture_output=True,timeout=100)
  if result.returncode:raise RuntimeError('Database shutdown failed: '+result.stderr.decode(errors='replace'))
  p.wait(timeout=15)
 for f in logs:f.close()
if '--hold' in sys.argv:
 # Hold an OS file lock for the lifetime of the supervisor, including startup.
 # The file may remain after a crash; the OS releases its lock automatically.
 supervisor_lock=open(STATE/'supervisor.lock','a+b')
 supervisor_lock.seek(0,2)
 if supervisor_lock.tell()==0:supervisor_lock.write(b'0');supervisor_lock.flush()
 supervisor_lock.seek(0)
 try:
  if os.name=='nt':
   import msvcrt
   msvcrt.locking(supervisor_lock.fileno(),msvcrt.LK_NBLCK,1)
  else:
   import fcntl
   fcntl.flock(supervisor_lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
 except (OSError,BlockingIOError):
  print('The local website supervisor is already running or starting.',flush=True)
  raise SystemExit(0)
 if ready():print('Already running: http://127.0.0.1:5080/local',flush=True);raise SystemExit(0)
 (STATE/'stop.request').unlink(missing_ok=True)
 try:
  for port in [15432,16379,3000,5080]:
   if alive(port):raise RuntimeError('Port '+str(port)+' is already in use. Stop the existing local services first.')
  background('postgres',[PG/'postgres.exe','-D',STATE/'pgdata-ready','-h','127.0.0.1','-p','15432','-c','max_connections=100','-c','shared_buffers=64MB'],ROOT)
  background('cache',[GARNET,'--bind','127.0.0.1','--port','16379','--memory','64m','--index','8m','--lua','--lua-transaction-mode'],ROOT)
  wait_for(pg_ready,'Waiting for PostgreSQL')
  wait_for(lambda:alive(16379),'Waiting for cache')
  background('frontend',['C:/Program Files/nodejs/node.exe',ROOT/'2016-roblox-main/node_modules/next/dist/bin/next','dev','-H','127.0.0.1','-p','3000'],ROOT/'2016-roblox-main')
  background('website',['C:/Program Files/dotnet/dotnet.exe',ROOT/'Roblox/Roblox.Website/bin/Debug/net10.0/Roblox.Website.dll'],ROOT/'Roblox/Roblox.Website')
  wait_for(ready,'Waiting for website')
  print('Ready: http://127.0.0.1:5080/local',flush=True)
  while not (STATE/'stop.request').exists():
   status('running','Ready: http://127.0.0.1:5080/local')
   for name,p in children.items():
    if p.poll() is not None:raise RuntimeError(name+' stopped unexpectedly')
   time.sleep(1)
  status('stopping','Saving and stopping local services')
  shutdown();status('stopped','All local services stopped')
 except Exception as e:
  try:shutdown()
  except Exception as cleanup:print(str(cleanup),flush=True)
  status('error',str(e));print(str(e),flush=True);raise SystemExit(1)
elif 'stop' in sys.argv:
 (STATE/'stop.request').write_text('stop')
 print('Stopping local services...',flush=True)
 for _ in range(120):
  try:s=json.loads((STATE/'status.json').read_text())
  except Exception:s={}
  if s.get('state') in ['stopped','error'] or (not alive(5080) and not alive(15432)):
   print(s.get('message','Stopped'),flush=True);break
  time.sleep(1)
 else:raise SystemExit('Stop timed out; see .local/status.json')
else:
 if ready():print('Ready: http://127.0.0.1:5080/local',flush=True);raise SystemExit(0)
 try:s=json.loads((STATE/'status.json').read_text());recent=time.time()-s['updated']<15 and s['state']=='starting'
 except Exception:recent=False
 launched=time.time()
 if not recent:
  log=open(STATE/'supervisor.log','ab',buffering=0)
  subprocess.Popen([sys.executable,__file__,'--hold'],cwd=ROOT,env=ENV,stdout=log,stderr=log,stdin=subprocess.DEVNULL,creationflags=FLAGS)
 print('Starting the website. The first startup may take a few minutes...',flush=True)
 for _ in range(600):
  if ready():print('Ready: open http://127.0.0.1:5080/local in Opera GX',flush=True);break
  try:s=json.loads((STATE/'status.json').read_text())
  except Exception:s={}
  # Ignore an error left over from a previous run; only report errors written after this launch.
  if s.get('state')=='error' and s.get('updated',0)>=launched-1:raise SystemExit(s['message'])
  time.sleep(1)
 else:raise SystemExit('Startup timed out. See .local/status.json and .local logs.')
