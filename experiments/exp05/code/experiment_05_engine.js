/* Emergence Lab 05 — evolvable instrument use. Standalone JS, UMD exported. */
(function(root,factory){const o=factory();if(typeof module==='object'&&module.exports)module.exports=o;root.Exp05=o;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const KEYS=['safe','ambiguous','danger'];
function rng32(seed){let a=seed>>>0;return function(){a|=0;a=(a+0x6D2B79F5)|0;let t=Math.imul(a^(a>>>15),1|a);t=(t+Math.imul(t^(t>>>7),61|t))^t;return ((t^(t>>>14))>>>0)/4294967296;};}
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
function normal(r){return (r()+r()+r()+r()+r()+r()-3)*1.41421356237;}
function sigmoid(x){return x>18?1:x< -18?0:1/(1+Math.exp(-x));}
function opts(v={}){return {seed:Math.floor(v.seed??41),n:Math.floor(v.n??200),generations:Math.floor(v.generations??240),rounds:Math.floor(v.rounds??24),measurementCost:+(v.measurementCost??.19),hardwareCost:+(v.hardwareCost??.026),accuracy:+(v.accuracy??.92),scenario:v.scenario??'shift',control:v.control??'truthful',selection:+(v.selection??3.4),mutation:+(v.mutation??.65)};}
function gene(r){return {hardware:0,policy:[r(),r(),r()],bias:[r()*4-2,r()*4-2,r()*4-2],weight:r()*7-3.5};}
function clone(g){return {hardware:g.hardware,policy:g.policy.slice(),bias:g.bias.slice(),weight:g.weight};}
function mutate(g,r,o){const h=clone(g);if(o.control!=='disabled'&&r()<.012)h.hardware=1-h.hardware;
 if(o.control==='disabled')h.hardware=0;
 // One of seven continuous decision parameters changes; scale set by mutation input.
 if(r()<.75){const i=Math.floor(r()*7);if(i<3)h.policy[i]=clamp(h.policy[i]+normal(r)*.23*o.mutation,0,1);else if(i<6)h.bias[i-3]=clamp(h.bias[i-3]+normal(r)*.8*o.mutation,-7,7);else h.weight=clamp(h.weight+normal(r)*1.0*o.mutation,-8,8);}
 return h;}
function sampleEvent(r,changed=false){const u=r(),idx=u<.30?0:u<.70?1:2;let p=changed?[.54,.5,.46][idx]:[.92,.5,.08][idx];return {idx, safe:r()<p};}
function evaluate(g,e,r,o){let probe=false,measurement=0,cost=(g.hardware?o.hardwareCost:0);
 if(g.hardware&&o.control!=='disabled'&&r()<g.policy[e.idx]){probe=true;cost+=o.measurementCost;
   const valid=o.control==='shuffled'?r()<.5:(r()<o.accuracy?e.safe:!e.safe);
   measurement=valid?1:-1;
 }
 let p=sigmoid(g.bias[e.idx]+(probe?g.weight*measurement:0));const enter=r()<p;
 const gross=enter?(e.safe?2:-3):0;
 return {net:gross-cost,quality:(enter===e.safe?1:0),probe:(probe?1:0),enter:(enter?1:0)};
}
function init(v){const o=opts(v),r=rng32(o.seed),population=Array.from({length:o.n},()=>gene(r));return {options:o,r,population,generation:0,trace:[],last:null};}
function tick(s){const o=s.options,r=s.r,g=s.generation,changed=o.scenario==='shift'&&g>=Math.floor(o.generations/2);
 const events=Array.from({length:o.rounds},()=>sampleEvent(r,changed));let sum=0,q=0,probes=0,agentFitness=[];
 for(const agent of s.population){let payoff=0,acc=0,nProbe=0;for(const e of events){const result=evaluate(agent,e,r,o);payoff+=result.net;acc+=result.quality;nProbe+=result.probe;}
 const score=payoff/o.rounds;agentFitness.push(score);sum+=score;q+=acc/o.rounds;probes+=nProbe/o.rounds;
 }
 const max=Math.max(...agentFitness),w=agentFitness.map(v=>Math.exp(clamp(o.selection*(v-max),-38,0))+.0000001);let total=0;const cdf=w.map(v=>total+=v);
 const next=[];for(let i=0;i<o.n;i++){
  const target=r()*total;let a=0,b=o.n-1;while(a<b){const m=(a+b)>>1;if(cdf[m]<target)a=m+1;else b=m;}
  const parent=o.control==='noinherit'?gene(r):s.population[a];next.push(mutate(parent,r,o));
 }
 let withProbe=0,probNeutral=0,probGreen=0,probRed=0,wPositive=0;
 for(const a of next){if(a.hardware){withProbe++;probGreen+=a.policy[0];probNeutral+=a.policy[1];probRed+=a.policy[2];if(a.weight>0)wPositive++;}}
 const t={generation:g+1,phase:changed?'changed':'stable',payoff:sum/o.n,quality:q/o.n,probes:probes/o.n,hardware:withProbe/o.n,neutralUse:withProbe?probNeutral/withProbe:0,greenUse:withProbe?probGreen/withProbe:0,redUse:withProbe?probRed/withProbe:0,positive:withProbe?wPositive/withProbe:0};
 s.population=next;s.generation++;s.trace.push(t);s.last=t;return t;}
function run(v){const s=init(v);while(s.generation<s.options.generations)tick(s);return s;}
function examplePairs(seed=883){const r=rng32(seed),a=[],p=[.92,.5,.08];for(let i=0;i<15;i++){const idx=i%3;const safe=r()<p[idx];const sample=(r()<.92?safe:!safe);a.push({idx,safe,sample});}return a;}
return {KEYS,rng32,opts,gene,mutate,sampleEvent,evaluate,init,tick,run,examplePairs};
});
