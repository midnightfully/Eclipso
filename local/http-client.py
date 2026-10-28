import struct,zlib,secrets
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
