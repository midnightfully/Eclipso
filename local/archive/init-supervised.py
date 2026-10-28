import subprocess,pathlib,time,os
r=pathlib.Path(__file__).resolve().parent.parent
os.chdir(r)
f=open(r/'.local/init-supervised.log','w')
proc=subprocess.Popen([str(r/'.local/runtime/postgres/pgsql/bin/initdb.exe'),'-D',str(r/'.local/pgdata4'),'-U','postgres','--encoding=UTF8','--locale=C','-A','scram-sha-256','--pwfile='+str(r/'.local/pg-password.txt'),'--no-sync'],stdout=f,stderr=f,creationflags=subprocess.CREATE_NO_WINDOW)
print('Init PID',proc.pid,flush=True)
for _ in range(6):
 time.sleep(5)
 print('Status',proc.poll(),flush=True)
 exec(pathlib.Path("C:/Users/gauth/Documents/Codex/2026-10-27/you-are-toker-you-re-toker/work/process-list.py").read_text())
 if proc.poll() is not None:break
proc.wait()
