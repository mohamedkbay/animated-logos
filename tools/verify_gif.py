#!/usr/bin/env python3
"""Verify an actual animated, looping preview rather than just a GIF header."""
import argparse,hashlib,json
from pathlib import Path
from PIL import Image

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('gif');p.add_argument('--width',type=int);p.add_argument('--duration',type=float)
a=p.parse_args();file=Path(a.gif);image=Image.open(file)
assert image.format=='GIF' and image.n_frames>1
assert image.info.get('loop')==0
if a.width:assert image.width==a.width
duration=0;distinct=set()
for i in range(image.n_frames):
    image.seek(i);duration+=image.info.get('duration',0)
    sample=image.convert('RGB');sample.thumbnail((160,90))
    distinct.add(hashlib.sha256(sample.tobytes()).hexdigest())
assert len(distinct)>2,'Preview appears static'
if a.duration is not None:assert abs(duration/1000-a.duration)<=.1
print(json.dumps({'frames':image.n_frames,'size':image.size,'duration_ms':duration,
                  'distinct_sampled_frames':len(distinct),'loop':0,'bytes':file.stat().st_size},indent=2))
