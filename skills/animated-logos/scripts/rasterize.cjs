#!/usr/bin/env node
// Uses an already installed Playwright package and browser; installs nothing.
const fs=require('fs'),path=require('path');
if(process.argv.includes('--help')){
 console.log('node rasterize.cjs PROJECT [--browser-executable CHROME_PATH]');process.exit(0);
}
function local(root,relative){
 const file=path.resolve(root,relative),rel=path.relative(root,file);
 if(rel.startsWith('..'+path.sep)||rel==='..'||path.isAbsolute(rel))throw Error('Asset escapes project');
 const real=fs.realpathSync(file),rr=path.relative(fs.realpathSync(root),real);
 if(rr.startsWith('..'+path.sep)||rr==='..'||path.isAbsolute(rr))throw Error('Asset symlink escapes project');
 return file;
}
async function main(){
 const root=path.resolve(process.argv[2]||'');
 if(!process.argv[2])throw Error('Supply PROJECT; use --help');
 const plan=JSON.parse(fs.readFileSync(path.join(root,'plan.json'),'utf8'));
 const {chromium}=require('playwright');
 const flag=process.argv.indexOf('--browser-executable');
 const candidates=[flag>=0?process.argv[flag+1]:null,process.env.CHROME_PATH,
 '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
 '/usr/bin/google-chrome','/usr/bin/chromium',chromium.executablePath()].filter(Boolean);
 const executablePath=candidates.find(p=>fs.existsSync(p));
 if(!executablePath)throw Error('No installed Chromium browser; provide --browser-executable');
 const jobs=plan.layers.map(l=>({svg:l.svg,png:l.png}));
 jobs.push({svg:plan.master_svg,png:plan.master_png});
 const seen=new Set();
 const browser=await chromium.launch({headless:true,executablePath});
 try{
  const context=await browser.newContext({viewport:{width:plan.width,height:plan.height},deviceScaleFactor:1,javaScriptEnabled:false});
  await context.route('**/*',route=>route.abort());
  const page=await context.newPage();
  for(const job of jobs){
   if(seen.has(job.png))continue;seen.add(job.png);
   const source=fs.readFileSync(local(root,job.svg),'utf8');
   if(/<\s*(script|foreignObject)\b|\bon\w+\s*=|<!ENTITY|javascript:/i.test(source))throw Error('Active SVG content is unsupported');
   if(/(?:href\s*=\s*["']\s*(?:https?:|file:)|url\(\s*["']?https?:)/i.test(source))throw Error('Embed external SVG resources before rasterizing');
   const output=path.resolve(root,job.png),rel=path.relative(root,output);
   if(rel.startsWith('..')||path.isAbsolute(rel))throw Error('Output escapes project');
   fs.mkdirSync(path.dirname(output),{recursive:true});
   // Existing output parents are checked too; prevent writes through external symlinks.
   local(root,path.relative(root,path.dirname(output)));
   await page.setContent('<html><head><style>html,body{margin:0;background:transparent}svg{display:block}</style></head><body>'+source+'</body></html>');
   await page.screenshot({path:output,omitBackground:true});
  }
  console.log(`Rasterized ${seen.size} SVG assets at ${plan.width}x${plan.height}`);
 }finally{await browser.close();}
}
main().catch(e=>{console.error(e.message);process.exit(1);});
