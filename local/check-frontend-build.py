import pathlib,subprocess,os
ROOT=pathlib.Path(__file__).resolve().parent.parent
env=os.environ.copy();env.update(NEXT_BUILD_DIR='.next-check',NEXT_TELEMETRY_DISABLED='1',NEXT_IGNORE_INCORRECT_LOCKFILE='1')
with open(ROOT/'.local/frontend-build.log','wb') as log:
 result=subprocess.run(['C:/Program Files/nodejs/node.exe',str(ROOT/'2016-roblox-main/node_modules/next/dist/bin/next'),'build'],cwd=ROOT/'2016-roblox-main',env=env,stdout=log,stderr=subprocess.STDOUT)
print('Frontend production build exit:',result.returncode)
raise SystemExit(result.returncode)
