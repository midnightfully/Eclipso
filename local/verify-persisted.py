"""Capture a current baseline, restart separately, then verify unchanged account state."""
import pathlib,runpy,json,sys
ROOT=pathlib.Path(__file__).resolve().parent.parent
Client=runpy.run_path(str(ROOT/'local/http-client.py'))['Client']
args=sys.argv[1:]
if args not in [['capture'],['verify']]:raise SystemExit('Usage: python local/verify-persisted.py capture|verify; restart between the two commands.')
account=json.loads((ROOT/'.local/test-accounts.json').read_text());client=Client()
client.call('/local/login','POST',{'username':account['buyer'],'password':account['password']});state=client.call('/local/state')
snapshot={key:state[key] for key in ['userId','balance','inventory']};path=ROOT/'.local/restart-snapshot.json'
if args==['capture']:path.write_text(json.dumps(snapshot,indent=2));print('Captured current balance and inventory. Restart the services, then run verify.')
else:
 if not path.exists():raise SystemExit('Capture a baseline before restarting first.')
 assert snapshot==json.loads(path.read_text()),'Account state changed from the captured baseline'
 print('PASS: account, balance and inventory match the captured baseline')
