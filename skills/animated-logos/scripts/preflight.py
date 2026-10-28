#!/usr/bin/env python3
"""Report existing local rendering dependencies as JSON; install nothing."""
import argparse,json,shutil,subprocess,sys
from pathlib import Path


def executable(name,args):
    found=shutil.which(name)
    if not found:return {'ok':False,'detail':f'Executable not found: {name}'}
    try:
        p=subprocess.run([found,*args],capture_output=True,text=True,timeout=12)
        line=(p.stdout or p.stderr).splitlines()
        return {'ok':p.returncode==0,'path':found,'version':line[0] if line else 'No version output'}
    except (OSError,subprocess.TimeoutExpired) as e:return {'ok':False,'detail':str(e)}


def inspect(pipeline,node='node',blender='blender',ffmpeg='ffmpeg',ffprobe='ffprobe',playwright_module='playwright',browser=''):
    checks={'python':{'ok':sys.version_info>=(3,10),'version':sys.version.split()[0]},'node':executable(node,['--version']),'ffmpeg':executable(ffmpeg,['-version']),'ffprobe':executable(ffprobe,['-version'])}
    if pipeline=='blender':checks['blender']=executable(blender,['--version'])
    if checks['node']['ok']:
        script="const fs=require('node:fs');try{const m=process.argv[1],p=require(m),b=process.argv[2]||p.chromium.executablePath();console.log(JSON.stringify({ok:fs.existsSync(b),module:require.resolve(m),browser:b,detail:fs.existsSync(b)?'Existing browser found':'Browser missing; pass --browser for an installed Chromium browser'}))}catch(e){console.log(JSON.stringify({ok:false,detail:e.message.split('\\n')[0]}))}"
        try:
            p=subprocess.run([checks['node']['path'],'-e',script,playwright_module,browser],capture_output=True,text=True,timeout=12)
            checks['browser_runtime']=json.loads(p.stdout)
        except (OSError,ValueError,subprocess.TimeoutExpired) as e:checks['browser_runtime']={'ok':False,'detail':str(e)}
    else:checks['browser_runtime']={'ok':False,'detail':'Check Node before resolving Playwright and Chromium'}
    missing=[name for name,result in checks.items() if not result['ok']]
    return {'schemaVersion':1,'pipeline':pipeline,'ready':not missing,'missing':missing,'checks':checks,'nextAction':'Run the selected pipeline with the resolved executable paths.' if not missing else 'Resolve missing tools from existing local installations, then rerun preflight. No installation or download was attempted.'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pipeline',choices=['canvas','blender'],required=True)
    for name,default in [('node','node'),('blender','blender'),('ffmpeg','ffmpeg'),('ffprobe','ffprobe'),('playwright-module','playwright'),('browser','')]:p.add_argument('--'+name,default=default)
    a=p.parse_args();result=inspect(**vars(a));print(json.dumps(result,indent=2));return 0 if result['ready'] else 2

if __name__=='__main__':sys.exit(main())
