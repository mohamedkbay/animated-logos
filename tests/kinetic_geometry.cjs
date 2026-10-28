'use strict';
const assert=require('node:assert/strict');
const m=require('../skills/animated-logos/assets/kinetic-type/engine.js');
for(let scene=0;scene<6;scene++)assert.equal(m.stateAt(scene*3).scene,scene);
assert.equal(m.stateAt(-1).time,0);assert.equal(m.stateAt(99).scene,5);
for(let i=0;i<180;i++){const t=i/10;assert.deepEqual(m.stateAt(t),m.stateAt(t));}
let previous=-1;
for(let i=0;i<=300;i++){const v=m.countAt(i/100,1280);assert(v>=previous&&v>=0&&v<=1280);previous=v;}
assert.equal(m.countAt(0,1280),0);assert.equal(m.countAt(3,1280),1280);
for(const value of [1,19,1280,9999])for(const weight of [1,10,100,1000])assert.equal(m.digitAt(value,weight).fraction,0);
assert.deepEqual(m.digitAt(9.5,10),{number:0,fraction:.5});
assert.deepEqual(m.digitAt(10,10),{number:1,fraction:0});
assert.equal(m.stretchAt(0),0);assert.equal(m.stretchAt(3),0);assert.equal(m.stretchAt(1.4),96);
assert.equal(m.projection(500,500),null);assert.equal(m.projection(400,500),null);assert.equal(m.projection(524,500),null);
assert(m.projection(700,500)>m.projection(900,500));
function cross(a,b,c){return(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);}
function intersects(a,b,c,d){return cross(a,b,c)*cross(a,b,d)<-1e-10&&cross(c,d,a)*cross(c,d,b)<-1e-10;}
for(let frame=0;frame<=90;frame++){
 const p=m.morphAt(frame/30);assert.equal(p.length,80);assert(p.every(x=>x.every(Number.isFinite)));assert(Math.abs(m.area(p))>.2);
 for(let i=0;i<p.length;i++)for(let j=i+2;j<p.length;j++){
  if(i===0&&j===p.length-1)continue;
  assert(!intersects(p[i],p[(i+1)%p.length],p[j],p[(j+1)%p.length]),`Contour crossing at frame ${frame}, edges ${i}/${j}`);
 }
}
assert.deepEqual(m.morphAt(0),m.shapes[0]);assert.deepEqual(m.morphAt(3),m.shapes[3]);
assert.throws(()=>m.resample([[0,0],[0,0]]),/nonzero perimeter/);
console.log('Kinetic state, bounded counter, Arabic excursion, depth projection and noncrossing morph checks passed.');
assert.equal(m.resolvePlan({target:42}).target,42);
for(const plan of [{duration:30},{target:10000},{hook:['one']},{cutWords:['one','two']},{accent:'red'},{maxExtension:-1},{joinX:NaN},{unsupported:true}])assert.throws(()=>m.resolvePlan(plan));
