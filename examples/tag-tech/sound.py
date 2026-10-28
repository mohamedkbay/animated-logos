"""Original deterministic sound design; Python standard library only."""
from pathlib import Path
import json,math,random,wave,array,sys
R=Path(__file__).resolve().parent;plan=json.loads((R/'plan.json').read_text());sr=48000;N=round(plan['duration']*sr);left=[0.0]*N;right=[0.0]*N;rng=random.Random(47023)
def env(t,d,attack=.01,release=.08):return min(1,t/attack)*min(1,max(0,(d-t)/release))
def add(data,time,gain,pan=0):
 start=round(time*sr);gl=math.sqrt((1-pan)/2)*gain;gr=math.sqrt((1+pan)/2)*gain
 for i,v in enumerate(data[:N-start]):left[start+i]+=v*gl;right[start+i]+=v*gr
def tone(freq,duration,kind):
 out=[]
 for i in range(round(duration*sr)):
  t=i/sr
  if kind=='glass':v=sum(a*math.sin(2*math.pi*freq*ratio*t)*math.exp(-t/decay) for ratio,a,decay in [(1,.8,.22),(2.758,.28,.09),(5.403,.1,.045)])
  elif kind=='resolve':v=math.sin(2*math.pi*freq*t)*math.exp(-t/.55)+.15*math.sin(2*math.pi*freq*2*t)*math.exp(-t/.22)
  else:v=(math.sin(2*math.pi*freq*t)+.2*math.sin(2*math.pi*freq*3.7*t))*math.exp(-t/.055)
  out.append(v*env(t,duration,.006,.1))
 return out
def air(duration):
 out=[];lp=0;previous=0
 for i in range(round(duration*sr)):
  t=i/sr;v=rng.uniform(-1,1);lp=.91*lp+.09*v;hp=lp-previous;previous=lp;out.append((lp*.65+hp*.45)*math.sin(math.pi*t/duration)**2)
 return out
for cue in plan['soundCues']:
 t=cue['frame']/plan['fps'];kind=cue['kind'];gain=cue['gain']
 if kind=='air':add(air(1.25),t,gain,-.12)
 elif kind=='glass':add(tone(cue['note'],.6,'glass'),t,gain,cue.get('pan',0))
 elif kind=='contact':add(tone(220,.24,'body'),t,gain,-.2)
 elif kind=='lock':add(tone(130,.32,'body'),t,gain);add(tone(1174.66,.25,'glass'),t,.06)
 elif kind=='tick':add(tone(980,.085,'body'),t,gain,.12)
 elif kind=='resolve':
  for j,note in enumerate([587.33,880,1174.66]):add(tone(note,1.55,'resolve'),t+j*.045,gain*.55,[-.24,0,.24][j])
peak=max(max(map(abs,left)),max(map(abs,right)));gain=.785/peak if peak else 1;pcm=array.array('h')
for l,r in zip(left,right):pcm.extend((round(max(-1,min(1,l*gain))*32767),round(max(-1,min(1,r*gain))*32767)))
if sys.byteorder!='little':pcm.byteswap()
with wave.open(str(R/'sound-design.wav'),'wb') as w:w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes(pcm.tobytes())
(R/'sound-design.json').write_text(json.dumps({'source':'Original procedural synthesis','seed':47023,'sampleRate':sr,'duration':N/sr,'channels':2,'peakBeforeEncoding':.785,'cueFrames':[c['frame']for c in plan['soundCues']],'referenceAudioUsed':False},indent=2)+'\n');print('Original 48 kHz stereo sound design created.')
