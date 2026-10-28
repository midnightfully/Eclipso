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
import secrets
results=[]
def test(name,fn):
 try:
  fn();results.append({'test':name,'result':'PASS'});print('PASS',name,flush=True)
 except Exception as e:
  results.append({'test':name,'result':'FAIL','error':str(e)});print('FAIL',name,str(e),flush=True);raise
 finally:(ROOT/'local/test-results.json').write_text(json.dumps(results,indent=2))
a=Client();b=Client();nonce=secrets.token_hex(3);pw=secrets.token_urlsafe(18)
namea='Buyer'+nonce;nameb='Seller'+nonce
(ROOT/'.local/test-accounts.json').write_text(json.dumps({'buyer':namea,'seller':nameb,'password':pw}))
test('Seed sample catalog',lambda:a.call('/local/seed','POST',{}))
test('Create buyer account',lambda:a.call('/local/signup','POST',{'username':namea,'password':pw}))
test('Create second account',lambda:b.call('/local/signup','POST',{'username':nameb,'password':pw}))
def balance_grant():
 old=a.call('/local/state')['balance']['robux'];a.call('/local/grant','POST',{});new=a.call('/local/state')['balance']['robux'];assert new-old==10000,(old,new)
test('Test-credit grant persists in database',balance_grant)
def purchase():
 old=a.call('/local/state');item=next(x for x in old['catalog'] if x['id']==900001)
 a.call('/apisite/economy/v1/purchases/products/900001','POST',{'expectedCurrency':1,'expectedPrice':25,'expectedSellerId':item['creator_id']})
 new=a.call('/local/state');assert old['balance']['robux']-new['balance']['robux']==25;assert any(x['asset_id']==900001 for x in new['inventory'])
test('Catalog purchase deducts balance and grants inventory',purchase)
def denied_duplicate():
 before=a.call('/local/state');item=next(x for x in before['catalog'] if x['id']==900001)
 try:a.call('/apisite/economy/v1/purchases/products/900001','POST',{'expectedCurrency':1,'expectedPrice':25,'expectedSellerId':item['creator_id']})
 except RuntimeError:pass
 else:raise AssertionError('Duplicate purchase unexpectedly succeeded')
 after=a.call('/local/state');assert before['balance']==after['balance'];assert len(before['inventory'])==len(after['inventory'])
test('Duplicate purchase rejected without spending',denied_duplicate)
def resale():
 b.call('/local/grant','POST',{});listing=b.call('/apisite/economy/v1/assets/900003/resellers')['data'][0]
 b.call('/apisite/economy/v1/purchases/products/900003','POST',{'expectedCurrency':1,'expectedPrice':listing['price'],'expectedSellerId':listing['seller']['id'],'userAssetId':listing['userAssetId']})
 b.call('/apisite/economy/v1/assets/900003/resellable-copies/'+str(listing['userAssetId']),'PATCH',{'price':500})
 before=a.call('/local/state');seller_before=b.call('/local/state')
 a.call('/apisite/economy/v1/purchases/products/900003','POST',{'expectedCurrency':1,'expectedPrice':500,'expectedSellerId':seller_before['userId'],'userAssetId':listing['userAssetId']})
 after=a.call('/local/state');seller_after=b.call('/local/state')
 assert before['balance']['robux']-after['balance']['robux']==500
 assert any(x['id']==listing['userAssetId'] for x in after['inventory'])
 assert not any(x['id']==listing['userAssetId'] for x in seller_after['inventory'])
 assert seller_after['balance']['robux']>seller_before['balance']['robux']
test('Limited resale transfers the existing copy between accounts',resale)
def login():
 before=a.call('/local/state');a.call('/apisite/auth/v2/logout','POST',{});assert not a.call('/local/state')['loggedIn'];a.call('/local/login','POST',{'username':namea,'password':pw});after=a.call('/local/state');assert before['balance']==after['balance'];assert before['inventory']==after['inventory']
test('Logout and login preserve balances and inventory',login)
