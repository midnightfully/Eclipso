"""Choose an existing personal account as local site owner; no passwords handled."""
import pathlib,runpy,json,sys,os
ROOT=pathlib.Path(__file__).resolve().parent.parent
cfgpath=ROOT/'Roblox/Roblox.Website/appsettings.json'
cfg=json.loads(cfgpath.read_text())
if not cfg.get('LocalDevelopment'):raise SystemExit('Owner setup is available only in local development.')
name=sys.argv[1] if len(sys.argv)>1 else input('Your existing website username: ').strip()
if not name:raise SystemExit('No username entered. Nothing changed.')
ctx=runpy.run_path(str(ROOT/'local/inspect-db.py'))
rows=json.loads(ctx['sql']("SELECT coalesce(json_agg(t),'[]') FROM (SELECT id,username FROM \"user\" WHERE lower(username)=lower('"+name.replace("'","''")+"')) t"))
if len(rows)!=1:raise SystemExit('Account not found. Create it at http://127.0.0.1:5080/local first.')
account=rows[0]
if account['id']==1:raise SystemExit('Roblox is the automated system account. Choose your personal account.')
if '--check-only' in sys.argv:print('Validated existing personal account; configuration unchanged.');raise SystemExit(0)
backup=ROOT/'.local/backups';backup.mkdir(exist_ok=True)
backup_prev=cfg.get('OwnerUserId')
(backup/'owner-before-change.json').write_text(json.dumps({'OwnerUserId':backup_prev}))
cfg['OwnerUserId']=str(account['id'])
tmp=cfgpath.with_suffix('.json.tmp');tmp.write_text(json.dumps(cfg,indent=2));os.replace(tmp,cfgpath)
ctx['sql']("INSERT INTO admin_audit_log(actor_user_id,method,path,action,parameters,status_code,outcome) VALUES (NULL,'LOCAL','local/set-owner.py','SetOwner','"+json.dumps({'previousOwnerUserId':backup_prev,'newOwnerUserId':account['id'],'username':account['username']}).replace("'","''")+"',200,'success: configuration changed by operator on this PC')")
print('Site owner set to '+account['username']+' (#'+str(account['id'])+'). Restart the website, then sign in and open /admin/.')
