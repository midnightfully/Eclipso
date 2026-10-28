"""Session persistence and revocation across full restarts (local only). Restarts the whole stack twice.
Results: local/session-test-results.json"""
import pathlib, runpy, json, secrets, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
Client = runpy.run_path(str(ROOT / 'local/http-client.py'))['Client']
sql = runpy.run_path(str(ROOT / 'local/inspect-db.py'))['sql']
results = []
def test(name, fn):
    try:
        d = fn(); results.append({'test': name, 'result': 'PASS', 'details': d}); print('PASS', name, d, flush=True)
    except Exception as e:
        results.append({'test': name, 'result': 'FAIL', 'error': str(e)}); print('FAIL', name, e, flush=True)
    finally:
        (ROOT / 'local/session-test-results.json').write_text(json.dumps(results, indent=2, default=str))

def restart():
    for args in (['stop'], []):
        r = subprocess.run([sys.executable, str(ROOT / 'local/servers.py'), *args], capture_output=True, text=True, timeout=900)
        if args == [] and 'Ready' not in r.stdout: raise RuntimeError('restart failed: ' + r.stdout[-300:])

def me(c):
    try: return c.call('/apisite/users/v1/users/authenticated')['id']
    except RuntimeError as e: return str(e)[:3]

name = 'EclSess' + secrets.token_hex(4); pw = secrets.token_urlsafe(16)
c = Client(); uid = c.call('/local/signup', 'POST', {'username': name, 'password': pw})['userId']
other = Client(); other.call('/apisite/auth/v2/login', 'POST', {'ctype': 'username', 'cvalue': name, 'password': pw})

def stored():
    rows = int(sql(f"SELECT count(*) FROM user_web_session WHERE user_id={uid} AND revoked_at IS NULL AND expires_at > now() + interval '29 days'"))
    assert rows == 2, rows
    return '2 live sessions stored in PostgreSQL with ~30-day expiry'
test('Login creates a database session with an expiry', stored)

def survives():
    assert me(c) == uid and me(other) == uid
    restart()
    assert me(c) == uid, me(c); assert me(other) == uid, me(other)
    return 'both sessions still valid after full stop/start (cache emptied)'
test('Sessions survive a full restart', survives)

stolen = list(c.cookies)  # a copy of the cookie, as if taken before logout
def thief_client():
    t = Client()
    for ck in stolen: t.cookies.set_cookie(ck)
    return t
def logout_revokes():
    c.call('/apisite/auth/v2/logout', 'POST', {})
    assert me(c) == '401', me(c)
    thief = thief_client()
    assert me(thief) == '401', 'copied cookie still worked after logout'
    assert me(other) == uid, 'logging out one browser must not end the other session'
    revoked = int(sql(f'SELECT count(*) FROM user_web_session WHERE user_id={uid} AND revoked_at IS NOT NULL'))
    assert revoked == 1, revoked
    return 'logged-out cookie rejected (incl. a copy); other browser still signed in; 1 row revoked'
test('Logout revokes only that session', logout_revokes)

def revoked_after_restart():
    restart()
    thief = thief_client()
    assert me(thief) == '401', 'revoked session came back after restart'
    assert me(other) == uid
    return 'revoked session stays dead after restart; live one still valid'
test('Revocation survives a restart', revoked_after_restart)

raise SystemExit(1 if any(r['result'] == 'FAIL' for r in results) else 0)
