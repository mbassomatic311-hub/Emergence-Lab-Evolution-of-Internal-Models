const fs=require('fs');
const {EmergenceWorld}=require('./exp03_engine.js');
const seeds=Array.from({length:20},(_,i)=>(i+1)*777);
const modes=['evolve','locked','scrambled','no_loop','nonheritable'];
const results=[];
for(let mode of modes){
 for(let seed of seeds){
  const w=new EmergenceWorld(seed,mode).run(400);
  const h=w.history;
  let firstComplete=h.find(x=>x.complete>0)?.gen??null;
  let firstMajority=h.find(x=>x.complete>.5)?.gen??null;
  let first90=h.find(x=>x.complete>=.9)?.gen??null;
  let late=h.slice(-40).reduce((s,x)=>s+x.accuracy,0)/40;
  results.push({seed,mode,lateAccuracy:late,firstComplete,firstMajority,first90,finalComplete:h.at(-1).complete,finalUseful:h.at(-1).useful,finalAccuracy:h.at(-1).accuracy,history:h.filter(x=>x.gen%10===0)});
 }
}
fs.writeFileSync('/mnt/data/consciousness_lab/experiment_03_results.json',JSON.stringify(results,null,2));
const mean=a=>a.reduce((s,x)=>s+x,0)/a.length;
const sd=a=>Math.sqrt(a.reduce((s,x)=>s+(x-mean(a))**2,0)/(a.length-1));
for(const mode of modes){let r=results.filter(x=>x.mode===mode),arr=r.map(x=>x.lateAccuracy);
 console.log(`${mode} | mean accuracy ${(mean(arr)*100).toFixed(2)}% | sd ${(sd(arr)*100).toFixed(2)}pp | complete ${(mean(r.map(x=>x.finalComplete))*100).toFixed(2)}% | >50% circuit ${r.filter(x=>x.firstMajority!=null).length}/20 | first majority median ${r.filter(x=>x.firstMajority!=null).map(x=>x.firstMajority).sort((a,b)=>a-b)[9]??'none'}`);
}
let ev=results.filter(x=>x.mode==='evolve');console.log('EVOLVE: first complete median',ev.map(x=>x.firstComplete).sort((a,b)=>a-b)[9],'first90 worlds',ev.filter(x=>x.first90!==null).length);
