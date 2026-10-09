'use strict';
class RNG {
  constructor(seed) { this.s = (Number(seed)>>>0) || 1; }
  next() { this.s = (Math.imul(1664525, this.s) + 1013904223)>>>0; return this.s/4294967296; }
  range(a,b) { return a + (b-a)*this.next(); }
  normal() { return (this.next()+this.next()+this.next()+this.next()+this.next()+this.next()-3) * 0.40824829; }
  index(n) { return Math.floor(this.next()*n); }
}
const POP=180, TRIALS=7, DELAY=3, MUT_ADD=.022, MUT_REMOVE=.009;
const clamp=(x,a,b)=>Math.min(b,Math.max(a,x));
const sig=(x)=>1/(1+Math.exp(-x));
const edgeCount=(g)=>g.sensor+g.loop+g.output;
const hasCircuit=(g)=>!!(g.sensor&&g.loop&&g.output);
class EmergenceWorld {
  constructor(seed=42, mode='evolve') {
    this.seed=Number(seed)||42;this.mode=mode;this.rng=new RNG(this.seed);this.generation=0;
    this.population=Array.from({length:POP},()=>this.blankGenome());
    this.history=[];this.last=null;this.record(.5,0); }
  blankGenome(){return {sensor:0,loop:0,output:0,decoder:this.rng.range(-2.5,2.5),retention:this.rng.range(.72,.99)};}
  mutate(g){const n={...g};
    if(this.mode!=='locked'){
      for(const k of ['sensor','loop','output']){
        if(n[k]===0&&this.rng.next()<MUT_ADD)n[k]=1;
        else if(n[k]===1&&this.rng.next()<MUT_REMOVE)n[k]=0;
      }
    }
    if(this.rng.next()<.09)n.decoder=clamp(n.decoder+this.rng.normal()*.50,-3.5,3.5);
    if(this.rng.next()<.09)n.retention=clamp(n.retention+this.rng.normal()*.055,.5,1);
    return n; }
  choose(g,cue){
    // The cue exists only at the beginning of a trial. The state is then updated
    // during three blank ticks. Only a heritable feedback edge can preserve it.
    let state=g.sensor?cue:0;
    for(let j=0;j<DELAY;j++){
      state=(g.loop&&this.mode!=='no_loop')?(g.retention*state+.13*this.rng.normal()):0;
    }
    let pRight=g.output?sig(2.9*g.decoder*state):.5;
    return this.rng.next()<pRight?1:-1;
  }
  tick(){
    this.generation++;
    let score=new Float64Array(POP),hits=0,lastCue=1,lastSafe=1,left=0,right=0,correctLast=0;
    for(let t=0;t<TRIALS;t++){
      const cue=this.rng.next()<.5?-1:1;
      const safe=this.mode==='scrambled'?(this.rng.next()<.5?-1:1):cue;
      let thisCorrect=0,thisLeft=0,thisRight=0;
      for(let i=0;i<POP;i++){
        const action=this.choose(this.population[i],cue);
        if(action===safe){score[i]++;hits++;thisCorrect++;}
        if(action===-1)thisLeft++;else thisRight++;
      }
      lastCue=cue;lastSafe=safe;left=thisLeft;right=thisRight;correctLast=thisCorrect;
    }
    const parents=this.population;
    let sums=new Float64Array(POP),total=0;
    for(let i=0;i<POP;i++){
      // Multiplicative penalty for extra wiring allows neutral and maladaptive
      // circuits to be lost rather than becoming common without selective benefit.
      total += Math.exp(3.0*(score[i]/TRIALS - .5)-.19*edgeCount(parents[i]));
      sums[i]=total;
    }
    const children=[];
    for(let i=0;i<POP;i++){
      if(this.mode==='nonheritable') children.push(this.mutate(this.blankGenome()));
      else {
        const target=this.rng.next()*total;
        let lo=0,hi=POP-1;
        while(lo<hi){let mid=(lo+hi)>>1;if(sums[mid]<target)lo=mid+1;else hi=mid;}
        children.push(this.mutate(parents[lo]));
      }
    }
    const rate=hits/(POP*TRIALS);
    this.last={cue:lastCue,safe:lastSafe,left,right,correct:correctLast,accuracy:rate};
    this.population=children;
    this.record(rate, correctLast/POP);
    return this.last;
  }
  record(accuracy,lastChoice){
    let sensor=0,loop=0,output=0,complete=0,positive=0,meanRet=0,wires=0;
    for(const g of this.population){sensor+=g.sensor;loop+=g.loop;output+=g.output;wires+=edgeCount(g);meanRet+=g.retention;if(hasCircuit(g)){complete++;if(g.decoder>0)positive++;}}
    this.history.push({gen:this.generation,accuracy,complete:complete/POP,useful:positive/POP,sensor:sensor/POP,loop:loop/POP,output:output/POP,wires:wires/POP,retention:meanRet/POP});
  }
  run(n){for(let i=0;i<n;i++)this.tick();return this;}
  stats(){const h=this.history[this.history.length-1];const n=Math.min(40,this.generation);let late=0;
    for(let i=0;i<n;i++)late+=this.history[this.history.length-1-i].accuracy;
    return {...h,seed:this.seed,mode:this.mode,lateAccuracy:n?late/n:null,generations:this.generation,last:this.last};
  }
}
if(typeof module!=='undefined'&&module.exports)module.exports={EmergenceWorld,POP,TRIALS,DELAY};
