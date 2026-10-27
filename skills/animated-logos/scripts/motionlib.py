"""Shared, frame-sampled motion for Blender and experimental AE export."""
import json
import math
from pathlib import Path

PROFILES = {
    'clean': dict(spin=1.0, spread=100, damping=10, frequency=15, drop=125, stretch=.32),
    'restrained': dict(spin=.16, spread=36, damping=14, frequency=8, drop=42, stretch=.06),
    'elastic': dict(spin=1.3, spread=135, damping=7.5, frequency=17, drop=155, stretch=.44),
}
FAMILIES = {
    'assembly': {'name':'Radial assembly','wordmark':'drop'},
    'orbit': {'name':'Orbital gather','wordmark':'orbit'},
    'pop': {'name':'Scale pop','wordmark':'pop'},
    'fold': {'name':'Planar fold','wordmark':'fold'},
    'glitch': {'name':'Deterministic jitter','wordmark':'glitch'},
    'wipe': {'name':'Directional matte','wordmark':'wipe'},
}
WORDMARKS=('drop','orbit','pop','fold','glitch','wipe')

def family(plan):return plan.get('family','assembly')
def wordmark(plan):return plan.get('wordmark') or FAMILIES[family(plan)]['wordmark']

def jitter(frame,seed):
    """A bounded integer hash, independent of global random state."""
    return (((frame*1103515245+seed*12345)&0x7fffffff)%2001)/1000-1

def back(u):
    u=clamp(u)-1
    return 1+2.2*u*u*u+1.2*u*u

def clamp(u):
    return max(0.0, min(1.0, u))

def smooth(u):
    u = clamp(u)
    return u*u*(3-2*u)

def local_file(root, relative):
    root = Path(root).resolve()
    path = (root/relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError('Project asset path escapes project directory')
    return path

def validate(plan):
    if plan.get('schema') != 1:
        raise ValueError('Expected plan schema 1')
    for key in ('width', 'height', 'fps'):
        if type(plan.get(key)) is not int or plan[key] <= 0:
            raise ValueError(f'{key} must be a positive integer')
    duration = plan.get('duration')
    if not isinstance(duration, (int, float)) or not math.isfinite(duration) or duration <= 0:
        raise ValueError('duration must be finite and positive')
    if abs(duration*plan['fps']-round(duration*plan['fps'])) > 1e-6:
        raise ValueError('duration must span an integer number of frames')
    if plan.get('profile') not in PROFILES:
        raise ValueError('Unknown profile')
    if family(plan) not in FAMILIES or wordmark(plan) not in WORDMARKS:
        raise ValueError('Unknown symbol or wordmark motion family')
    timing = plan['timing']
    if not (0 <= timing['gather_start'] < timing['gather_end'] <= timing['handoff'] <= timing['move_start'] < timing['move_end'] < duration):
        raise ValueError('Invalid phase order')
    names = set()
    roles = []
    for layer in plan['layers']:
        if layer['name'] in names:
            raise ValueError('Duplicate layer name')
        names.add(layer['name']); roles.append(layer['role'])
        if layer['role'] not in ('background', 'part', 'whole', 'letter'):
            raise ValueError('Unsupported layer role')
        if not (0 <= layer['start'] < layer['end'] <= duration):
            raise ValueError('Layer outside timeline')
        if len(layer['pivot']) != 2 or not all(math.isfinite(v) for v in layer['pivot']):
            raise ValueError('Invalid pivot')
        bounds=layer.get('bounds_x',[0,plan['width']])
        if len(bounds)!=2 or not all(math.isfinite(v) for v in bounds) or not 0<=bounds[0]<bounds[1]<=plan['width']:
            raise ValueError('Invalid horizontal reveal bounds')
        start, end = frame_range(plan, layer)
        if end <= start:
            raise ValueError('Layer shorter than one frame')
        if layer['role'] == 'part' and end != round(timing['handoff']*plan['fps'])+1:
            raise ValueError('Part must end at master handoff')
        if layer['role'] == 'whole' and start != round(timing['handoff']*plan['fps'])+1:
            raise ValueError('Whole master must start at handoff')
        if layer['role'] == 'letter' and layer['start'] < timing['move_end']:
            raise ValueError('Default recipe starts letters after symbol travel')
    if roles.count('whole') != 1 or 'part' not in roles:
        raise ValueError('Assembly recipe needs parts and exactly one whole master')
    return plan

def load_project(root):
    root = Path(root).resolve()
    plan = validate(json.loads((root/'plan.json').read_text(encoding='utf8')))
    for layer in plan['layers']:
        for key in ('svg', 'png'):
            local_file(root, layer[key])
    return plan

def frame_range(plan, layer):
    fps = plan['fps']
    return round(layer['start']*fps)+1, round(layer['end']*fps)+1

def pose(plan, layer, frame):
    """Return alpha, x/y pixels (down-positive), scale x/y, clockwise degrees."""
    fps=plan['fps']; t=(frame-1)/fps; timing=plan['timing']
    role=layer['role']; start,end=frame_range(plan,layer)
    if not start <= frame < end:
        return (0.,0.,0.,1.,1.,0.)
    if role == 'background':
        return (1.,0.,0.,1.,1.,0.)
    p=PROFILES[plan['profile']]; ratio=plan['width']/1920; kind=family(plan)
    if role in ('part','whole'):
        move=smooth((t-timing['move_start'])/(timing['move_end']-timing['move_start']))
        dx=(plan['width']/2-layer['pivot'][0])*(1-move)
        dy=0.; scale=1+.9*(1-move); rotation=0.; alpha=1.
        if role == 'part':
            u=clamp((t-timing['gather_start'])/(timing['gather_end']-timing['gather_start']))
            e=1-(1-u)**3; i=layer['part_index']
            if kind in ('assembly','orbit'):
                progress=smooth(u) if kind=='orbit' else e
                angle=i*2*math.pi/3+(2*math.pi if kind=='orbit' else 1.8)*(1-progress)
                radius=p['spread']*ratio*(1-progress)
                dx+=radius*math.cos(angle);dy+=radius*math.sin(angle)
                scale*=.4+.6*progress
                rotation=[-110,135,-150][i%3]*p['spin']*(1-progress)
            elif kind=='pop':scale*=.22+.78*back(u)
            elif kind=='fold':
                dx+=(i-1)*80*ratio*(1-e);rotation=(i-1)*45*(1-e)
                alpha=clamp((t-timing['gather_start'])/.09)
                return (alpha,dx,dy,scale*(.05+.95*e),scale*(1.25-.25*e),rotation)
            elif kind=='glitch' and u<1:
                envelope=(1-u)**2
                dx+=50*ratio*envelope*jitter(frame,i+1)
                dy+=16*ratio*envelope*jitter(frame,i+17)
                rotation=7*envelope*jitter(frame,i+41)
            alpha=clamp((t-timing['gather_start'])/.09)
        return (alpha,dx,dy,scale,scale,rotation)
    elapsed=(frame-start)/fps
    if elapsed >= .85:
        return (1.,0.,0.,1.,1.,0.)
    mode=wordmark(plan);u=clamp(elapsed/.65);e=1-(1-u)**3
    if mode=='wipe':return (clamp(elapsed/.05),0.,0.,1.,1.,0.)
    if mode=='pop':
        sc=.35+.65*back(clamp(elapsed/.55))
        return (clamp(elapsed/.075),0.,0.,sc,sc,0.)
    if mode=='fold':return (clamp(elapsed/.075),0.,18*ratio*(1-e),.06+.94*e,1+.12*(1-e),-12*(1-e))
    if mode=='orbit':return (clamp(elapsed/.075),100*ratio*(1-e),-85*ratio*math.sin(math.pi*u)*(1-e),1.,1.,-10*(1-e))
    if mode=='glitch':
        v=clamp(elapsed/.4);envelope=(1-v)**2
        return (clamp(elapsed/.055),28*ratio*envelope*jitter(frame,3),8*ratio*envelope*jitter(frame,31),1.,1.,0.)
    d=math.exp(-p['damping']*elapsed); wave=math.cos(p['frequency']*elapsed)
    return (clamp(elapsed/.075),0.,-p['drop']*ratio*d*wave,
            1-p['stretch']*.4*d*wave,1+p['stretch']*d*wave,1.2*d*wave)

def right_crop(plan,layer,frame):
    """Pixels removed from the untransformed full-canvas asset's right edge."""
    role=layer['role'];fps=plan['fps'];t=(frame-1)/fps
    if role=='part' and family(plan)=='wipe':
        timing=plan['timing'];u=clamp((t-timing['gather_start'])/(timing['gather_end']-timing['gather_start']))
    elif role=='letter' and wordmark(plan)=='wipe':
        start,_=frame_range(plan,layer);u=clamp((frame-start)/fps/.42)
    else:return 0
    if u>=1:return 0
    left,right=layer.get('bounds_x',[0,plan['width']])
    return max(0,min(plan['width'],round(plan['width']-(left+(right-left)*smooth(u)))))

def sample(plan):
    result=[]
    for layer in plan['layers']:
        start,end=frame_range(plan,layer)
        item=dict(name=layer['name'],png=layer['png'],pivot=layer['pivot'],
                           start_frame=start,end_frame=end,
                           samples=[[frame,*pose(plan,layer,frame)] for frame in range(start,end)])
        crops=[[frame,right_crop(plan,layer,frame)] for frame in range(start,end)]
        if any(row[1] for row in crops):item['crop_samples']=crops
        result.append(item)
    return dict(width=plan['width'],height=plan['height'],fps=plan['fps'],
                duration=plan['duration'],transparent=plan.get('transparent',False),layers=result)
