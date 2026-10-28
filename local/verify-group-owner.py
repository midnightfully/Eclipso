import pathlib,runpy,json
ROOT=pathlib.Path(__file__).resolve().parent.parent
Client=runpy.run_path(str(ROOT/'local/http-client.py'))['Client'];c=Client()
results=json.loads((ROOT/'local/social-test-results.json').read_text());group=next(x['details'] for x in results if x['test']=='Group creation and membership' and x['result']=='PASS')
accounts=json.loads((ROOT/'.local/test-accounts.json').read_text());c.call('/local/login','POST',{'username':accounts['buyer'],'password':accounts['password']});uid=c.call('/local/state')['userId']
g=c.call('/apisite/groups/v1/groups/'+str(group['groupId']));assert g['owner']['userId']==uid,g['owner'];print('PASS: saved group and creator ownership remain after service restart')
