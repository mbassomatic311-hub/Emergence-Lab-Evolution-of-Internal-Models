/* Emergence Lab Experiment 04: evolutionary competition between perceptual interfaces. */
(function(root,factory){const x=factory(); if(typeof module==='object'&&module.exports)module.exports=x; root.EvoPerception=x;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const NAMES=['Icons','Detailed','Adaptive','Blind'];
const COL=['#68e0c2','#9a9eff','#f4c571','#88929f'];
function mulberry32(seed){let a=seed>>>0;return function(){a|=0;a=(a+0x6D2B79F5)|0;let t=Math.imul(a^(a>>>15),1|a);t=(t+Math.imul(t^(t>>>7),61|t))^t;return ((t^(t>>>14))>>>0)/4294967296;};}
function randn(rng){return (rng()+rng()+rng()+rng()+rng()+rng()-3)*1.4142135623730951;} // Irwin-Hall approx unit sigma
function clamp(x,min,max){return Math.max(min,Math.min(max,x));}
function normOptions(opts={}){return {seed:Math.round(opts.seed??42), size:Math.round(opts.size??160), rounds:Math.round(opts.rounds??10), generations:Math.round(opts.generations??160), scenario:opts.scenario??'shock', fullCost:Number(opts.fullCost??0.19), iconCost:Number(opts.iconCost??0.024), hybridOverhead:Number(opts.hybridOverhead??0.033), mutation:Number(opts.mutation??0.018), strength:Number(opts.strength??5.0), sensorNoise:Number(opts.sensorNoise??0.085)};}
function world(rng,lambda){return {lambda,choices:Array.from({length:4},()=>({f:rng(),h:rng()}))};}
function regime(opts,g,rng){if(opts.scenario==='stable')return 1.0;if(opts.scenario==='variable'||(opts.scenario==='shock'&&g>=Math.floor(opts.generations/2))){return rng()<.5?0.35:3.25;}return 1.0;}
function observe(p,strategy,lambda,rng,opts){let alt=strategy===2?(lambda>=1.5?1:0):strategy;
  if(alt===3)return {choice:Math.floor(rng()*p.length), cost:0};
  let choice=0,best=-Infinity;
  for(let i=0;i<p.length;i++){
    let score;
    if(alt===0){ const raw=p[i].f-p[i].h+randn(rng)*opts.sensorNoise; score=clamp(Math.round(raw*2),-2,2); }
    else{ const f=clamp(p[i].f+randn(rng)*opts.sensorNoise*1.5,0,1),h=clamp(p[i].h+randn(rng)*opts.sensorNoise*1.5,0,1);score=2*f-lambda*h; }
    // Break ties randomly without favoring the first candidate.
    score+=rng()*1e-5;
    if(score>best){best=score;choice=i;}
  }
  let cost=(alt===0?opts.iconCost:opts.fullCost)+(strategy===2?opts.hybridOverhead:0);
  return {choice,cost};
}
function trial(w,strategy,rng,opts){const o=observe(w.choices,strategy,w.lambda,rng,opts);const p=w.choices[o.choice];const gross=2*p.f-w.lambda*p.h;return {net:gross-o.cost,gross,cost:o.cost,choice:o.choice};}
function initialize(opts){const p=normOptions(opts);const rng=mulberry32(p.seed);const population=Array.from({length:p.size},(_,i)=>i%4); // exactly balanced, shuffled
for(let i=population.length-1;i>0;i--){let j=Math.floor(rng()*(i+1));[population[i],population[j]]=[population[j],population[i]];}
return {options:p,rng,population,g:0,traces:[],lastWorld:null,lastScore:null,fitnessHistory:[]};}
function step(state){const {rng,options:opts}=state,g=state.g;const worlds=Array.from({length:opts.rounds},()=>world(rng,regime(opts,g,rng)));const agents=state.population;const scores=new Array(agents.length);let totals=[0,0,0,0],counts=[0,0,0,0],totalCost=[0,0,0,0];
for(let i=0;i<agents.length;i++){
 const s=agents[i];let x=0,c=0;for(const w of worlds){const r=trial(w,s,rng,opts);x+=r.net;c+=r.cost;}
 scores[i]=x/opts.rounds;totals[s]+=scores[i];totalCost[s]+=c/opts.rounds;counts[s]++;
}
const best=Math.max(...scores);
const weights=scores.map(v=>Math.exp(clamp(opts.strength*(v-best),-45,0))+.000001);
let sum=0;const cdf=weights.map(w=>sum+=w);
const next=[];
for(let i=0;i<agents.length;i++){
  const target=rng()*sum;let lo=0,hi=cdf.length-1;while(lo<hi){let mid=(lo+hi)>>1;if(cdf[mid]<target)lo=mid+1;else hi=mid;}
  let s=agents[lo];if(rng()<opts.mutation)s=Math.floor(rng()*4);next.push(s);
}
const avg=totals.map((v,i)=>counts[i]?v/counts[i]:null);const costs=totalCost.map((v,i)=>counts[i]?v/counts[i]:null);
const frequencies=[0,0,0,0];for(let i=0;i<next.length;i++)frequencies[next[i]]++;
const trace={generation:g+1,phase:(opts.scenario==='shock'&&g>=Math.floor(opts.generations/2))?'changed':opts.scenario==='stable'?'stable':opts.scenario==='shock'?'stable':'variable',frequencies:frequencies.map(v=>v/next.length),avg,mean: scores.reduce((a,b)=>a+b,0)/scores.length, costs, lambda:worlds[0].lambda};
state.lastWorld=worlds[0];state.lastScore={counts,avg};state.population=next;state.traces.push(trace);state.g++;return trace;
}
function run(opts){const state=initialize(opts);while(state.g<state.options.generations)step(state);return state;}
function benchmark(opts,seed=7919,examples=4000){const o=normOptions(opts),rng=mulberry32(seed);let sum=[0,0,0,0],correct=[0,0,0,0],cost=[0,0,0,0];let total=0;
  for(let j=0;j<examples;j++) {const lambda=regime(o, o.scenario==='shock'?(j<examples/2?0:o.generations-1):0,rng);const w=world(rng,lambda);const optimal=Math.max(...w.choices.map(v=>2*v.f-w.lambda*v.h));for(let a=0;a<4;a++){const t=trial(w,a,rng,o);sum[a]+=t.net;cost[a]+=t.cost;const actual=2*w.choices[t.choice].f-w.lambda*w.choices[t.choice].h;if(optimal-actual<0.000001)correct[a]++;}total++; }
return {mean:sum.map(x=>x/total),optimal:correct.map(x=>x/total),cost:cost.map(x=>x/total),n:total};
}
function inspectWorld(seed=42){const rng=mulberry32(seed);return Array.from({length:100},(_,i)=>({x:i%10,y:Math.floor(i/10),f:rng(),h:rng()}));}
function icon(f,h){return clamp(Math.round((f-h)*2),-2,2);}
return {NAMES,COL,mulberry32,regime,world,observe,trial,initialize,step,run,benchmark,inspectWorld,icon,normOptions};
});
