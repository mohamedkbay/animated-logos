/* Original motion study. Browser + Node, no framework or network dependency. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory();
  else root.KineticType = factory();
})(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';
  const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
  const mix = (a, b, p) => p === 0 ? a : p === 1 ? b : a + (b - a) * p;
  const ease = p => 1 - Math.pow(1 - clamp(p), 3);
  const smooth = p => { p = clamp(p); return p * p * (3 - 2 * p); };
  const defaults = {
    duration: 18, sceneDuration: 3, fps: 30, target: 1280,
    paper: '#efeee6', ink: '#101212', accent: '#f34325',
    hook: ['LET IDEAS', 'MOVE.'], cutWords: ['IDEA', 'MOVE', 'MAKE'],
    stretchWord: 'نـمدّ', maxExtension: 96,
    brand: 'NOVA', footer: 'ANIMATED LOGOS · ORIGINAL MOTION STUDY'
  };
  function resolvePlan(supplied={}) {
    if(!supplied||typeof supplied!=='object'||Array.isArray(supplied))throw Error('Plan must be a JSON object');
    const known=new Set([...Object.keys(defaults),'joinX']);
    for(const key of Object.keys(supplied))if(!known.has(key))throw Error('Unknown plan field: '+key);
    const plan={...defaults,...supplied};
    if(plan.duration!==18||plan.sceneDuration!==3)throw Error('The built-in study is six 3-second scenes; customize the engine for another timeline');
    for(const [field,length] of [['hook',2],['cutWords',3]])if(!Array.isArray(plan[field])||plan[field].length!==length||plan[field].some(v=>typeof v!=='string'||!v.trim()))throw Error(field+' must contain '+length+' nonempty strings');
    for(const field of ['stretchWord','brand','footer'])if(typeof plan[field]!=='string'||!plan[field].trim())throw Error(field+' must be a nonempty string');
    for(const field of ['paper','ink','accent'])if(!/^#[0-9a-f]{6}$/i.test(plan[field]))throw Error(field+' must use #RRGGBB');
    if(!Number.isInteger(plan.target)||plan.target<1||plan.target>9999)throw Error('Counter target must be an integer from 1 to 9999');
    if(!Number.isInteger(plan.fps)||plan.fps<1||plan.fps>60)throw Error('fps must be an integer from 1 to 60');
    if(!Number.isFinite(plan.maxExtension)||plan.maxExtension<0||plan.maxExtension>160)throw Error('maxExtension must be from 0 to 160 logical pixels');
    if(plan.joinX!==undefined&&(!Number.isFinite(plan.joinX)||plan.joinX<0))throw Error('joinX must be a nonnegative logical coordinate');
    return plan;
  }
  function stateAt(t, config = defaults) {
    const time = clamp(t, 0, config.duration);
    const scene = Math.min(5, Math.floor(time / config.sceneDuration));
    const local = clamp(time - scene * config.sceneDuration, 0, config.sceneDuration);
    return {time, scene, local, progress: local / config.sceneDuration};
  }
  function stretchAt(t, max = 96) {
    return max * (ease((t - .45) / .65) - ease((t - 1.75) / .65));
  }
  function countAt(t, target) { return target * ease((t - .32) / 1.85); }
  function digitAt(value, weight) {
    const number=Math.floor(value/weight)%10;
    const carry=weight===1 ? value%1 : clamp(value%weight-(weight-1));
    return {number, fraction:smooth(carry)};
  }
  function area(points) {
    return points.reduce((s, p, i) => { const q = points[(i + 1) % points.length]; return s + p[0] * q[1] - q[0] * p[1]; }, 0) / 2;
  }
  function resample(points, n = 80) {
    const lengths = points.map((p, i) => Math.hypot(p[0] - points[(i + 1) % points.length][0], p[1] - points[(i + 1) % points.length][1]));
    const perimeter = lengths.reduce((a, b) => a + b, 0);
    if (!(perimeter > 0)) throw new Error('A morph contour must have nonzero perimeter');
    let segment = 0, before = 0;
    return Array.from({length:n}, (_, i) => {
      const distance = i * perimeter / n;
      while (segment < points.length - 1 && before + lengths[segment] < distance) before += lengths[segment++];
      const p = points[segment], q = points[(segment + 1) % points.length];
      const u = (distance - before) / (lengths[segment] || 1);
      return [mix(p[0], q[0], u), mix(p[1], q[1], u)];
    });
  }
  function align(previous, next) {
    next = next.slice();
    if (Math.sign(area(previous)) !== Math.sign(area(next))) next.reverse();
    let best = 0, error = Infinity;
    for (let shift = 0; shift < next.length; shift++) {
      const e = previous.reduce((sum, p, i) => { const q = next[(i + shift) % next.length]; return sum + (p[0]-q[0])**2 + (p[1]-q[1])**2; }, 0);
      if (e < error) { error = e; best = shift; }
    }
    return next.map((_, i) => next[(i + best) % next.length]);
  }
  const circle = Array.from({length:160}, (_, i) => { const a = i * Math.PI / 80 - Math.PI / 2; return [Math.cos(a), Math.sin(a)]; });
  const phone = [];
  for (const [x,y,start] of [[.46,-.8,-Math.PI/2],[.46,.8,0],[-.46,.8,Math.PI/2],[-.46,-.8,Math.PI]]) {
    for (let i=0;i<20;i++) { const a=start+i/19*Math.PI/2; phone.push([x+.2*Math.cos(a),y+.2*Math.sin(a)]); }
  }
  const triangle = [[0,-1.05],[1,.78],[-1,.78]];
  const heart = Array.from({length:200}, (_,i) => {const t=i*Math.PI/100;return [16*Math.sin(t)**3/17,-(13*Math.cos(t)-5*Math.cos(2*t)-2*Math.cos(3*t)-Math.cos(4*t))/17];});
  const shapes = [circle,phone,triangle,heart].map(p=>resample(p));
  for(let i=1;i<shapes.length;i++) shapes[i]=align(shapes[i-1],shapes[i]);
  function morphAt(t) {
    const phase=clamp((t-.25)/.72,0,3);const index=Math.min(2,Math.floor(phase));const u=smooth(phase-index);
    return shapes[index].map((p,i)=>[mix(p[0],shapes[index+1][i][0],u),mix(p[1],shapes[index+1][i][1],u)]);
  }
  function projection(cameraZ, layerZ, focal = 310, near = 24) {
    const distance=cameraZ-layerZ;
    return distance<=near ? null : focal/distance;
  }
  function createRenderer(canvas, supplied = {}) {
    const plan = resolvePlan(supplied);
    const ctx=canvas.getContext('2d',{alpha:false,willReadFrequently:true}), scale=canvas.width/540;
    const font=(size,weight=700)=>`${weight} ${size}px MotionArabic`;
    function text(s,x,y,size=30,color=plan.ink,align='center') {
      ctx.font=font(size);ctx.textAlign=align;ctx.textBaseline='alphabetic';ctx.direction=/^[\x20-\x7e]+$/.test(s)?'ltr':'rtl';ctx.fillStyle=color;ctx.fillText(s,x,y);
    }
    function rounded(x,y,w,h,r,fill) {ctx.fillStyle=fill;ctx.beginPath();ctx.roundRect(x,y,w,h,r);ctx.fill();}
    function headline(s,y=155,color=plan.ink){ctx.font=font(28);const size=Math.min(28,28*448/Math.max(1,ctx.measureText(s).width));text(s,46,y,size,color,'left');}
    function background(dark=false){ctx.fillStyle=dark?plan.ink:plan.paper;ctx.fillRect(0,0,540,960);}
    function chrome(scene,dark) {
      const color=dark?plan.paper:plan.ink;
      for(let i=0;i<6;i++){ctx.fillStyle=i===scene?plan.accent:dark?'#555752':'#b9bdb5';ctx.fillRect(46+i*14,58,10,2);}
      text(`${String(scene+1).padStart(2,'0')} / ${['FOCUS','MATCH CUT','ARABIC JOIN','MORPH','DEPTH','COUNTER'][scene]}`,495,66,16,color,'right');
      ctx.save();ctx.font='10px monospace';ctx.direction='ltr';ctx.textAlign='left';ctx.fillStyle=dark?'#8a928a':'#747c74';ctx.fillText(plan.footer,46,916);ctx.restore();
    }
    // Shape the entire Arabic word first. Find a real thin baseline connector.
    const rasterScale=4, word=document.createElement('canvas');word.width=1800;word.height=620;
    const wc=word.getContext('2d',{willReadFrequently:true});wc.scale(rasterScale,rasterScale);wc.font=font(110);wc.direction='rtl';wc.textAlign='left';wc.textBaseline='alphabetic';wc.fillStyle=plan.ink;wc.fillText(plan.stretchWord,20,115);
    const data=wc.getImageData(0,0,word.width,word.height);let left=word.width,right=0,top=word.height,bottom=0;
    for(let y=0;y<word.height;y++)for(let x=0;x<word.width;x++)if(data.data[(y*word.width+x)*4+3]>128){left=Math.min(left,x);right=Math.max(right,x);top=Math.min(top,y);bottom=Math.max(bottom,y);}
    if(right<=left)throw new Error('Arabic text raster is empty; load the requested font before creating the renderer');
    let best=null;
    for(let x=Math.ceil(left+(right-left)*.18);x<right-(right-left)*.18;x++){
      let lo=word.height,hi=0,count=0;
      for(let y=top;y<=bottom;y++)if(data.data[(y*word.width+x)*4+3]>180){lo=Math.min(lo,y);hi=Math.max(hi,y);count++;}
      if(count>8 && hi-lo<76 && lo>280 && (best===null||count<best.count)) best={x,lo,hi,count};
    }
    if(supplied.joinX!==undefined){const x=Math.round(supplied.joinX*rasterScale);if(x<=left||x>=right)throw new Error('joinX must lie inside the shaped word');let lo=word.height,hi=0,count=0;for(let y=top;y<=bottom;y++)if(data.data[(y*word.width+x)*4+3]>180){lo=Math.min(lo,y);hi=Math.max(hi,y);count++;}if(count<8||hi-lo>76)throw new Error('joinX needs a thin solid baseline connector');best={x,lo,hi,count};}
    if(!best)throw new Error('No safe baseline connector found. Supply a measured joinX for a suitable connected word.');
    const wordBox={left,right,top,bottom,joinX:best.x,connectorTop:best.lo,connectorBottom:best.hi,width:(right-left+1)/rasterScale,height:(bottom-top+1)/rasterScale,rasterScale};
    function drawStretch(extension, baseline=515) {
      const e=Math.round(extension*rasterScale);const x=270-(wordBox.width+e/rasterScale)/2;const y=baseline-115;
      ctx.save();ctx.translate(x-left/rasterScale,y);ctx.scale(1/rasterScale,1/rasterScale);
      if(e===0)ctx.drawImage(word,0,0);
      else{
        ctx.drawImage(word,0,0,best.x,word.height,0,0,best.x,word.height);
        // Extend only the opaque baseline core, not faint neighboring glyph pixels.
        ctx.fillStyle=plan.ink;ctx.fillRect(best.x,best.lo,e+1,best.hi-best.lo+1);
        ctx.drawImage(word,best.x,0,word.width-best.x,word.height,best.x+e,0,word.width-best.x,word.height);
      }
      ctx.restore();
    }
    function draw(t) {
      const state=stateAt(t,plan), {scene,local}=state;
      ctx.setTransform(scale,0,0,scale,0,0);ctx.globalAlpha=1;ctx.globalCompositeOperation='source-over';
      const dark=scene===3||scene===5;background(dark);
      if(scene===0){
        const p=ease(local/.72), yy=mix(530,445,p), offset=mix(24,0,p);
        ctx.save();ctx.translate(0,offset);text(plan.hook[0],270,yy,55);rounded(67,yy+28,406,105,3,plan.accent);text(plan.hook[1],270,yy+105,72);ctx.restore();
        const start=Math.min(5,Math.floor(local/.16));
        for(let i=0;i<6;i++){ctx.globalAlpha=i<=start?1:0;rounded(420-i*67,690,54,75,5,i===0?plan.accent:plan.paper);ctx.strokeStyle=plan.ink;ctx.strokeRect(420-i*67,690,54,75);text(String(i+1).padStart(2,'0'),447-i*67,721,14);}
        ctx.globalAlpha=1;headline('Let the idea lead the motion.');
      }else if(scene===1){
        const index=Math.min(plan.cutWords.length-1,Math.floor(local/.76));
        ctx.fillStyle=plan.ink;ctx.fillRect(0,218,540,435);
        ctx.save();ctx.beginPath();ctx.rect(40,300,460,260);ctx.clip();text(plan.cutWords[index],270,505,112,plan.paper);ctx.restore();
        headline('New word. Same visual anchor.');
        ctx.fillStyle='#8e948d';ctx.fillRect(70,735,400,1);const px=70+400*clamp(local/3);ctx.fillStyle=plan.accent;ctx.fillRect(px,709,2,52);
        for(let i=0;i<3;i++)rounded(76+i*132,747,118,33,4,index===i?plan.accent:plan.ink);
      }else if(scene===2){
        headline('Extend the join. Preserve the glyphs.');const extension=stretchAt(local,plan.maxExtension);drawStretch(extension);
        if(extension>2){ctx.strokeStyle=plan.accent;ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(270-extension/2,582);ctx.lineTo(270+extension/2,582);ctx.moveTo(270-extension/2,575);ctx.lineTo(270-extension/2,589);ctx.moveTo(270+extension/2,575);ctx.lineTo(270+extension/2,589);ctx.stroke();text(`+${Math.round(extension)} px`,270,617,17,plan.accent);}
        text('Constant weight · Connected shaping',270,703,22,'#68756d');
      }else if(scene===3){
        headline('One contour. Four meanings.',155,plan.paper);const points=morphAt(local);ctx.fillStyle=plan.accent;ctx.beginPath();points.forEach((p,i)=>{if(i===0)ctx.moveTo(270+p[0]*104,493+p[1]*104);else ctx.lineTo(270+p[0]*104,493+p[1]*104);});ctx.closePath();ctx.fill();
        const labels=['Circle','Device','Direction','Like'];text(labels[Math.min(3,Math.floor(clamp((local-.25)/.72,0,3)))],270,702,24,plan.paper);
      }else if(scene===4){
        // Actual perspective projection with a near-plane cutoff.
        const cameraZ=mix(1050,85,smooth((local-.15)/2.4));
        for(const layer of [{z:0,color:plan.ink,hole:0},{z:270,color:plan.accent,hole:105},{z:560,color:plan.paper,hole:165}]){
          const s=projection(cameraZ,layer.z);if(s===null)continue;ctx.save();ctx.translate(270,500);ctx.scale(s,s);ctx.fillStyle=layer.color;ctx.beginPath();ctx.rect(-1200,-1800,2400,3600);if(layer.hole){ctx.moveTo(layer.hole,0);ctx.arc(0,0,layer.hole,0,Math.PI*2,true);}ctx.fill('evenodd');
          if(layer.z===0){ctx.fillStyle=plan.paper;ctx.beginPath();ctx.moveTo(0,-22);ctx.lineTo(22,0);ctx.lineTo(0,22);ctx.lineTo(-22,0);ctx.closePath();ctx.fill();text(plan.brand,0,60,23,plan.paper);}
          ctx.restore();
        }
        const white=cameraZ<590;headline('Camera through depth planes.',155,white?plan.paper:plan.ink);
        ctx.strokeStyle=white?plan.paper:plan.ink;ctx.lineWidth=1;for(const[x,y,dx,dy]of[[44,260,1,1],[496,260,-1,1],[44,760,1,-1],[496,760,-1,-1]]){ctx.beginPath();ctx.moveTo(x+24*dx,y);ctx.lineTo(x,y);ctx.lineTo(x,y+24*dy);ctx.stroke();}
      }else{
        headline('Time-driven digits.',155,plan.paper);const value=countAt(local,plan.target),digits=4;const step=83,total=digits*step;
        ctx.save();ctx.beginPath();ctx.rect(68,369,404,153);ctx.clip();
        for(let i=0;i<digits;i++){
          const weight=10**(digits-1-i),digit=digitAt(value,weight),number=digit.number,frac=digit.fraction;const x=270-total/2+step*(i+.5);
          text(String(number),x,492-frac*151,123,plan.paper);if(frac>0)text(String((number+1)%10),x,643-frac*151,123,plan.paper);
        }
        ctx.restore();text('One clock. An exact endpoint.',270,592,25,plan.paper);
        const progress=clamp(value/plan.target);for(let i=0;i<24;i++)rounded(63+i*17.5,678,13,27,2,i/24<progress?plan.accent:'#343b37');
        text(plan.brand,270,797,27,plan.paper);
      }
      chrome(scene,dark || (scene===4 && mix(1050,85,smooth((local-.15)/2.4))<590));
      return {...state, extension:scene===2?stretchAt(local,plan.maxExtension):0, count:scene===5?Math.round(countAt(local,plan.target)):null};
    }
    return {draw,plan,wordBox,drawStretch,wordCanvas:word};
  }
  return {defaults,resolvePlan,clamp,mix,ease,smooth,stateAt,stretchAt,countAt,digitAt,area,resample,align,morphAt,projection,shapes,createRenderer};
});
