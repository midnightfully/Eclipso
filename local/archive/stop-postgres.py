import pathlib,subprocess,os
exec(open('local/servers.py').read().split("if len(sys.argv)>1 and sys.argv[1]=='db':")[0])
ENV['PG_RESTRICT_EXEC']='1'
p=subprocess.run([str(PG/'pg_ctl.exe'),'-D',str(STATE/'pgdata-ready'),'-m','fast','-w','stop'],env=ENV,capture_output=True,timeout=25)
print(p.returncode,p.stdout.decode(),p.stderr.decode())
