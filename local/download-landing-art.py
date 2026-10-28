import urllib.request,pathlib
root=pathlib.Path(__file__).resolve().parent.parent
url='https://images.mein-mmo.de/magazin/medien/2017/03/roblox-achterbahn.jpg'
req=urllib.request.Request(url,headers={'User-Agent':'RevivalDevelopment/1.0'})
with urllib.request.urlopen(req,timeout=30) as r:
 data=r.read();assert r.headers.get_content_type().startswith('image/'),r.headers.get_content_type()
(root/'2016-roblox-main/public/img/revival/coaster.jpg').write_bytes(data)
print('Saved historical coaster artwork:',len(data),'bytes')
