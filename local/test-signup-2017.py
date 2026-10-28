import pathlib,json,runpy,secrets,time,urllib.request
ROOT=pathlib.Path(__file__).resolve().parent.parent
Client=runpy.run_path(str(ROOT/'local/http-client.py'))['Client']
for attempt in range(120):
 try:
  with urllib.request.urlopen('http://127.0.0.1:5080/local/state',timeout=2) as response:assert response.status==200
  break
 except Exception:
  if attempt==119:raise SystemExit('BLOCKED: local server is not ready; no tests run')
  time.sleep(1)
results=[]
def test(name,fn):
 try:
  details=fn();results.append({'test':name,'result':'PASS','details':details});print('PASS',name,details,flush=True)
 except Exception as e:
  results.append({'test':name,'result':'FAIL','error':str(e)});print('FAIL',name,str(e),flush=True)
 finally:(ROOT/'local/signup-2017-results.json').write_text(json.dumps(results,indent=2))
base={'username':'Landing'+secrets.token_hex(4),'password':secrets.token_urlsafe(24),'birthday':'1999-05-12','gender':'Female','acceptTerms':True}
c=Client()
def rejected(change):
 body=dict(base);body.update(change)
 try:c.call('/apisite/auth/v2/signup','POST',body)
 except RuntimeError as e:
  assert str(e).startswith('400 '),str(e);return 'HTTP 400'
 raise AssertionError('Invalid signup was accepted')
for name,change in [('Terms required',{'acceptTerms':False}),('Invalid birthday',{'birthday':'2020-02-31'}),('Future birthday',{'birthday':'2099-01-01'}),('Invalid gender',{'gender':'invalid'}),('Short password',{'password':'abc'}),('Invalid username',{'username':'a'})]:test(name,lambda change=change:rejected(change))
def signup():
 data=c.call('/apisite/auth/v2/signup','POST',base)
 assert data['userId']>1,data
 me=c.call('/apisite/users/v1/users/authenticated');assert me['id']==data['userId'] and me['name']==base['username'],me
 (ROOT/'.local/signup-test-account.json').write_text(json.dumps({'username':base['username'],'password':base['password'],'userId':data['userId']}))
 return {'userId':data['userId'],'session':'authenticated'}
test('Register and authenticated session',signup)
def login():
 other=Client();other.call('/apisite/auth/v2/login','POST',{'ctype':'username','cvalue':base['username'],'password':base['password']})
 assert other.call('/apisite/users/v1/users/authenticated')['name']==base['username']
 return 'New browser session authenticated'
test('Login with registered credentials',login)
def duplicate():
 time.sleep(5.2);return rejected({'username':base['username'].lower()})
test('Case-insensitive duplicate rejected',duplicate)
def public_page():
 for path,marker in [('/','SIGN UP AND START HAVING FUN!'),('/login','LOG IN AND START HAVING FUN!'),('/signup','SIGN UP AND START HAVING FUN!'),('/info/revival','revival')]:
  req=urllib.request.Request('http://127.0.0.1:5080'+path,headers={'User-Agent':'BubbabloxLocalTest/1.0'})
  with urllib.request.urlopen(req,timeout=90) as r:
   html=r.read().decode();assert r.status==200 and marker in html,(path,r.status,html[:100])
 return 'Signup, login and information routes render without redirect loops'
test('Public pages',public_page)
raise SystemExit(1 if any(r['result']=='FAIL' for r in results) else 0)
