#!/usr/bin/env python3
"""Small local toolkit. No downloads, installs, external accounts or paid calls."""
import argparse
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path
from motionlib import PROFILES, load_project, sample, local_file

def write_json(path, value):
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def demo(args):
    root=Path(args.project).resolve()
    if (root/'plan.json').exists():
        raise ValueError('Project already exists; use a new directory to preserve it')
    root.mkdir(parents=True,exist_ok=True); assets=root/'assets'; assets.mkdir(exist_ok=True)
    w,h=args.width,args.height; sx=w/1920; sy=h/1080; unit=min(sx,sy)
    pivot=[w*.36,h*.5]
    def svg(body):
        return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>'
    blade='<path d="M0 0 C-16 -34 -8 -70 29 -90 C42 -58 37 -20 0 0Z"/>'
    parts=[f'<g transform="translate({pivot[0]} {pivot[1]}) scale({unit}) rotate({i*120})" fill="#3e43e8">{blade}</g>' for i in range(3)]
    letters=[
        'M0 120V0H22L75 80V0H100V120H78L25 40V120Z',
        'M50 0C15 0 0 20 0 60S15 120 50 120 100 100 100 60 85 0 50 0ZM50 25C68 25 75 36 75 60S68 95 50 95 25 84 25 60 32 25 50 25Z',
        'M0 0H27L50 86 73 0H100L65 120H35Z',
        'M0 120L36 0H64L100 120H73L67 95H33L27 120ZM39 72H61L50 29Z',
    ]
    timing=dict(gather_start=.15,gather_end=.85,handoff=round(.95*args.fps)/args.fps,
                move_start=1.08,move_end=1.63)
    layers=[]
    def add(name,role,body,start,end,piv,**extra):
        (assets/(name+'.svg')).write_text(svg(body),encoding='utf8')
        layers.append(dict(name=name,role=role,svg=f'assets/{name}.svg',png=f'assets/{name}.png',
                           start=start,end=end,pivot=piv,**extra))
    if not args.transparent:
        add('00-background','background',f'<rect width="{w}" height="{h}" fill="white"/>',0,5.5,[w/2,h/2])
    for i,part in enumerate(parts):
        add(f'10-part-{i}','part',part,timing['gather_start'],timing['handoff'],pivot,part_index=i)
    add('20-symbol-master','whole',''.join(parts),timing['handoff'],5.5,pivot)
    letter_bodies=[]
    for i,path in enumerate(letters):
        x=w*.425+i*115*unit; y=h/2-60*unit
        body=f'<g transform="translate({x} {y}) scale({unit})"><path fill="#111111" fill-rule="evenodd" d="{path}"/></g>'
        letter_bodies.append(body)
        add(f'30-letter-{i}','letter',body,1.73+i*.095,5.5,[x+50*unit,y+60*unit])
    backdrop='' if args.transparent else f'<rect width="{w}" height="{h}" fill="white"/>'
    (assets/'final-master.svg').write_text(svg(backdrop+''.join(parts+letter_bodies)),encoding='utf8')
    plan=dict(schema=1,title='NOVA — original logo study',width=w,height=h,fps=args.fps,duration=5.5,
              transparent=args.transparent,profile=args.profile,timing=timing,layers=layers,
              master_svg='assets/final-master.svg',master_png='assets/final-master.png',
              provenance='Original geometric demonstration artwork; no customer assets or fonts')
    write_json(root/'plan.json',plan)
    load_project(root)
    print(f'Created {args.profile} demo: {len(layers)} layers, {w}x{h}, {args.fps} fps')

def sampled(args):
    root=Path(args.project).resolve(); plan=load_project(root)
    write_json(root/'timeline.json',sample(plan)); print('Saved timeline.json')

def encode(args):
    root=Path(args.project).resolve();plan=load_project(root)
    if plan.get('transparent'):
        raise ValueError('MP4 flattens alpha. Deliver the RGBA PNG sequence or choose an alpha-capable encoder explicitly.')
    if plan['width']%2 or plan['height']%2:
        raise ValueError('The yuv420p MP4 helper needs even width and height; retain the PNGs or choose an appropriate output size.')
    exe=shutil.which(args.ffmpeg)
    if not exe:raise ValueError('ffmpeg not found; supply --ffmpeg')
    output=Path(args.output).resolve()
    if output.exists():raise ValueError('Output exists; choose a new version')
    output.parent.mkdir(parents=True,exist_ok=True)
    cmd=[exe,'-hide_banner','-n','-framerate',str(plan['fps']),'-i',str(root/'frames/frame-%04d.png'),
         '-t',str(plan['duration']),'-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(output)]
    subprocess.run(cmd,check=True);print(output)

def contact(args):
    from PIL import Image,ImageDraw
    root=Path(args.project).resolve();plan=load_project(root)
    frames=sorted((root/'frames').glob('frame-*.png'))
    if not frames:raise ValueError('No rendered frames')
    selected=frames[::args.step]
    cellw=320;cellh=round(cellw*plan['height']/plan['width'])+23
    page_size=30
    out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
    for page,offset in enumerate(range(0,len(selected),page_size)):
        group=selected[offset:offset+page_size]
        sheet=Image.new('RGB',(cellw*5,cellh*math.ceil(len(group)/5)),'#e5e5e5');draw=ImageDraw.Draw(sheet)
        for i,path in enumerate(group):
            source=Image.open(path).convert('RGBA');back=Image.new('RGBA',source.size,'white');back.alpha_composite(source)
            im=back.convert('RGB');im.thumbnail((cellw,cellh-23));x=i%5*cellw;y=i//5*cellh
            sheet.paste(im,(x,y));frame=int(path.stem.split('-')[-1]);draw.text((x+4,y+cellh-20),f'{(frame-1)/plan["fps"]:.2f}s',fill='black')
        sheet.save(out/f'contact-{page:02}.jpg',quality=93)
    print(f'Saved {math.ceil(len(selected)/page_size)} timestamped sheets')

def ae_script(args):
    root=Path(args.project).resolve();plan=load_project(root);spec=sample(plan)
    for layer in spec['layers']:
        if not local_file(root,layer['png']).is_file():raise ValueError('Rasterize assets first')
    # Embed a literal for ES3/ExtendScript compatibility; JSON.parse is not required.
    jsx='''// animated logos: experimental, sampled raster-layer import. Does not save or render.
(function () {
var spec = SPEC;
var root = File($.fileName).parent;
for (var n=0;n<spec.layers.length;n++) {
  if (!File(root.fsName+"/"+spec.layers[n].png).exists) throw Error("Missing logo asset");
}
app.beginUndoGroup("animated logos import");
try {
  if (!app.project) app.newProject();
  var comp=app.project.items.addComp("animated logos",spec.width,spec.height,1,spec.duration,spec.fps);
  comp.motionBlur=false;
  for(var i=0;i<spec.layers.length;i++) {
    var s=spec.layers[i];
    var io=new ImportOptions(File(root.fsName+"/"+s.png));
    var layer=comp.layers.add(app.project.importFile(io));
    layer.name=s.name;layer.startTime=0;
    layer.inPoint=(s.start_frame-1)/spec.fps;layer.outPoint=(s.end_frame-1)/spec.fps;
    var tr=layer.property("ADBE Transform Group");
    tr.property("ADBE Anchor Point").setValue(s.pivot);
    var times=[],pos=[],sc=[],rot=[],alpha=[];
    for(var j=0;j<s.samples.length;j++) {
      var r=s.samples[j];times.push((r[0]-1)/spec.fps);
      pos.push([s.pivot[0]+r[2],s.pivot[1]+r[3]]);
      sc.push([100*r[4],100*r[5]]);rot.push(r[6]);alpha.push(100*r[1]);
    }
    var names=["ADBE Position","ADBE Scale","ADBE Rotate Z","ADBE Opacity"];
    var values=[pos,sc,rot,alpha];
    for(var p=0;p<names.length;p++) {
      var prop=tr.property(names[p]);prop.setValuesAtTimes(times,values[p]);
      for(var k=1;k<=prop.numKeys;k++) prop.setInterpolationTypeAtKey(k,KeyframeInterpolationType.LINEAR,KeyframeInterpolationType.LINEAR);
    }
  }
  comp.openInViewer();
} finally { app.endUndoGroup(); }
}());
'''.replace('SPEC',json.dumps(spec,ensure_ascii=True,separators=(',',':')))
    output=root/'import-motion.jsx'
    output.write_text(jsx,encoding='utf8');print('Generated experimental import-motion.jsx; AE execution not verified')

def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='action',required=True)
    d=sub.add_parser('demo');d.add_argument('--project',required=True);d.add_argument('--profile',choices=PROFILES,default='clean')
    d.add_argument('--width',type=int,default=1920);d.add_argument('--height',type=int,default=1080);d.add_argument('--fps',type=int,default=30)
    d.add_argument('--transparent',action='store_true');d.set_defaults(fn=demo)
    for name,fn in [('sample',sampled),('ae-script',ae_script)]:
        p=sub.add_parser(name);p.add_argument('--project',required=True);p.set_defaults(fn=fn)
    e=sub.add_parser('encode');e.add_argument('--project',required=True);e.add_argument('--output',required=True);e.add_argument('--ffmpeg',default='ffmpeg');e.set_defaults(fn=encode)
    c=sub.add_parser('contact-sheet');c.add_argument('--project',required=True);c.add_argument('--output',required=True);c.add_argument('--step',type=int,default=3);c.set_defaults(fn=contact)
    args=parser.parse_args()
    if getattr(args,'width',1)<=0 or getattr(args,'height',1)<=0 or getattr(args,'fps',30)<=0 or getattr(args,'fps',30)%2 or getattr(args,'step',1)<=0:
        parser.error('Positive dimensions/step and an even fps are required by the 5.5-second demo')
    try:args.fn(args)
    except (ValueError,FileNotFoundError,KeyError) as error:parser.exit(2,f'Error: {error}\n')

if __name__=='__main__':main()
