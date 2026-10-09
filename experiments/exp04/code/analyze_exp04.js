const fs=require('fs'),E=require('./experiment_04_engine.js');
const runs=24, gens=160;let all=[];
for(const scenario of ['stable','variable','shock']){
 const summaries=[],traces=[];
 for(let i=0;i<runs;i++) {const state=E.run({scenario,generations:gens,seed:1700+i,fullCost:0.1});summaries.push(state.traces.at(-1).frequencies);traces.push(state.traces.map(t=>t.frequencies));}
 const avg=(at)=>([0,1,2,3].map(j=>traces.reduce((sum,t)=>sum+t[at][j],0)/runs));
 const s={scenario,runs,generations:gens,final:avg(159),at40:avg(39),at80:avg(79),at120:avg(119),bench:E.benchmark({scenario,fullCost:.1},314159,12000)};
 console.log(JSON.stringify({scenario:s.scenario,final:s.final.map(x=>+x.toFixed(4)),at80:s.at80.map(x=>+x.toFixed(4)),benchNet:s.bench.mean.map(x=>+x.toFixed(4)),benchOptimal:s.bench.optimal.map(x=>+x.toFixed(3))}));all.push({summary:s,frequencies:traces});
}
fs.writeFileSync(__dirname+'/experiment_04_results.json',JSON.stringify(all));
