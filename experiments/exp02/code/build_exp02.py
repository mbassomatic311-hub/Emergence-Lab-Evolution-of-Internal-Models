from pathlib import Path
p=Path('/mnt/data/consciousness_lab/experiment_02_prediction.html')
html=r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Emergence Lab — Experiment 02: Can prediction evolve?</title>
<style>
:root{color-scheme:dark;--bg:#09121b;--panel:#111f2d;--border:#314657;--fg:#e8f2f8;--muted:#a9bdc9;--mint:#7be2ca;--gold:#f6cc76;--coral:#ff8f8c;--blue:#8dbafc}*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 8% -2%,#204050 0,transparent 42%),var(--bg);color:var(--fg);font:14px/1.5 system-ui,-apple-system,Segoe UI,sans-serif}main{max-width:1260px;margin:auto;padding:24px}header{display:flex;gap:15px;justify-content:space-between;align-items:start;margin-bottom:18px}.over{color:var(--mint);letter-spacing:.14em;font-weight:800;font-size:12px;text-transform:uppercase}h1{font-size:clamp(28px,4.4vw,44px);letter-spacing:-.045em;line-height:1.1;margin:5px 0 8px}.lead{color:var(--muted);margin:0;max-width:780px}.tag{padding:7px 11px;border:1px solid var(--border);border-radius:999px;white-space:nowrap;font-size:12px;color:var(--muted)}.grid{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(320px,1fr);gap:16px}.panel{background:linear-gradient(145deg,#142638,#101c29);border:1px solid var(--border);border-radius:15px;padding:17px;box-shadow:0 12px 35px #0002}.panel h2{font-size:15px;letter-spacing:-.015em;margin:0 0 10px}.panel p{margin:6px 0 12px}.muted,.note{color:var(--muted)}.note{font-size:12px;line-height:1.6}.canvasFrame{background:#09151f;border:1px solid #294054;border-radius:12px;overflow:hidden}.canvasFrame canvas{display:block;width:100%;height:auto}.controls{display:flex;gap:7px;flex-wrap:wrap;margin:13px 0}.btn{border-radius:9px;border:1px solid #436074;background:#213748;color:var(--fg);font:600 13px system-ui;padding:10px 13px;cursor:pointer}.btn.primary{color:#082b29;background:var(--mint);border-color:var(--mint)}.btn:hover{filter:brightness(1.13)}.btn:focus-visible,select:focus-visible,input:focus-visible{outline:2px solid white;outline-offset:2px}.fields{display:flex;flex-wrap:wrap;gap:9px;margin:12px 0}label{font-size:12px;color:var(--muted);font-weight:650;display:grid;gap:5px;flex:1;min-width:125px}select,input{background:#0b1a26;color:var(--fg);border:1px solid #466072;padding:9px 10px;border-radius:8px;font:13px system-ui;width:100%}.kpis{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-bottom:13px}.kpi{background:#0b1b28;border:1px solid var(--border);padding:10px;border-radius:10px}.number{font-weight:800;font-variant-numeric:tabular-nums;font-size:28px;letter-spacing:-.035em}.kpi .note{margin-top:0}.chart{width:100%;height:170px;display:block}.legend{display:flex;gap:16px;flex-wrap:wrap;font-size:12px;color:var(--muted);margin:6px 0 12px}.dot{width:9px;height:9px;display:inline-block;border-radius:2px;margin-right:6px}.summary{border-top:1px solid var(--border);margin-top:16px;padding-top:12px}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:15px}.cards h3{font-size:13px;margin:0 0 6px}.cards p{color:var(--muted);font-size:12px;line-height:1.65;margin:0}#notice{min-height:18px;color:var(--mint);font-size:12px}table{border-collapse:collapse;width:100%;font-size:12px;margin:12px 0}th,td{text-align:left;padding:8px;border-bottom:1px solid #2e4251}th{color:var(--muted)}@media(max-width:910px){.grid{grid-template-columns:1fr}.cards{grid-template-columns:1fr}}@media(max-width:500px){main{padding:14px}.panel{padding:12px}.tag{display:none}.btn{flex:1}header{margin-bottom:14px}.number{font-size:24px}}
</style></head><body><main><header><div><div class="over">Consciousness research sandbox · Experiment 02</div><h1>Can prediction evolve?</h1><p class="lead">A population of 180 agents sees a brief warning signal. Three time steps later, when the signal is gone, each agent chooses one of two routes. Can natural selection favor a circuit that remembers the warning?</p></div><div class="tag">Behavior ≠ proof of experience</div></header>
<div class="grid"><section class="panel"><h2>The delayed-signal challenge</h2><div class="canvasFrame"><canvas id="world" width="720" height="430" role="img" aria-label="Two-lane survival experiment with hidden safety gate, warning cue, and an evolving population"></canvas></div>
<div class="legend"><span><i class="dot" style="background:var(--mint)"></i>Agents taking the safe route</span><span><i class="dot" style="background:var(--coral)"></i>Agents choosing danger</span><span><i class="dot" style="background:var(--gold)"></i>Earlier warning cue</span></div>
<div class="controls"><button class="btn primary" id="play">▶ Evolve</button><button class="btn" id="plus10">+10 generations</button><button class="btn" id="plus100">+100 generations</button><button class="btn" id="reset">↺ Reset</button></div>
<div class="fields"><label>Experimental condition<select id="mode"><option value="predict">Predictive cue + inherited memory</option><option value="blocked">Memory blocked at choice</option><option value="random">Warning unrelated to danger</option><option value="nonheritable">No inherited behavior</option></select></label><label>Random seed<input id="seed" type="number" value="42" min="1" max="2147483647"></label><label>Speed<select id="speed"><option value="1">1 generation/frame</option><option value="3" selected>3 generations/frame</option><option value="10">10 generations/frame</option></select></label></div>
<div id="notice" aria-live="polite"></div><p class="note">Each generation faces 5 independent route choices. The warning is visible only at the start; the safe route is chosen after a 3-step delay. Each agent has two heritable parameters: <b>memory retention</b> and <b>signal interpretation</b>. Agents with more correct choices have more descendants. Reproduction and mutation are part of the programmed world. This is evolutionary selection, not within-lifetime learning.</p>
</section><aside class="panel"><h2>Measurements</h2><div class="kpis"><div class="kpi"><div class="number" id="gen">0</div><div class="note">Generations elapsed</div></div><div class="kpi"><div class="number" id="acc">—</div><div class="note">Correct choices, last generation</div></div><div class="kpi"><div class="number" id="ret">—</div><div class="note">Average memory-retention gene</div></div><div class="kpi"><div class="number" id="dec">—</div><div class="note">Average cue-decoding gene</div></div></div>
<h2>Accuracy over evolutionary time</h2><canvas class="chart" id="accChart" width="440" height="174"></canvas><div class="legend"><span><i class="dot" style="background:var(--mint)"></i>Correct choices</span><span><i class="dot" style="background:#52697b"></i>50% chance baseline</span></div>
<h2>Genes over evolutionary time</h2><canvas class="chart" id="geneChart" width="440" height="174"></canvas><div class="legend"><span><i class="dot" style="background:var(--gold)"></i>Memory retention (0–1)</span><span><i class="dot" style="background:var(--blue)"></i>Decoder gene, normalized (−1 to +1)</span></div>
<div class="summary"><h2>Interpretation</h2><p class="note" id="interpret">Advance the simulation and compare all four experimental conditions using the same seed.</p></div></aside></div>
<div class="cards"><section class="panel"><h3>What is deliberately programmed</h3><p>Short-lived cues, delayed decisions, noisy internal memory, two mutable genes, reproduction weighted by performance, and a small cost for memory. The agents do not invent nervous systems.</p></section><section class="panel"><h3>What selection may discover</h3><p>When warnings predict later danger, offspring of agents with better retention and cue interpretation may become more common. Control conditions test whether that requires useful memory and heredity.</p></section><section class="panel"><h3>What this cannot tell us</h3><p>Whether agents have feelings, awareness, or a subjective point of view. Successful prediction is measurable behavior; consciousness remains a separate explanatory problem.</p></section></div>
</main><script>
'use strict';
class RNG {constructor(seed){this.s=(Number(seed)>>>0)||42;}next(){this.s=(Math.imul(1664525,this.s)+1013904223)>>>0;return this.s/4294967296;}int(n){return Math.floor(this.next()*n)}range(a,b){return a+(b-a)*this.next();}normal(){return (this.next()+this.next()+this.next()+this.next()+this.next()+this.next()-3)*0.40824829;}}
const POP=180,TRIALS=5,DELAY=3,clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
class PredictionWorld {
 constructor(seed=42,mode='predict'){this.seed=seed;this.mode=mode;this.rng=new RNG(seed);this.generation=0;this.population=Array.from({length:POP},()=>this.randomGenome());this.records=[];this.last=null;this.totalOffspring=0;this.record(0.5);}
 randomGenome(){return {r:this.rng.range(.05,.75),d:this.rng.range(-2,2)};}
 childGenome(parent){if(this.mode==='nonheritable')return this.randomGenome();let r=parent.r,d=parent.d;if(this.rng.next()<.25)r=clamp(r+this.rng.range(-.19,.19),0,1);if(this.rng.next()<.25)d=clamp(d+this.rng.range(-.50,.50),-3,3);return {r,d};}
 // One warning is observed, then removed. Agent's recurrent memory is noisy at each of three elapsed steps.
 choose(g,cue){let mem=cue;for(let i=0;i<DELAY;i++){mem=g.r*mem+.27*this.rng.normal();}if(this.mode==='blocked')mem=0;
  const p=1/(1+Math.exp(-2.4*g.d*mem));return this.rng.next()<p?1:-1;
 }
 tick(){this.generation++;const score=new Float64Array(POP);let correct=0,chosenLeft=0,chosenRight=0,lastCue=1,lastSafe=1,lastCorrect=0;
  for(let trial=0;trial<TRIALS;trial++){
   const cue=this.rng.next()<.5?-1:1;const safe=this.mode==='random'?(this.rng.next()<.5?-1:1):cue;let c=0;
   for(let i=0;i<POP;i++){const picked=this.choose(this.population[i],cue);if(picked===safe){score[i]++;correct++;c++;}if(trial===TRIALS-1){if(picked===1)chosenRight++;else chosenLeft++;}}
   lastCue=cue;lastSafe=safe;lastCorrect=c;
  }
  // Fitness reflects accumulated survival/reproduction over five decisions; each agent has an opportunity to reproduce.
  let total=0;const cumulative=new Float64Array(POP);for(let i=0;i<POP;i++){
   const g=this.population[i];const fitness=Math.exp(.72*(score[i]-TRIALS/2))*(1-.08*g.r*g.r);
   total+=fitness;cumulative[i]=total;
  }
  const old=this.population, next=[];
  for(let n=0;n<POP;n++){const q=this.rng.next()*total;let lo=0,hi=POP-1;while(lo<hi){const mid=(lo+hi)>>1;if(cumulative[mid]<q)lo=mid+1;else hi=mid;}next.push(this.childGenome(old[lo]));}
  this.population=next;this.totalOffspring+=POP;const accuracy=correct/(POP*TRIALS);this.last={cue:lastCue,safe:lastSafe,chosenLeft,chosenRight,correct:lastCorrect,accuracy};this.record(accuracy);return this;
 }
 record(accuracy){let r=0,d=0;for(const g of this.population){r+=g.r;d+=g.d;}this.records.push({g:this.generation,accuracy,r:r/POP,d:d/POP});if(this.records.length>1501)this.records.shift();}
 run(n){for(let i=0;i<n;i++)this.tick();return this;}
 stats(){let last=this.records[this.records.length-1],late=this.records.slice(-Math.min(30,this.generation));return {seed:this.seed,mode:this.mode,generations:this.generation,accuracy:last.accuracy,avgLast30:this.generation?late.reduce((a,b)=>a+b.accuracy,0)/late.length:null,meanRetention:last.r,meanDecoder:last.d,last:this.last,records:this.records};}
}
const worldCanvas=document.getElementById('world'), ctx=worldCanvas.getContext('2d');let w=new PredictionWorld(),playing=false,request=null;
function label(x,y,s,size=13,color='#e8f2f8',align='left'){ctx.fillStyle=color;ctx.font=`${size}px system-ui`;ctx.textAlign=align;ctx.fillText(s,x,y);ctx.textAlign='left';}
function box(x,y,ww,hh,fill,stroke='#39546a',rad=10){ctx.fillStyle=fill;ctx.strokeStyle=stroke;ctx.lineWidth=1;ctx.beginPath();ctx.roundRect(x,y,ww,hh,rad);ctx.fill();ctx.stroke();}
function drawWorld(){ctx.fillStyle='#0b1926';ctx.fillRect(0,0,720,430);
 box(25,18,670,70,'#142737');label(43,43,'EARLIER: WARNING FLASH',12,'#a8bdcb');label(43,70,w.last?(w.last.cue===-1?'◀ LEFT':'RIGHT ▶'):'◀ LEFT  /  RIGHT ▶',22,'#f6cc76');label(660,65,'Signal disappears before decision',12,'#a8bdcb','right');
 label(42,127,'THREE TICKS LATER: AGENTS CHOOSE A ROUTE',12,'#a8bdcb');
 box(28,143,318,206,'#122d36');box(374,143,318,206,'#122d36');
 const safe=w.last?w.last.safe:null;const leftSafe=safe===-1,rightSafe=safe===1;
 label(187,173,'LEFT GATE',16,'#d8eaf2','center');label(533,173,'RIGHT GATE',16,'#d8eaf2','center');
 const c1=leftSafe?'#7be2ca':safe===null?'#638397':'#ff8f8c',c2=rightSafe?'#7be2ca':safe===null?'#638397':'#ff8f8c';
 box(49,187,276,43,leftSafe?'#1a4b48':'#47303a',c1);box(395,187,276,43,rightSafe?'#1a4b48':'#47303a',c2);
 label(187,213,safe===null?'Hidden':leftSafe?'SAFE + FOOD':'HAZARD',14,c1,'center');label(533,213,safe===null?'Hidden':rightSafe?'SAFE + FOOD':'HAZARD',14,c2,'center');
 if(w.last){for(let i=0;i<Math.min(72,w.last.chosenLeft);i++){ctx.fillStyle=leftSafe?'#7be2ca':'#ff8f8c';ctx.fillRect(58+(i%18)*14.7,251+Math.floor(i/18)*17,7,7);}for(let i=0;i<Math.min(72,w.last.chosenRight);i++){ctx.fillStyle=rightSafe?'#7be2ca':'#ff8f8c';ctx.fillRect(404+(i%18)*14.7,251+Math.floor(i/18)*17,7,7);}}
 label(187,333,w.last?`${w.last.chosenLeft} chose left`:'Waiting for first trial',13,'#b6c9d4','center');label(533,333,w.last?`${w.last.chosenRight} chose right`:'Waiting for first trial',13,'#b6c9d4','center');
 box(29,367,662,45,'#162b39');label(42,394,w.last?`Last trial: ${w.last.correct} / ${POP} chose the safe route  ·  Each generation includes 5 trials`:'Start evolution to see agents adapt across generations',13,'#d9e9ee');
}
function chart(id,lines,min,max){const cv=document.getElementById(id),c=cv.getContext('2d'),width=cv.width,height=cv.height,margin={l:35,r:13,t:10,b:24};c.clearRect(0,0,width,height);c.font='11px system-ui';c.fillStyle='#b5c4cf';c.strokeStyle='#32495a';c.lineWidth=1;
 for(let i=0;i<=4;i++){const y=margin.t+(height-margin.t-margin.b)*i/4;c.beginPath();c.moveTo(margin.l,y);c.lineTo(width-margin.r,y);c.stroke();c.fillText((max-(max-min)*i/4).toFixed(2).replace(/0+$/,'').replace(/\.$/,''),2,y+4);}
 let points=w.records,first=points[0].g,last=Math.max(first+1,points[points.length-1].g),x=(v)=>margin.l+(v-first)/(last-first)*(width-margin.l-margin.r),y=(v)=>margin.t+(1-(clamp(v,min,max)-min)/(max-min))*(height-margin.t-margin.b);
 for(const l of lines){c.beginPath();c.strokeStyle=l.color;c.lineWidth=l.width||2;let started=false;for(const v of points){if(v[l.key]==null)continue;let xx=x(v.g),yy=y(v[l.key]);if(!started){c.moveTo(xx,yy);started=true}else c.lineTo(xx,yy);}c.stroke();}
 c.fillStyle='#a2b8c4';c.fillText(String(first),margin.l,height-4);c.fillText(String(last),width-margin.r-33,height-4);
}
function render(){drawWorld();const s=w.stats();document.getElementById('gen').textContent=s.generations.toLocaleString();document.getElementById('acc').textContent=s.generations?(s.accuracy*100).toFixed(1)+'%':'—';document.getElementById('ret').textContent=s.meanRetention.toFixed(2);document.getElementById('dec').textContent=s.meanDecoder.toFixed(2);
 chart('accChart',[{key:'accuracy',color:'#7be2ca',width:2.5}],0,1);
 // Normalized decoding gene shown as a separate trajectory via derived values in renderer.
 const rd=w.records.map(v=>({...v,normalizedDecoder:v.d/3}));const orig=w.records;w.records=rd;chart('geneChart',[{key:'r',color:'#f6cc76'},{key:'normalizedDecoder',color:'#8dbafc'}],-1,1);w.records=orig;
 const t=document.getElementById('interpret');if(!s.generations)t.textContent='Run for at least 100 generations, then compare identical seeds across the four modes.';
 else if(s.mode==='blocked')t.textContent='The warning was erased before the decision. Correct-route choices should remain near chance regardless of inherited weights.';
 else if(s.mode==='random')t.textContent='Warnings carry no information about which gate is safe. Even perfect memory cannot consistently improve prediction.';
 else if(s.mode==='nonheritable')t.textContent='Agents are selected based on performance, but offspring are randomly reprogrammed, preventing sustained adaptation across generations.';
 else t.textContent=`Mean accuracy over the last ${Math.min(30,s.generations)} generations: ${(s.avgLast30*100).toFixed(1)}%. Both remembering and interpreting the cue can be favored when they lead to more descendants.`;
}
function stop(){playing=false;cancelAnimationFrame(request);document.getElementById('play').textContent='▶ Evolve';}
function reset(){stop();w=new PredictionWorld(Number(document.getElementById('seed').value)||42,document.getElementById('mode').value);render();document.getElementById('notice').textContent='World reset with fresh random genomes.';}
function step(n){stop();w.run(n);render();document.getElementById('notice').textContent=`Advanced ${n.toLocaleString()} generations.`;}
function loop(){if(!playing)return;w.run(Number(document.getElementById('speed').value));render();request=requestAnimationFrame(loop);}
document.getElementById('play').onclick=()=>{playing=!playing;if(playing){document.getElementById('play').textContent='❚❚ Pause';document.getElementById('notice').textContent='Evolution running.';request=requestAnimationFrame(loop);}else stop();};
document.getElementById('plus10').onclick=()=>step(10);document.getElementById('plus100').onclick=()=>step(100);document.getElementById('reset').onclick=reset;document.getElementById('mode').onchange=reset;document.getElementById('seed').onchange=reset;
window.PredictionWorld=PredictionWorld;window.getStats=()=>w.stats();window.runBatch=(seed,mode,steps)=>new PredictionWorld(seed,mode).run(steps).stats();render();
</script></body></html>'''
p.write_text(html)
print(p, len(html))
