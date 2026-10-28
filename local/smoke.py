import urllib.request,urllib.error,http.cookiejar,json,pathlib,time
ROOT=pathlib.Path(__file__).resolve().parent.parent
BASE='http://127.0.0.1:5080'
class Client:
 def __init__(self):
  self.cookies=http.cookiejar.CookieJar();self.http=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookies));self.token=''
 def call(self,path,method='GET',body=None):
  for attempt in range(2):
   req=urllib.request.Request(BASE+path,data=json.dumps(body).encode() if body is not None else None,method=method,headers={'User-Agent':'BubbabloxLocalTest/1.0','Content-Type':'application/json','x-csrf-token':self.token,'Origin':BASE})
   try:
    with self.http.open(req,timeout=30) as r:
     data=r.read().decode();return json.loads(data) if data else {}
   except urllib.error.HTTPError as e:
    if e.code==403 and e.headers.get('x-csrf-token') and attempt==0:self.token=e.headers['x-csrf-token'];continue
    raise RuntimeError(str(e.code)+' '+e.read().decode()[:1500]) from e
c=Client()
for path,method,body in [('/local/state','GET',None),('/local/seed','POST',{})]:
 print(path,c.call(path,method,body),flush=True)
