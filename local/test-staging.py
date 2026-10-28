"""External smoke test of https://staging.eclipso.lol through Caddy (HTTPS + staging basic auth).
Creates one synthetic account (EclStg*). Reads the staging password from .local/staging-login.txt.
Results: local/staging-test-results.json"""
import pathlib, json, secrets, base64, re, urllib.request, urllib.error, http.cookiejar

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = 'https://staging.eclipso.lol'
pw = re.search(r'password: (\S+)', (ROOT / '.local/staging-login.txt').read_text()).group(1)
BASIC = 'Basic ' + base64.b64encode(f'kindmops:{pw}'.encode()).decode()
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) EclipsoStagingTest/1.0'
results = []
def test(name, fn):
    try:
        d = fn(); results.append({'test': name, 'result': 'PASS', 'details': d}); print('PASS', name, d, flush=True)
    except Exception as e:
        results.append({'test': name, 'result': 'FAIL', 'error': str(e)}); print('FAIL', name, e, flush=True)
    finally:
        (ROOT / 'local/staging-test-results.json').write_text(json.dumps(results, indent=2, default=str))

class C:
    def __init__(self, auth=True):
        self.jar = http.cookiejar.CookieJar(); self.tok = ''; self.auth = auth
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *a, **k): return None
        self.op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar), NoRedirect)
    def req(self, path, method='GET', body=None, headers=None):
        for _ in range(2):
            h = {'User-Agent': UA, 'Content-Type': 'application/json', 'x-csrf-token': self.tok, 'Origin': SITE, **(headers or {})}
            if self.auth: h['Authorization'] = BASIC
            r = urllib.request.Request(SITE + path, json.dumps(body).encode() if body is not None else None, method=method, headers=h)
            try:
                with self.op.open(r, timeout=60) as resp: return resp.status, resp.headers, resp.read().decode(errors='replace')
            except urllib.error.HTTPError as e:
                if e.code == 403 and e.headers.get('x-csrf-token') and _ == 0: self.tok = e.headers['x-csrf-token']; continue
                return e.code, e.headers, e.read().decode(errors='replace')

def password_required():
    st, _, _ = C(auth=False).req('/login')
    assert st == 401, st
    return 'staging refuses visitors without the staging password (401)'
test('Staging is private', password_required)

def pages():
    out = {}
    for p, marker in [('/', 'SIGN UP AND START HAVING FUN'), ('/login', 'LOG IN AND START HAVING FUN'), ('/catalog', 'Catalog - Eclipso'), ('/info/revival', 'Eclipso')]:
        st, _, body = C().req(p); assert st == 200 and marker in body, (p, st, body[:120]); out[p] = 200
    return out
test('Public pages render over HTTPS', pages)

name = 'EclStg' + secrets.token_hex(4); upw = secrets.token_urlsafe(18); c = C()
def signup_login():
    st, h, body = c.req('/apisite/auth/v2/signup', 'POST', {'username': name, 'password': upw, 'birthday': '2000-01-15', 'gender': 'Male', 'acceptTerms': True})
    assert st == 200, (st, body[:200])
    cookie = h.get('Set-Cookie', '')
    assert 'secure' in cookie.lower() and 'httponly' in cookie.lower(), cookie[:200]
    st, _, me = c.req('/apisite/users/v1/users/authenticated'); me = json.loads(me)
    assert st == 200 and me['name'] == name, me
    c2 = C(); st, _, body = c2.req('/apisite/auth/v2/login', 'POST', {'ctype': 'username', 'cvalue': name, 'password': upw}); assert st == 200, body[:200]
    st, _, body = C().req('/apisite/auth/v2/login', 'POST', {'ctype': 'username', 'cvalue': name, 'password': 'wrong-password-123'}); assert st != 200
    return {'userId': me['id'], 'session cookie': 'Secure; HttpOnly', 'wrong password': 'refused'}
test('Signup, login, Secure session cookie', signup_login)

def roblox_profile():
    st, _, body = C().req('/apisite/users/v1/users/1'); u = json.loads(body)
    p = json.loads((ROOT / 'docs/roblox-profile.json').read_text(encoding='utf-8'))
    assert u['name'] == 'Roblox' and u['description'] == p['description']
    return 'user 1 Roblox with exact biography'
test('System account', roblox_profile)

def locked_down():
    out = {}
    for p in ['/local', '/local/state', '/swagger/index.html', '/swagger/v1/swagger.json']:
        st, _, _ = c.req(p); assert st in (404, 403) or (st == 200 and p.startswith('/swagger') is False and False), (p, st)
        out[p] = st
    st, _, body = c.req('/apisite/auth/v2/logout', 'POST', {}, headers={'Origin': 'https://evil.example'})
    assert st == 403 and 'Cross-site' in body, (st, body[:120]); out['cross-site POST'] = 403
    st, _, _ = c.req('/admin/'); assert st == 302, st; out['/admin as normal user'] = 'redirect'
    return out
test('Test endpoints, Swagger, cross-site and admin are locked on the server', locked_down)

def upload_gate():
    st, _, body = c.req('/develop/upload-version', 'POST', {})
    assert st in (400, 415), (st, body[:150])
    return {'place upload': st}
test('Untrusted-content uploads are refused on the server', upload_gate)

raise SystemExit(1 if any(r['result'] == 'FAIL' for r in results) else 0)
