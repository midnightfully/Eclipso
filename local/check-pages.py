import urllib.request,urllib.error,json,pathlib,time
r=pathlib.Path(__file__).resolve().parent.parent
for path in ['/local','/home','/catalog']:
 try:
  t=time.time()
  req=urllib.request.Request('http://127.0.0.1:5080'+path,headers={'User-Agent':'BubbabloxLocalTest/1.0'})
  with urllib.request.urlopen(req,timeout=90) as res:
   html=res.read().decode();(r/'.local'/('page-'+path[1:]+'.html')).write_text(html,encoding='utf-8');print(path,res.status,len(html),round(time.time()-t,2),flush=True)
 except Exception as e: print(path,repr(e),flush=True)
