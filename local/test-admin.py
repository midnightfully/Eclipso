"""Admin authorization and audit-trail integration test (local only).

Creates two synthetic accounts (AdmTestUser*, AdmTestStaff*), gives the staff account a few permissions
directly in the database for the duration of the test, and removes them in `finally`.
Does not touch the configured owner account or user 1. Results: local/admin-test-results.json
"""
import pathlib, runpy, json, re, secrets, urllib.request, urllib.error

ROOT = pathlib.Path(__file__).resolve().parent.parent
helpers = runpy.run_path(str(ROOT / 'local/http-client.py'))
Client = helpers['Client']
sql = runpy.run_path(str(ROOT / 'local/inspect-db.py'))['sql']
BASE = 'http://127.0.0.1:5080'

names = re.findall(r'^\s*(\w+)\s*,', (ROOT / 'Roblox/Roblox.Models/Enums/Staff.cs').read_text(), re.M)
perm = {n: names.index(n) for n in ['GetAdminLogs', 'SetPermissions', 'GetStats']}

results = []
def test(name, fn):
    try:
        detail = fn(); results.append({'test': name, 'result': 'PASS', 'details': detail}); print('PASS', name, detail, flush=True)
    except Exception as e:
        results.append({'test': name, 'result': 'FAIL', 'error': str(e)}); print('FAIL', name, e, flush=True)
    finally:
        (ROOT / 'local/admin-test-results.json').write_text(json.dumps(results, indent=2))

def status(client, path, method='GET', body=None):
    """Return the HTTP status (redirects not followed) for a request made with client's cookies."""
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k): return None
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(client.cookies), NoRedirect)
    for attempt in range(2):
        req = urllib.request.Request(BASE + path, data=json.dumps(body).encode() if body is not None else None, method=method,
                                     headers={'User-Agent': 'EclipsoAdminTest/1.0', 'Content-Type': 'application/json', 'x-csrf-token': client.token, 'Origin': BASE})
        try:
            with opener.open(req, timeout=30) as r: return r.status, r.headers.get('Location')
        except urllib.error.HTTPError as e:
            if e.code == 403 and e.headers.get('x-csrf-token') and attempt == 0: client.token = e.headers['x-csrf-token']; continue
            return e.code, e.headers.get('Location')

def make_account(prefix):
    c = Client(); name = prefix + secrets.token_hex(3)
    uid = c.call('/local/signup', 'POST', {'username': name, 'password': secrets.token_urlsafe(18)})['userId']
    return c, uid, name

anon = Client()
user, user_id, user_name = make_account('AdmTestUser')
staff, staff_id, staff_name = make_account('AdmTestStaff')
owner_id = json.loads((ROOT / 'Roblox/Roblox.Website/appsettings.json').read_text()).get('OwnerUserId')
assert owner_id not in (user_id, staff_id)
first_audit_id = int(sql('SELECT coalesce(max(id),0) FROM admin_audit_log'))

try:
    for p in perm.values():
        sql(f'INSERT INTO user_permission(user_id,permission) VALUES ({staff_id},{p}) ON CONFLICT DO NOTHING')

    def anon_blocked():
        page = status(anon, '/admin/'); api = status(anon, '/admin-api/api/stats')
        assert page[0] == 302 and page[1].endswith('/home'), page
        assert api[0] == 403, api
        return {'admin page': page, 'admin api': api[0]}
    test('Logged-out visitor cannot open admin page or API', anon_blocked)

    def user_blocked():
        checks = {
            'page /admin/': status(user, '/admin/')[0],
            'GET stats': status(user, '/admin-api/api/stats')[0],
            'GET audit log': status(user, '/admin-api/api/logs?logType=audit')[0],
            'POST give permission to self': status(user, f'/admin-api/api/staff/permissions?userId={user_id}&permission=GetStats', 'POST', {})[0],
            'GET pending asset image (was unguarded)': status(user, '/admin-api/api/assets/pending-assets/image/x')[0],
            'GET lottery users (was unguarded)': status(user, '/admin-api/api/lottery/get-users-eligible')[0],
        }
        assert checks['page /admin/'] == 302, checks
        bad = {k: v for k, v in checks.items() if k != 'page /admin/' and v != 403}
        assert not bad, bad
        return checks
    test('Normal user is refused by the server (page redirect, API 403)', user_blocked)

    def no_perms_leaked():
        n = int(sql(f'SELECT count(*) FROM user_permission WHERE user_id={user_id}'))
        assert n == 0, n
        return 'normal user still has 0 staff permissions'
    test('Refused self-promotion did not change the database', no_perms_leaked)

    def staff_allowed():
        page = status(staff, '/admin/'); stats = status(staff, '/admin-api/api/stats')
        assert page[0] == 200 and stats[0] == 200, (page, stats)
        denied = status(staff, '/admin-api/api/assets/pending-assets/image/x')[0]
        assert denied == 403, denied  # staff without GetPendingModerationItems
        return {'page': page[0], 'stats': stats[0], 'permission it lacks': denied}
    test('Staff opens panel; per-permission checks still apply', staff_allowed)

    def staff_cannot_escalate():
        s = status(staff, f'/admin-api/api/staff/permissions?userId={user_id}&permission=GetStats', 'POST', {})[0]
        s2 = status(staff, f'/admin-api/api/staff/permissions?userId={staff_id}&permission=GiveUserRobux', 'POST', {})[0]
        assert s == 403 and s2 == 403, (s, s2)
        assert int(sql(f'SELECT count(*) FROM user_permission WHERE user_id={user_id}')) == 0
        assert int(sql(f"SELECT count(*) FROM user_permission WHERE user_id={staff_id}")) == len(perm)
        return 'staff holding SetPermissions cannot grant others or itself (owner-only), DB unchanged'
    test('Role management is owner-only', staff_cannot_escalate)

    def audit_recorded():
        rows = json.loads(sql(f"SELECT coalesce(json_agg(t ORDER BY id),'[]') FROM (SELECT id, actor_user_id, method, action, status_code, outcome FROM admin_audit_log WHERE id > {first_audit_id}) t"))
        by_actor = lambda a: [r for r in rows if r['actor_user_id'] == a]
        assert any(r['action'] == 'SetUserPermissions' and r['status_code'] == 403 for r in by_actor(user_id)), rows
        assert any(r['action'] == 'SetUserPermissions' and r['status_code'] == 403 and 'owner' in r['outcome'] for r in by_actor(staff_id)), rows
        assert any(r['actor_user_id'] is None and r['status_code'] == 403 for r in rows), rows
        listed = staff.call('/admin-api/api/logs?logType=audit&limit=50')
        assert any(r.get('actor_user_id') == staff_id for r in listed['data']), 'audit API did not list staff entries'
        return {'new audit rows': len(rows), 'visible in admin Logs page API': True}
    test('Denied attempts are recorded in the audit trail and visible to staff', audit_recorded)

    def logout_respected():
        staff.call('/apisite/auth/v2/logout', 'POST', {})
        page = status(staff, '/admin/'); api = status(staff, '/admin-api/api/stats')
        assert page[0] == 302 and api[0] == 403, (page, api)
        return {'after logout page': page[0], 'api': api[0]}
    test('Logout ends admin access', logout_respected)
finally:
    for p in perm.values():
        sql(f'DELETE FROM user_permission WHERE user_id={staff_id} AND permission={p}')
    left = sql(f'SELECT count(*) FROM user_permission WHERE user_id IN ({user_id},{staff_id})')
    print('cleanup: remaining test permissions =', left)

raise SystemExit(1 if any(r['result'] == 'FAIL' for r in results) else 0)
