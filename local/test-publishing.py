import pathlib,runpy,json,re,secrets
ROOT=pathlib.Path(__file__).resolve().parent.parent
helpers=runpy.run_path(str(ROOT/'local/http-client.py'));Client=helpers['Client'];multipart=helpers['multipart'];png=helpers['png']
ctx=runpy.run_path(str(ROOT/'local/inspect-db.py'));sql=ctx['sql']
accounts=json.loads((ROOT/'.local/test-accounts.json').read_text());admin=Client();buyer=Client()
admin.call('/local/login','POST',{'username':accounts['seller'],'password':accounts['password']});buyer.call('/local/login','POST',{'username':accounts['buyer'],'password':accounts['password']})
uid=admin.call('/local/state')['userId'];assert uid!=1
source=(ROOT/'Roblox/Roblox.Models/Enums/Staff.cs').read_text();names=re.findall(r'^\s*(\w+)\s*,',source,re.M)
needed=[names.index(name) for name in ['CreateAsset','SetAssetProduct','GetProductDetails','MakeItemLimited']]
existing=json.loads(sql("SELECT coalesce(json_agg(permission),'[]') FROM user_permission WHERE user_id="+str(uid)))
added=[x for x in needed if x not in existing]
results=[]
def test(name,fn):
 try:
  detail=fn();results.append({'test':name,'result':'PASS','details':detail});print('PASS',name,str(detail),flush=True)
 except Exception as e:results.append({'test':name,'result':'FAIL','error':str(e)});print('FAIL',name,str(e),flush=True)
 finally:(ROOT/'local/publishing-test-results.json').write_text(json.dumps(results,indent=2))
def profile():
 expected=json.loads((ROOT/'docs/roblox-profile.json').read_text());actual=buyer.call('/apisite/users/v1/users/1');assert actual['name']==expected['username'] and actual['description']==expected['description'],actual;return 'exact username and biography served by API'
def panel():
 with admin.http.open('http://127.0.0.1:5080/admin/',timeout=40) as r:
  text=r.read().decode();assert r.status==200 and '/admin/build-redirect/bundle.js' in text
 with admin.http.open('http://127.0.0.1:5080/admin/build-redirect/bundle.js',timeout=30) as r:assert r.status==200 and len(r.read())>1000
 return 'authenticated HTML and JavaScript bundle served'
def publish():
 nonce=secrets.token_hex(3);fields={'name':'Local Upload '+nonce,'description':'PNG publishing integration fixture','assetTypeId':1,'genre':0,'isForSale':'true','isVisible':'true','isLimited':'false','isLimitedUnique':'false','price':7}
 created=multipart(admin,'/admin-api/api/asset/create',fields,[('rbxm','local-icon.png','image/png',png())]);aid=created['assetId']
 before=buyer.call('/local/state')['balance']['robux'];buyer.call('/apisite/economy/v1/purchases/products/'+str(aid),'POST',{'expectedCurrency':1,'expectedPrice':7,'expectedSellerId':1});after=buyer.call('/local/state');assert after['balance']['robux']==before-7 and any(x['asset_id']==aid for x in after['inventory'])
 admin.call('/admin-api/api/asset/product','PATCH',{'assetId':aid,'isForSale':False,'isVisible':True,'isLimited':True,'isLimitedUnique':False,'priceRobux':7,'maxCopies':None})
 product=admin.call('/admin-api/api/product/details?assetId='+str(aid));assert product['isLimited']==True and product['isForSale']==False,product
 return {'assetId':aid,'verified':'PNG upload, real purchase, inventory, convert to limited/off-sale; no 3D rendering claimed'}
try:
 for perm in added:sql('INSERT INTO user_permission(user_id,permission) VALUES ('+str(uid)+','+str(perm)+') ON CONFLICT DO NOTHING')
 test('Exact public Roblox profile after restart',profile)
 test('Admin panel and bundle delivery',panel)
 test('Admin upload, purchase and limited product settings',publish)
finally:
 for perm in added:sql('DELETE FROM user_permission WHERE user_id='+str(uid)+' AND permission='+str(perm))
def denied():
 try:buyer.call('/admin-api/api/product/details?assetId=900001')
 except RuntimeError as e:
  assert str(e).startswith('403'),str(e);return 'non-staff rejected with HTTP 403'
 raise AssertionError('Non-staff API access was allowed')
test('Non-staff admin rejection',denied)
