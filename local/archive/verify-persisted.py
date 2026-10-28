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
saved=json.loads((ROOT/'.local/test-accounts.json').read_text())
c=Client();c.call('/local/login','POST',{'username':saved['buyer'],'password':saved['password']})
s=c.call('/local/state');assert s['balance']['robux']==9475,s['balance'];assert {900001,900002,900003}.issubset({i['asset_id'] for i in s['inventory']});print('PASS full restart preserves account, 9475 test robux, and three inventory items',flush=True)
