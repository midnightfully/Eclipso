"""Security regression tests (local only): cross-site request refusal, untrusted-upload gate.
Results: local/security-test-results.json"""
import pathlib, runpy, json, secrets, time, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
h = runpy.run_path(str(ROOT / 'local/http-client.py'))
Client, multipart = h['Client'], h['multipart']
BASE = 'http://127.0.0.1:5080'
results = []
def test(name, fn):
    try:
        d = fn(); results.append({'test': name, 'result': 'PASS', 'details': d}); print('PASS', name, d, flush=True)
    except Exception as e:
        results.append({'test': name, 'result': 'FAIL', 'error': str(e)}); print('FAIL', name, e, flush=True)
    finally:
        (ROOT / 'local/security-test-results.json').write_text(json.dumps(results, indent=2, default=str))

c = Client(); name = 'EclSec' + secrets.token_hex(4)
uid = c.call('/local/signup', 'POST', {'username': name, 'password': secrets.token_urlsafe(16)})['userId']

def raw(path, headers, body=b'{}'):
    req = urllib.request.Request(BASE + path, data=body, method='POST', headers={'User-Agent': 'Mozilla/5.0 EclipsoSecTest', 'Content-Type': 'application/json', **headers})
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(c.cookies))
    try:
        with opener.open(req, timeout=30) as r: return r.status, r.read().decode()[:200]
    except urllib.error.HTTPError as e: return e.code, e.read().decode()[:200]

def cross_site():
    out = {}
    for label, path in [('CSRF-exempt route /user/request-friendship', '/user/request-friendship?recipientUserId=1'),
                        ('CSRF-exempt route /marketplace/purchase', '/marketplace/purchase'),
                        ('normal API route', '/apisite/auth/v2/logout')]:
        for hdr in ({'Origin': 'https://evil.example'}, {'Sec-Fetch-Site': 'cross-site'}, {'Origin': 'null'}):
            st, body = raw(path, hdr)
            assert st == 403 and 'Cross-site request refused' in body, (label, hdr, st, body)
        out[label] = '403 for foreign Origin, Sec-Fetch-Site cross-site, null Origin'
    assert c.call('/apisite/users/v1/users/authenticated')['id'] == uid, 'session was affected'
    return out
test('Cross-site browser requests are refused, incl. CSRF-exempt routes', cross_site)

def client_style_allowed():
    st, body = raw('/user/request-friendship?recipientUserId=1', {})  # game-client style: no Origin / Sec-Fetch
    assert 'Cross-site request refused' not in body, (st, body)
    st2, body2 = raw('/apisite/auth/v2/logout', {'Origin': BASE, 'Sec-Fetch-Site': 'same-origin'})
    assert 'Cross-site request refused' not in body2, (st2, body2)
    return {'no-origin client request': st, 'same-origin browser request': st2}
test('Same-site and game-client style requests are not blocked by the cross-site check', client_style_allowed)

c2 = Client(); c2.call('/local/signup', 'POST', {'username': 'EclSec' + secrets.token_hex(4), 'password': secrets.token_urlsafe(16)})
def upload_gate():
    out = {}
    for label, type_id, fname, data in [('mesh', 4, 'x.mesh', b'version 1.00\n1\n[0,0,0][0,0,0][0,0,0]'), ('audio', 3, 'x.mp3', b'ID3' + b'\0' * 64), ('shirt', 11, 's.png', h['png']())]:
        time.sleep(6)  # the site allows one upload attempt per 5 seconds per user/IP
        try:
            multipart(c2, '/develop/upload', {'name': 'gate test', 'assetType': type_id}, [('file', fname, 'application/octet-stream', data)])
            raise AssertionError(label + ' upload was accepted')
        except RuntimeError as e:
            assert e.args[0].startswith('400') and 'not available yet' in e.args[0], e.args[0][:200]
            out[label] = 'refused: not available yet'
    time.sleep(6)
    try:
        multipart(c2, '/develop/upload-version', {'assetId': 1}, [('file', 'p.rbxl', 'application/octet-stream', b'<roblox></roblox>')])
        raise AssertionError('place version upload accepted')
    except RuntimeError as e:
        assert e.args[0].startswith('400') and 'not available yet' in e.args[0], e.args[0][:200]
        out['place version'] = 'refused'
    return out
test('Uploads needing native tools / RCC are refused while the gate is off', upload_gate)

raise SystemExit(1 if any(r['result'] == 'FAIL' for r in results) else 0)
