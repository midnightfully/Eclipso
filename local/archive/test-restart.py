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
s=c.call('/local/state');assert any(i['asset_id']==900001 for i in s['inventory']);assert any(i['asset_id']==900003 for i in s['inventory']);assert s['balance']['robux']==9575,s['balance'];print('PASS persisted account, balance, and inventory after backend restart',flush=True)
a=next(x for x in s['catalog'] if x['id']==900002)
c.call('/apisite/economy/v1/purchases/products/900002','POST',{'expectedCurrency':1,'expectedPrice':100,'expectedSellerId':a['creator_id']})
s=c.call('/local/state');copy=next(x for x in s['inventory'] if x['asset_id']==900002);assert copy['serial']==1,copy;assert s['balance']['robux']==9475,s['balance'];print('PASS limited-unique purchase assigns serial 1 and deducts 100',flush=True)
