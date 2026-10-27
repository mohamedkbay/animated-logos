#!/usr/bin/env python3
"""Check real rendered endpoints against the vector master's rasterization."""
import argparse,json,subprocess,math
from pathlib import Path
from PIL import Image,ImageChops,ImageStat

p=argparse.ArgumentParser();p.add_argument('--project',required=True);p.add_argument('--video');p.add_argument('--ffprobe',default='ffprobe');a=p.parse_args()
root=Path(a.project).resolve();plan=json.loads((root/'plan.json').read_text())
expected=round(plan['duration']*plan['fps']);frames=sorted((root/'frames').glob('frame-*.png'))
assert len(frames)==expected,(len(frames),expected)
for i,f in enumerate(frames,1):assert f.name==f'frame-{i:04}.png',f.name
actual=Image.open(frames[-1]).convert('RGBA');master=Image.open(root/plan['master_png']).convert('RGBA')
assert actual.size==master.size==(plan['width'],plan['height'])
if plan.get('transparent'):
    assert actual.getchannel('A').getextrema()[0]==0
    alpha_rms=ImageStat.Stat(ImageChops.difference(actual.getchannel('A'),master.getchannel('A'))).rms[0]
    assert alpha_rms<1,alpha_rms
else:alpha_rms=0
def on_white(im):
    bg=Image.new('RGBA',im.size,'white');bg.alpha_composite(im);return bg.convert('RGB')
rms=max(ImageStat.Stat(ImageChops.difference(on_white(actual),on_white(master))).rms)
assert rms<1,rms
result=dict(frames=len(frames),size=list(actual.size),fps=plan['fps'],master_rms=rms,alpha_rms=alpha_rms)
if a.video:
    info=json.loads(subprocess.check_output([a.ffprobe,'-v','error','-show_streams','-show_format','-of','json',a.video]))
    v=next(s for s in info['streams'] if s['codec_type']=='video')
    assert v['codec_name']=='h264' and v['pix_fmt']=='yuv420p'
    assert (v['width'],v['height'])==actual.size
    n,d=map(int,v['r_frame_rate'].split('/'));assert n/d==plan['fps']
    assert abs(float(info['format']['duration'])-plan['duration'])<1/plan['fps']
    result['encoded']='H.264 yuv420p, expected frame rate and duration'
print(json.dumps(result,indent=2))
