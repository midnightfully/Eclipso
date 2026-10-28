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

import secrets,struct,zlib
results=[]
def test(name,fn):
 try:
  result=fn();results.append({'test':name,'result':'PASS','details':result});print('PASS',name,str(result),flush=True)
 except Exception as e:
  results.append({'test':name,'result':'FAIL','error':str(e)});print('FAIL',name,str(e),flush=True)
 finally:(ROOT/'local/social-test-results.json').write_text(json.dumps(results,indent=2))
a=Client();b=Client();accounts=json.loads((ROOT/'.local/test-accounts.json').read_text())
a.call('/local/login','POST',{'username':accounts['buyer'],'password':accounts['password']});b.call('/local/login','POST',{'username':accounts['seller'],'password':accounts['password']})
aid=a.call('/local/state')['userId'];bid=b.call('/local/state')['userId']
def friends():
 a.call('/apisite/friends/v1/users/'+str(bid)+'/unfriend','POST',{})
 a.call('/apisite/friends/v1/users/'+str(bid)+'/request-friendship','POST',{})
 req=b.call('/apisite/friends/v1/my/friends/requests?limit=10')['data'];assert any(x['id']==aid for x in req),req
 b.call('/apisite/friends/v1/users/'+str(aid)+'/accept-friend-request','POST',{})
 for client,uid,target in [(a,aid,bid),(b,bid,aid)]:
  items=client.call('/apisite/friends/v1/users/'+str(uid)+'/friends')['data'];assert any(x['id']==target for x in items),items
 a.call('/apisite/friends/v1/users/'+str(bid)+'/unfriend','POST',{})
 assert not any(x['id']==bid for x in a.call('/apisite/friends/v1/users/'+str(aid)+'/friends')['data'])
 return 'request, accept, reciprocal lists, remove'
def multipart(client,path,fields,files):
 boundary='LocalBoundary'+secrets.token_hex(12);parts=[]
 for key,value in fields.items():parts.append(('--'+boundary+'\r\nContent-Disposition: form-data; name="'+key+'"\r\n\r\n'+str(value)+'\r\n').encode())
 for key,filename,mime,data in files:parts.append(('--'+boundary+'\r\nContent-Disposition: form-data; name="'+key+'"; filename="'+filename+'"\r\nContent-Type: '+mime+'\r\n\r\n').encode()+data+b'\r\n')
 payload=b''.join(parts)+('--'+boundary+'--\r\n').encode()
 for attempt in range(2):
  request=urllib.request.Request(BASE+path,data=payload,headers={'User-Agent':'BubbabloxLocalTest/1.0','Content-Type':'multipart/form-data; boundary='+boundary,'Origin':BASE,'x-csrf-token':client.token})
  try:
   with client.http.open(request,timeout=60) as response:
    data=response.read().decode();return json.loads(data) if data else {}
  except urllib.error.HTTPError as e:
   if e.code==403 and e.headers.get('x-csrf-token') and attempt==0:client.token=e.headers['x-csrf-token'];continue
   raise RuntimeError(str(e.code)+' '+e.read().decode()[:1600])
def png():
 def chunk(t,d):return struct.pack('!I',len(d))+t+d+struct.pack('!I',zlib.crc32(t+d))
 return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',16,16,8,2,0,0,0))+chunk(b'IDAT',zlib.compress((b'\0'+b'\x28\x8e\xc8'*16)*16))+chunk(b'IEND',b'')
def group():
 old=a.call('/local/state')['balance']['robux'];name='Local Group '+secrets.token_hex(3)
 created=multipart(a,'/apisite/groups/v1/groups/create',{'name':name,'description':'Local integration test group','publicGroup':'true','buildersClubMembersOnly':'false'},[('icon','icon.png','image/png',png())]);gid=created['id']
 details=a.call('/apisite/groups/v1/groups/'+str(gid));assert details['name']==name,details
 assert a.call('/local/state')['balance']['robux']==old-100
 b.call('/apisite/groups/v1/groups/'+str(gid)+'/users','POST',{})
 roles=b.call('/apisite/groups/v1/users/'+str(bid)+'/groups/roles')['data'];assert any(x['group']['id']==gid for x in roles),roles
 return {'groupId':gid,'name':name,'checks':'create, owner, 100 debit, public join'}
def profile():
 data=a.call('/apisite/users/v1/users/1');expected=json.loads((ROOT/'docs/roblox-profile.json').read_text());assert data['name']==expected['username'] and data['description']==expected['description'];return {'id':data['id'],'name':data['name']}
test('Roblox system profile public API',profile)
test('Friendship lifecycle',friends)
test('Group creation and membership',group)
