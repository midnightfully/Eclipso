import pathlib,subprocess,os
exec(open('local/servers.py').read().split("if len(sys.argv)>1 and sys.argv[1]=='db':")[0])
p=subprocess.run([str(PG/'psql.exe'),'-h','127.0.0.1','-p','15432','-U','postgres','-d','bubbabloxlocal','-c',"SELECT count(*) FROM information_schema.tables WHERE table_schema='public'"],env=ENV,capture_output=True,timeout=20)
print(p.returncode,repr(p.stdout),repr(p.stderr))
