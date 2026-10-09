const E=require('./experiment_05_engine.js'); const fs=require('fs');
const seeds=Array.from({length:24},(_,i)=>9101+i*97);const experiments={truthful:{control:'truthful',scenario:'shift'},shuffled:{control:'shuffled',scenario:'shift'},disabled:{control:'disabled',scenario:'shift'},expensive:{control:'truthful',measurementCost:1.3,scenario:'shift'},noinherit:{control:'noinherit',scenario:'shift'},stable:{control:'truthful',scenario:'stable'}};
const results={settings:{seeds,generations:240,rounds:24,n:200,measurementCost:.19,accuracy:.92},experiments:{}};
for(const [name,p] of Object.entries(experiments)){
 let summaries=[],series=[];
 for(const seed of seeds){const s=E.run({...p,seed});const tail=s.trace.slice(-30);const avg=(key,start)=>start.reduce((a,t)=>a+t[key],0)/start.length;
 const pre=s.trace.slice(85,120),post=s.trace.slice(140,175);
 summaries.push({seed,late_payoff:avg('payoff',tail),late_quality:avg('quality',tail),late_hardware:avg('hardware',tail),late_probes:avg('probes',tail),late_neutralUse:avg('neutralUse',tail),late_greenUse:avg('greenUse',tail),pre_quality:avg('quality',pre),post_quality:avg('quality',post),pre_hardware:avg('hardware',pre),post_hardware:avg('hardware',post)});
 series.push(s.trace);
 }
 const keys=Object.keys(summaries[0]);let avg={};for(const k of keys.slice(1))avg[k]=summaries.reduce((a,b)=>a+b[k],0)/summaries.length;
 results.experiments[name]={averages:avg,replicates:summaries,series:seeds.map((seed,i)=>({seed,trace:series[i]}))};
 console.log(name, Object.fromEntries(['late_payoff','late_quality','late_hardware','late_probes','late_neutralUse','late_greenUse','pre_quality','post_quality'].map(k=>[k,+avg[k].toFixed(3)])));
}
fs.writeFileSync('/mnt/data/consciousness_lab/experiment_05_results.json',JSON.stringify(results));
