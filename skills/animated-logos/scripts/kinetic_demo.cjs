#!/usr/bin/env node
'use strict';
/* Render the original Arabic kinetic study with existing local dependencies. */
const fs=require('node:fs/promises'),path=require('node:path'),{spawn,spawnSync}=require('node:child_process');
const {once}=require('node:events');
const template=path.resolve(__dirname,'../assets/kinetic-type');
const help=`Usage: kinetic_demo.cjs COMMAND --project PATH [options]
Commands:
  init    Create a fresh study: --font FILE --font-license FILE [--plan JSON]
  check   Check the actual font, deterministic frames and endpoint restoration
  render  Encode the study: [--output FILE] [--width 540] [--fps 30] [--ffmpeg PATH] [--ffprobe PATH]
Runtime options for check/render: --browser PATH --playwright-module MODULE_OR_PATH
Existing output/project versions are preserved. Use preflight.py --pipeline canvas first.
The built-in study is six 3-second scenes, portrait, silent. Read references/agent-workflow.md.
`;
const allowed={init:['project','font','font-license','plan'],check:['project','browser','playwright-module','width','fps'],render:['project','browser','playwright-module','width','fps','ffmpeg','ffprobe','output']};
function options(args,command){const out={};for(let i=0;i<args.length;i+=2){const key=args[i].slice(2);if(!args[i].startsWith('--')||!allowed[command].includes(key))throw Error('Unknown option '+args[i]+' for '+command+'; run --help');if(args[i+1]===undefined||args[i+1].startsWith('--'))throw Error('Missing value for '+args[i]);if(key in out)throw Error('Duplicate option '+args[i]);out[key]=args[i+1];}return out;}
async function main(){
 if(process.argv.length===2||process.argv.includes('--help')){console.log(help);return;}
 const command=process.argv[2];if(!allowed[command])throw Error('Unknown command; run --help');
 const o=options(process.argv.slice(3),command);if(!o.project)throw Error('--project PATH is required; run --help');
 const project=path.resolve(o.project);
 if(command==='init'){
  if(!o.font||!o['font-license'])throw Error('init requires --font and --font-license for redistributable Arabic shaping');
  try{await fs.access(project);throw Error('Choose a fresh project directory');}catch(e){if(e.code!=='ENOENT')throw e;}
  const ext=path.extname(o.font).toLowerCase();if(!['.woff2','.woff','.ttf','.otf'].includes(ext))throw Error('Use a local WOFF2, WOFF, TTF or OTF font');
  const plan=o.plan?JSON.parse(await fs.readFile(o.plan,'utf8')):{};
  require(path.join(template,'engine.js')).resolvePlan(plan);
  await fs.access(o.font);await fs.access(o['font-license']);
  await fs.mkdir(project,{recursive:true});
  await fs.copyFile(o.font,path.join(project,'font'+ext));await fs.copyFile(o['font-license'],path.join(project,'FONT-LICENSE.txt'));
  await fs.copyFile(path.join(template,'engine.js'),path.join(project,'engine.js'));
  const html=(await fs.readFile(path.join(template,'index.html'),'utf8')).replace('__FONT_FILE__','font'+ext);await fs.writeFile(path.join(project,'index.html'),html);
  await fs.writeFile(path.join(project,'plan.js'),'window.KINETIC_PLAN = '+JSON.stringify(plan,null,2)+';\n');
  console.log('Created portable original study:',project);return;
 }
 const pw=o['playwright-module']||'playwright';const {chromium}=require(pw);
 const width=Number(o.width||540),height=Math.round(width*16/9/2)*2;let fps=Number(o.fps||30);
 if(!Number.isInteger(width)||width<180||width>2160||width%2||!Number.isInteger(fps)||fps<1||fps>60)throw Error('Choose an even width from 180 to 2160 and an integer fps from 1 to 60');
 const browser=await chromium.launch({headless:true,...(o.browser?{executablePath:o.browser}:{})});let encoder;
 try{
  const page=await browser.newPage({viewport:{width,height},deviceScaleFactor:1});
  await page.route(/^https?:\/\//,r=>r.abort());
  await page.goto(require('node:url').pathToFileURL(path.join(project,'index.html')).href);
  await page.evaluate(async({width,height})=>{const c=document.getElementById('stage');c.width=width;c.height=height;await window.motionReady;window.motionRenderer=KineticType.createRenderer(c,window.KINETIC_PLAN);window.renderAt=t=>window.motionRenderer.draw(t);},{width,height});
  const study=await page.evaluate(()=>({plan:motionRenderer.plan,wordBox:motionRenderer.wordBox}));
  if(!o.fps)fps=study.plan.fps;
  if(command==='check'){
   const check=await page.evaluate(()=>{
    const c=document.getElementById('stage'),ctx=c.getContext('2d');
    function pixels(t){renderAt(t);return Array.from(ctx.getImageData(0,0,c.width,c.height).data);}
    const first=pixels(7.3);renderAt(2);renderAt(15.1);const again=pixels(7.3);if(first.some((v,i)=>v!==again[i]))throw Error('Random seeks changed a deterministic frame');
    const end=renderAt(18);if(end.count!==motionRenderer.plan.target)throw Error('Counter endpoint mismatch');
    // The zero-extension render is a direct master draw, pixel-identical before/after extension.
    function stretch(e){ctx.setTransform(1,0,0,1,0,0);ctx.fillStyle=motionRenderer.plan.paper;ctx.fillRect(0,0,c.width,c.height);ctx.scale(c.width/540,c.width/540);motionRenderer.drawStretch(e);return Array.from(ctx.getImageData(0,0,c.width,c.height).data);}
    const master=stretch(0);stretch(96);const restored=stretch(0);if(master.some((v,i)=>v!==restored[i]))throw Error('Arabic master was not restored');
    renderAt(0);return {deterministicSeek:true,masterRestored:true,counterEndpoint:end.count,connector:motionRenderer.wordBox.joinX,connectorFound:true};
   });
   await fs.writeFile(path.join(project,'browser-check.json'),JSON.stringify({...check,width,height,fps},null,2));console.log(JSON.stringify(check));return;
  }
  const output=path.resolve(o.output||path.join(project,'preview.mp4'));
  try{await fs.access(output);throw Error('Output exists; choose a new version');}catch(e){if(e.code!=='ENOENT')throw e;}
  const frames=Math.round(study.plan.duration*fps);
  await fs.mkdir(path.dirname(output),{recursive:true});
  const probe=spawnSync(o.ffprobe||'ffprobe',['-version'],{encoding:'utf8'});if(probe.status!==0)throw Error('FFprobe is unavailable; pass --ffprobe for an installed executable');
  encoder=spawn(o.ffmpeg||'ffmpeg',['-hide_banner','-loglevel','error','-f','image2pipe','-vcodec','png','-framerate',String(fps),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','18','-threads','2','-pix_fmt','yuv420p','-frames:v',String(frames),'-movflags','+faststart',output],{stdio:['pipe','inherit','inherit']});
  let encodeError;encoder.on('error',e=>{encodeError=e;});encoder.stdin.on('error',e=>{encodeError=e;});
  const closed=new Promise(resolve=>encoder.once('close',resolve));
  await once(encoder,'spawn');
  await fs.mkdir(path.join(project,'review'),{recursive:true});
  for(let frame=0;frame<frames;frame++){
   if(encodeError)throw encodeError;
   await page.evaluate(t=>renderAt(t),frame/fps);
   const data=Buffer.from(await page.evaluate(()=>document.getElementById('stage').toDataURL('image/png').split(',')[1]),'base64');
   if(!encoder.stdin.write(data))await once(encoder.stdin,'drain');
   if(frame%Math.round(fps/2)===0||frame===frames-1)await fs.writeFile(path.join(project,'review',String(frame).padStart(5,'0')+'.png'),data);
   if(frame%fps===0)process.stdout.write(`Rendered ${frame}/${frames}\n`);
  }
  encoder.stdin.end();const code=await closed;if(code!==0)throw Error('FFmpeg exited '+code);
  const checked=spawnSync(o.ffprobe||'ffprobe',['-v','error','-show_streams','-show_format','-of','json',output],{encoding:'utf8'});
  if(checked.status!==0)throw Error('Encoded video could not be inspected by FFprobe');
  const info=JSON.parse(checked.stdout),video=info.streams.find(v=>v.codec_type==='video');
  if(!video||video.width!==width||video.height!==height||Number(video.nb_frames)!==frames||Math.abs(Number(info.format.duration)-frames/fps)>1/fps)throw Error('Encoded media does not match the requested frame contract');
  await fs.writeFile(path.join(project,'render-report.json'),JSON.stringify({width,height,fps,frames,duration:frames/fps,audio:false,verifiedMedia:true,engine:'Canvas2D; absolute-time sampled',referenceMediaBundled:false},null,2));console.log('Rendered:',output);
 }finally{if(encoder&&encoder.exitCode===null)encoder.kill('SIGTERM');await browser.close();}
}
if(require.main===module)main().catch(e=>{console.error(e.message);process.exitCode=1;});
module.exports={options};
