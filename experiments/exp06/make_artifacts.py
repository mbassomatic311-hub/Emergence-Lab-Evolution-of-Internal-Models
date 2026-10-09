from pathlib import Path
import json,html,zipfile,hashlib,textwrap,shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image,Table,TableStyle,PageBreak,KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.enums import TA_LEFT,TA_CENTER
from reportlab.lib.units import inch

ROOT=Path(__file__).resolve().parent
metrics=json.loads((ROOT/'metrics.json').read_text());champions=json.loads((ROOT/'champions.json').read_text()); traces=json.loads((ROOT/'traces.json').read_text())
seeds=[100003+101*i for i in range(24)]
modes=['evolve','no_recurrence','random_fitness','no_inheritance']
labels=['Evolved recurrence','No recurrence','Random selection','No inheritance']
sc=[metrics[a]['exact_payoff']['mean'] for a in modes]
ci=[metrics[a]['exact_payoff']['ci95'] for a in modes]

# Figure 1: all independent run results (not just aggregate means)
fig,ax=plt.subplots(figsize=(9.1,4.7));rng=np.random.default_rng(41)
import csv
rows=list(csv.DictReader((ROOT/'results_per_seed.csv').open()))
for i,mode in enumerate(modes):
    values=np.array([float(r['exact_payoff']) for r in rows if r['mode']==mode])
    ax.scatter(i+rng.normal(0,.075,len(values)),values,s=18,alpha=.55)
    ax.errorbar([i],[sc[i]],yerr=np.array([[sc[i]-ci[i][0]],[ci[i][1]-sc[i]]]),fmt='o',capsize=5,color='black',markersize=7)
ax.axhline(0,linestyle='--',linewidth=1,color='.55')
ax.axhline(.21,linestyle=':',linewidth=1,color='.3')
ax.text(3.34,.212,'Oracle bound',fontsize=9,va='bottom',ha='right')
ax.set_xticks(range(4),labels,rotation=8);ax.set_ylabel('Expected net survival payoff / episode')
ax.set_title('Experiment 06: outcomes from 24 independent evolutionary runs per condition')
ax.set_xlim(-.45,3.45);fig.tight_layout();fig.savefig(ROOT/'figure_1_payoffs.png',dpi=190);plt.close(fig)

# Figure 2: within same champion, retain recurrent memory vs destroy it
v=sorted([r for r in rows if r['mode']=='evolve'],key=lambda s:int(s['seed']))
val=np.array([float(r['exact_payoff']) for r in v]);links=np.array([float(r['active_links']) for r in v])
fig,axs=plt.subplots(1,2,figsize=(9.1,4.1))
axs[0].plot(range(1,25),val,marker='o',lw=1.3);axs[0].axhline(0,linestyle='--',color='.5');axs[0].axhline(.21,linestyle=':',color='.5')
axs[0].set_xlabel('Independent evolution replicate');axs[0].set_ylabel('Expected payoff');axs[0].set_title('Evolutionary variability')
axs[1].scatter(links,val);axs[1].set_xlabel('Active recurrent connections');axs[1].set_ylabel('Expected payoff');axs[1].set_title('Connections are not a consciousness measure')
fig.tight_layout();fig.savefig(ROOT/'figure_2_variability.png',dpi=190);plt.close(fig)

m=metrics['evolve'];bestseed=max(seeds,key=lambda s:float(next(r['exact_payoff'] for r in v if int(r['seed'])==s)))
best=champions[f'evolve_{bestseed}']
mean=m['exact_payoff']['mean'];conf=m['exact_payoff']['ci95'];mean_auc=m['agency_auc']['mean'];null=metrics['random_fitness']['exact_payoff']['mean'];
no_mem=m['scrambled_payoff']['mean'];q80=m['q80_payoff']['mean'];q08=m['q08_payoff']['mean'];

paper=f'''# Evolved Action-Outcome Comparison in Minimal Recurrent Agents: An Exploratory Simulation

**Status:** Open computational methods note, not a peer-reviewed paper or proof of consciousness. Prepared 8 October 2026. Authorship and affiliations to be confirmed prior to public distribution.

## Abstract
An elementary prerequisite for distinguishing self-generated from external sensory events is to combine an earlier motor command with a later sensory consequence. We tested whether structural mutation and Darwinian-style selection could produce that ability in agents initialized with no recurrent neural connections. Four-unit neural controllers faced a two-phase ecology in which the current sensory signal alone was uninformative about the hidden source. Recurrent connections were initially absent and could arise through inherited mutations. We analyzed 24 independent evolutionary runs per condition, 300 generations each, against no-recurrence, random-fitness, and no-inheritance controls. The primary outcome was expected survival payoff on a fully specified probability distribution, with additional interventions and independent held-out trials. The mean evolved payoff was {mean:.4f} (95% bootstrap interval {conf[0]:.4f}–{conf[1]:.4f}), compared with {null:.4f} under random fitness selection and an analytic ceiling of 0.2100. Mean post hoc source classification AUC was {mean_auc:.3f}. These results provide a minimal demonstration of evolved sensorimotor comparison under engineered constraints, not evidence for subjective awareness. Direct conceptual antecedents include corollary discharge and robot self-modeling research.

## Research question and scope
Can inherited mutation and selection create a working action-outcome comparison circuit from initially absent recurrent connections when the organism benefits from distinguishing self-caused and external sensory consequences? The study is a model of evolved **causal sensorimotor integration**, not a measurement of conscious experience, not an origin-of-life simulation, and not an unrestricted open-ended artificial ecology.

## Methods (ADEMP)
**Aims.** Identify the minimal structural condition under which an agent can use its own preceding motor action to make an adaptive decision about an ambiguous event; quantify variance across independent evolutionary histories.

**Data generation.** Each episode samples balanced motor direction c in {{−1,+1}} and equally likely hidden source z∈{{self,external}}. Self-generated events agree with c with probability q=0.92; externally generated events are random. At the earlier phase the controller observes c, while at the later phase it observes only the binary sensory event y. The source itself is never an input. Entry earns +1 for self-caused events, −1 for externally caused events; declining earns 0. The design intentionally makes action–event contingency useful for survival.

**Controllers and evolution.** The controller has four nonlinear hidden units. Initial action-to-event recurrent weights are all zero and connection masks all false. Structural mutations can introduce or remove recurrent edges; continuous weights also mutate. Population size 192; 300 generations; 24 elites; 64 eligible parents; other hyperparameters and immutable pre-run checksums in STUDY_PROTOCOL.md and engine.py. Fitness is computed as the exact expected environmental payoff over the four possible (c,y) pairs. There is no backpropagation or explicit self/other classification training. The source enters only the environment/payoff computation.

**Estimands and analysis.** The primary estimand is the mean across 24 fresh, fixed simulation seeds of champion expected payoff, paired to the same genome with recurrence disabled. The analytic maximum is 0.2100 at q=0.92 and no measurement cost. 95% percentile bootstrap intervals resample independent evolutionary seeds 12,000 times. Negative controls separately disable recurrence, randomize fitness-based selection, or prevent genotype inheritance. Held-out Monte Carlo trials per champion: 25,000. Secondary interventions change event reliability to q=0.80, 0.50, and 0.08; shuffle the retained cue; measure post hoc ROC AUC of entry likelihood for latent causal source.

**Study status.** The analysis plan was frozen locally before the 24-seed runs, with SHA-256 hashes, but was NOT externally or prospectively preregistered. Some model choices were informed by pilot runs excluded from this set; findings remain exploratory.

## Results
- Evolved recurrence: mean payoff {mean:.4f}; 95% bootstrap CI [{conf[0]:.4f},{conf[1]:.4f}].
- No recurrence: mean payoff {metrics['no_recurrence']['exact_payoff']['mean']:.4f}; random fitness: {null:.4f}; no inheritance: {metrics['no_inheritance']['exact_payoff']['mean']:.4f}.
- Mean post-hoc hidden-source ROC AUC: {mean_auc:.3f} (chance is 0.5). This reflects information acquired about cause, **not** subjectivity.
- Held-out reliability q=0.80: mean exact payoff {q80:.4f}; uninformative q=0.50: {m['q50_payoff']['mean']:.4f}; reversed q=0.08: {q08:.4f}.
- When cue memory is shuffled on new episodes, average payoff is {no_mem:.4f}. Cutting recurrence analytically yields {m['exact_payoff']['mean']-metrics['paired_differences']['evolve_minus_memory_ablated']['mean']:.4f}.
- Individual evolutionary runs varied; Figure 2 shows the full distribution rather than selecting only successful examples.

## Interpretation
The data support a narrow computational claim: an action-history link can be favored when survival requires integrating temporally separated sensory and motor information. The same controller loses that advantage when recurrence is removed, cues are scrambled, or the environment ceases to carry useful motor-contingent information. This is a minimal computational reenactment of an established concept: a corollary-discharge/efference-copy-like comparison. The model does not demonstrate a full body model, subjective feeling, personal identity, or an evolutionary origin of consciousness.

## Major limitations
1. The task was designed so the action–outcome comparison matters. Its evolution cannot establish that real ecology necessarily produces subjective awareness.
2. Even though recurrent links were initially absent, neural units, mutation operators, survival payoffs, timing and sensory representations were specified by the experimenter.
3. The controller has only two observations and a binary action. It has no metabolism, body morphology, changing physical world or genuinely self-directed sensor exploration.
4. Analytical selection fitness uses the full known environment distribution rather than individual noisy lifetime survival; stochastic uncertainty is added only in held-out evaluation.
5. The phenomenon overlaps extensively with existing corollary discharge, internal-model and evolutionary robotics literature. Original scientific novelty has not been established.
6. A linear or nonlinear readout decoding causal source from internal state cannot establish phenomenal consciousness.
7. The local protocol was not published before the run and does not have the status of external preregistration or independently verified replication.

## Publication assessment
Suitable for open sharing as an **exploratory computational note with code**, but not yet suitable to claim a new theory of consciousness or a peer-reviewed biological discovery. A stronger research submission would need external critique, replication by someone independent, ecologically richer simulations, independent controller architectures, comparison to published models, robustness to altered evolutionary parameters, and a demonstrably novel prediction.

## References
- Crapse, T.B. & Sommer, M.A. (2008). Corollary discharge across the animal kingdom. *Nature Reviews Neuroscience* 9, 587–600. doi:10.1038/nrn2457.
- Bongard, J., Zykov, V. & Lipson, H. (2006). Resilient machines through continuous self-modeling. *Science* 314, 1118–1121. doi:10.1126/science.1133687.
- Tanaka, T. & Imamizu, H. (2025). Sense of agency for a new motor skill emerges via the formation of a structural internal model. *Communications Psychology* 3, 70. doi:10.1038/s44271-025-00240-7.
- Morris, T.P., White, I.R. & Crowther, M.J. (2019). Using simulation studies to evaluate statistical methods. *Statistics in Medicine* 38, 2074–2102. doi:10.1002/sim.8086.
- Center for Open Science (2025). Simulation Studies Preregistration Template and OSF registration guidance. https://help.osf.io/article/330-welcome-to-registrations.
'''
(ROOT/'research_note.md').write_text(paper)

# standalone interactive HTML with accurate live forward-pass for the champion genome.
metrics_json=json.dumps({k:v for k,v in metrics.items() if k in modes},separators=(',',':'))
trace_data=json.dumps({str(seed):traces[f'evolve_{seed}'] for seed in seeds},separators=(',',':'))
agent_json=json.dumps({str(seed):champions[f'evolve_{seed}'] for seed in seeds},separators=(',',':'))
page='''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Emergence Lab • Experiment 06</title>
<style> :root{--bg:#0a1420;--panel:#111f2d;--line:#2c4254;--t:#edf4f7;--sub:#a8bdc9;--accent:#40d6bc;--warning:#f2c17e} *{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--t);font-family:Inter,system-ui,Arial,sans-serif;line-height:1.5}.wrap{max-width:1020px;margin:0 auto;padding:32px 20px 65px}header{border-bottom:1px solid var(--line);padding-bottom:22px}h1{font-size:clamp(27px,5vw,47px);letter-spacing:-.04em;line-height:1.08;margin:10px 0}h2{font-size:22px;margin:0 0 13px;letter-spacing:-.025em}p{color:var(--sub);margin:10px 0}.eyebrow{font-size:12px;letter-spacing:.16em;color:var(--accent);font-weight:800}.hero{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:22px 0}.stat{padding:18px;background:var(--panel);border:1px solid var(--line);border-radius:13px}.stat strong{font-size:29px;display:block;font-variant-numeric:tabular-nums}.stat span{font-size:12px;color:var(--sub)}.grid{display:grid;grid-template-columns:1.1fr .9fr;gap:15px}.card{padding:24px;border:1px solid var(--line);border-radius:15px;background:var(--panel);margin:0 0 16px}.btn,select{appearance:none;color:var(--t);border:1px solid var(--line);border-radius:10px;background:#193044;padding:10px 13px;font:inherit;cursor:pointer}.btn[aria-pressed=true]{background:var(--accent);color:#071924;font-weight:800}.controls{display:flex;flex-wrap:wrap;gap:8px;margin:13px 0}.wide{width:100%}.meter{height:11px;border-radius:100px;overflow:hidden;background:#2b4050;margin:15px 0 6px}.fill{height:100%;background:var(--accent);width:50%;transition:width .2s}.mono{font-family:ui-monospace,SFMono-Regular,monospace;font-size:13px}.hint{color:var(--warning);font-size:13px} .muted{color:var(--sub);font-size:13px} .plot{width:100%;height:240px;background:#0d1a28;border:1px solid var(--line);border-radius:10px}.legend{display:flex;flex-wrap:wrap;gap:15px;color:var(--sub);font-size:12px;margin-top:10px}.swatch{display:inline-block;width:9px;height:9px;border-radius:50%;background:var(--accent)}input[type=range]{width:100%;accent-color:var(--accent)}.out{padding:13px;background:#0d1a28;border:1px solid var(--line);border-radius:9px;margin-top:13px}.fine{font-size:12px;line-height:1.5;color:var(--sub)}a{color:var(--accent)}@media(max-width:680px){.grid{grid-template-columns:1fr}.hero{grid-template-columns:1fr 1fr}.card{padding:17px}} </style></head>
<body><main class="wrap"><header><div class="eyebrow">EMERGENCE LAB / EXPERIMENT 06 / EXPLORATORY</div><h1>When does a system distinguish <em>itself</em> from the world?</h1><p>Twenty-four independent evolutionary runs, controls and an interactive inspection of actual evolved neural genomes. This is sensorimotor computation, not a consciousness detector.</p></header>
<div class="hero"><div class="stat"><strong id="heroGain"></strong><span>Mean payoff: evolving recurrence</span></div><div class="stat"><strong id="heroAuc"></strong><span>Mean causal-source AUC (chance = .50)</span></div><div class="stat"><strong>24 × 300</strong><span>Independent seeds × generations per condition</span></div></div>
<section class="grid"><article class="card"><h2>1. Evolution under selection</h2><p>Select one evolved population. The curve shows its recorded fitness history, not a live rerun.</p><label class="muted" for="seed">Evolution replicate</label> <select id="seed"></select><svg id="history" viewBox="0 0 540 240" class="plot" role="img" aria-label="Recorded evolutionary survival payoff over generations"></svg><div id="traceText" class="muted"></div></article>
<article class="card"><h2>2. Counterfactual sensory events</h2><p>The agent saw a motor command, then an ambiguous event. Try the four combinations and remove memory.</p><div class="muted">Earlier motor command</div><div class="controls"><button class="btn" id="cueNeg" aria-pressed="false">Left (−)</button><button class="btn" id="cuePos" aria-pressed="true">Right (+)</button></div><div class="muted">Later sensory signal</div><div class="controls"><button class="btn" id="eventNeg" aria-pressed="false">Left (−)</button><button class="btn" id="eventPos" aria-pressed="true">Right (+)</button></div><label><input type="checkbox" id="block"> Cut recurrence / erase retained command</label><div class="meter"><div class="fill" id="decisionFill"></div></div><strong id="decisionText"></strong><div id="caseMessage" class="muted"></div><div class="out mono" id="neuronText"></div></article></section>
<section class="grid"><article class="card"><h2>3. The environment changes</h2><p>Change how reliably an action produces a matching sensory event. Watch the same evolved controller's expected payoff change without retraining.</p><label for="q" id="qText"></label><input id="q" type="range" min="0" max="100" value="92" step="1"><div class="out"><div class="muted">Expected net payoff per episode</div><strong id="qPayoff" style="font-size:26px"></strong><div id="qNote" class="hint"></div></div></article><article class="card"><h2>4. Conditions and controls</h2><p>Mean expected survival payoff across 24 independent evolutionary histories.</p><div id="controlBars"></div><p class="fine">A genome selected by random fitness can still have useful processing by chance. All negative controls are reported, not discarded.</p></article></section>
<article class="card"><h2>What this does—and does not—mean</h2><p>An earlier motor command can become useful later when sensory consequences are otherwise ambiguous. The environment's source information is hidden from the controller; survival selects better responses. No explicit “self/other” output is trained.</p><p>However, we engineered the two-stage task, possible neural units, payoff consequences, and mutation mechanism. Evolved memory is not equivalent to a conscious self. This is an exploratory illustration of a concept already studied as <em>corollary discharge</em> and <em>efference copy</em>.</p><div class="fine">Source and study protocol are included in the reproducibility archive. The browser view plays back genuine computed results; modifying a slider evaluates a saved neural controller and does not rerun evolution.</div></article></main>
<script> const M=__METRICS__; const TR=__TRACES__;const A=__AGENTS__;let seed=Object.keys(A)[0],cue=1,event=1;const el=id=>document.getElementById(id);const fmt=x=>(x>=0?'+':'')+x.toFixed(3);el('heroGain').textContent=fmt(M.evolve.exact_payoff.mean);el('heroAuc').textContent=M.evolve.agency_auc.mean.toFixed(3);Object.keys(A).forEach((s,i)=>{const o=document.createElement('option');o.value=s;o.textContent='Run '+(i+1)+' · seed '+s;el('seed').appendChild(o)});el('seed').onchange=e=>{seed=e.target.value;draw()};
function network(c,y,memory=true){const g=A[seed],p=g.plain,H=4,h0=[],h1=[];for(let j=0;j<H;j++)h0[j]=Math.tanh(c*p[j]+p[8+j]);for(let j=0;j<H;j++){let v=y*p[4+j]+p[8+j];if(memory){for(let i=0;i<H;i++)v+=h0[i]*g.rec[i][j]*g.mask[i][j]}h1[j]=Math.tanh(v)}let z=p[16];for(let j=0;j<H;j++)z+=h1[j]*p[12+j];return{prob:1/(1+Math.exp(-Math.max(-45,Math.min(45,z)))),h:h1}}
function exact(q,memory){const cfg=[[-1,-1],[-1,1],[1,-1],[1,1]];let sum=0;for(const[c,y]of cfg){const p=network(c,y,memory).prob;sum+=p*(.25*(c===y?q:1-q)-.125)}return sum}
function lineplot(){const t=TR[seed],svg=el('history');let values=t.map(x=>x[1]), ymax=Math.max(.22,...values), ymin=Math.min(-.005,...values);let xp=i=>37+i/(t.length-1)*480;let yp=v=>215-(v-ymin)/(ymax-ymin)*185;svg.innerHTML='';const NS='http://www.w3.org/2000/svg';function add(tag,attrs){const e=document.createElementNS(NS,tag);for(const[k,v]of Object.entries(attrs))e.setAttribute(k,v);svg.appendChild(e);return e}for(const k of [0,.1,.2]){const y=yp(k);add('line',{x1:35,x2:525,y1:y,y2:y,stroke:'#294558'});const txt=add('text',{x:2,y:y+4,fill:'#a8bdc9','font-size':'12'});txt.textContent=k.toFixed(2)}const pts=t.map((z,i)=>`${xp(i)},${yp(z[1])}`).join(' ');add('polyline',{points:pts,fill:'none',stroke:'#40d6bc','stroke-width':'3','stroke-linejoin':'round'});el('traceText').textContent='Final best payoff: '+fmt(t[t.length-1][1])+' · Average active recurrent connections: '+t[t.length-1][3].toFixed(1)}
function update(){for(const [id,value]of [['cueNeg',-1],['cuePos',1],['eventNeg',-1],['eventPos',1]])el(id).setAttribute('aria-pressed',String(id.startsWith('cue')?cue===value:event===value));const result=network(cue,event,!el('block').checked);el('decisionFill').style.width=(100*result.prob).toFixed(1)+'%';el('decisionText').textContent=(100*result.prob).toFixed(1)+'% tendency to approach';el('caseMessage').textContent=(cue===event?'Event matches earlier motor command':'Event conflicts with motor command')+'. This is evidence about the cause, not certainty.';el('neuronText').textContent='Hidden state: ['+result.h.map(v=>v.toFixed(2)).join(', ')+']';const q=+el('q').value/100;el('qText').textContent='Motor-to-sensation reliability: '+(100*q).toFixed(0)+'%';const p=exact(q,!el('block').checked);el('qPayoff').textContent=fmt(p);el('qNote').textContent=q===.5?'No causal information: chance-level payoff.':q<.5?'The motor relationship is reversed: this policy may fail.':'The learned contingency is still informative.'}
for(const [id,v] of [['cueNeg',-1],['cuePos',1]])el(id).onclick=()=>{cue=v;update()};for(const[id,v]of [['eventNeg',-1],['eventPos',1]])el(id).onclick=()=>{event=v;update()};el('block').onchange=update;el('q').oninput=update;function bars(){const names={evolve:'Evolving recurrence',no_recurrence:'No recurrence',random_fitness:'Random selection',no_inheritance:'No inheritance'},e=el('controlBars');e.innerHTML='';for(const k of ['evolve','no_recurrence','random_fitness','no_inheritance']){const v=M[k].exact_payoff.mean;const item=document.createElement('div');item.style.marginBottom='14px';item.innerHTML='<div class="muted">'+names[k]+' · '+fmt(v)+'</div><div class="meter" style="margin-top:5px"><div class="fill" style="width:'+Math.max(1,Math.max(0,v)/.21*100).toFixed(1)+'%"></div></div>';e.appendChild(item)}}function draw(){lineplot();update()}bars();draw(); </script></body></html>'''
page=page.replace('__METRICS__',metrics_json).replace('__TRACES__',trace_data).replace('__AGENTS__',agent_json)
(ROOT/'experiment_06_interactive.html').write_text(page)

# Summary PDF (use reportlab, no HTML to DOC conversion).
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleX',parent=styles['Title'],fontName='Helvetica-Bold',fontSize=20,leading=24,spaceAfter=12,textColor=colors.HexColor('#12283D')))
styles.add(ParagraphStyle(name='SubX',parent=styles['Heading2'],fontName='Helvetica-Bold',fontSize=11,leading=15,spaceBefore=10,spaceAfter=5,textColor=colors.HexColor('#173B50')))
styles.add(ParagraphStyle(name='ParaX',parent=styles['BodyText'],fontSize=9.0,leading=12.5,spaceAfter=5))
styles.add(ParagraphStyle(name='SmallX',parent=styles['BodyText'],fontSize=8,leading=11,spaceAfter=5,textColor=colors.HexColor('#435766')))
def P(t,style='ParaX'):return Paragraph(html.escape(t),styles[style])
doc=SimpleDocTemplate(str(ROOT/'experiment_06_research_note.pdf'),pagesize=(612,792),rightMargin=48,leftMargin=48,topMargin=38,bottomMargin=38)
story=[P('Evolved Action-Outcome Comparison in Minimal Recurrent Agents','TitleX'),P('An exploratory computational methods note | Experiment 06 | 8 October 2026','SmallX'),P('Scope: sensorimotor computation; not a test or demonstration of consciousness.','SmallX'),Spacer(1,7),P('Abstract','SubX'),P(f'We tested whether survival-oriented selection creates action-outcome comparison in artificial neural agents initialized without recurrent connections. Across 24 independent evolution seeds and 300 generations per condition, evolved networks achieved a mean expected payoff of {mean:.4f} (95% bootstrap CI {conf[0]:.4f}–{conf[1]:.4f}), against an analytic maximum of 0.2100. A random-selection baseline scored {null:.4f} on average. The task was engineered to make earlier motor commands informative about later ambiguous events; accordingly the result demonstrates evolved sensorimotor processing within an artificial task, not subjective experience.'),P('Research design','SubX'),P('A 4-unit neural controller saw an action command at time 0, then a binary sensory event at time 1. The event could originate from the action (92% directional correspondence) or an external source (random direction), with equal prior probability. Correctly treating self-caused events as safe and external events as dangerous improved survival payoff. Recurrent links capable of carrying the earlier command were absent initially and could arise by mutation; no explicit self/other label was available to the agent.'),P('Methods and analyses','SubX'),P('24 independent seeds; population 192; 300 generations; truncation selection, genotype inheritance, structural and continuous mutations. Same-budget baselines: no recurrence, random fitness selection, no genotype inheritance. Exact expected survival payoff was the primary metric. Secondary: hold-out Monte Carlo trials, memory ablation, cue scrambling, contingency change, and post-hoc causal-source AUC. Analysis plan frozen locally, NOT externally preregistered.'),Image(str(ROOT/'figure_1_payoffs.png'),width=480,height=234),P('Figure 1. Each dot is a separate evolutionary run. Black markers show condition means and 95% bootstrap intervals; dotted line indicates theoretical maximum.','SmallX'),PageBreak(),P('Findings and qualifications','TitleX'),P('Results','SubX')]
res_data=[['Condition','Mean payoff','95% bootstrap CI']]
for key,label in zip(modes,labels):
 x=metrics[key]['exact_payoff'];res_data.append([label,f'{x["mean"]:.4f}',f'{x["ci95"][0]:.4f} to {x["ci95"][1]:.4f}'])
t=Table(res_data,colWidths=[220,100,170],repeatRows=1,hAlign='LEFT')
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E7F0F2')),('TEXTCOLOR',(0,0),(-1,0),colors.HexColor('#173B50')),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('LINEBELOW',(0,0),(-1,-1),.4,colors.HexColor('#CBD8DE')),('BOTTOMPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8),('FONTSIZE',(0,0),(-1,-1),8.5)]));story.append(t)
story+=[Spacer(1,12),P(f'Post-hoc AUC for hidden event source: {mean_auc:.3f} (chance 0.50). On a reduced-reliability environment (q=0.80), expected payoff was {q80:.4f}; when no information was present (q=0.50), {m["q50_payoff"]["mean"]:.4f}; with inverted contingency (q=0.08), {q08:.4f}.', 'ParaX'),Image(str(ROOT/'figure_2_variability.png'),width=410,height=165),P('Figure 2. Runs vary substantially. Connections are structural prerequisites here, not measures of experience.','SmallX'),P('What can be concluded','SubX'),P('A recurrent action-history pathway can evolve from initially absent connections and improve survival in an engineered two-stage motor/sensory task. The behavior is contingent on the environmental model and disappears when the historical information is made inaccessible. This is a minimal computational illustration of action-outcome comparison.'),P('What cannot be concluded','SubX'),P('No agent was shown to have first-person experience, awareness, selfhood, a biological brain, or an independently developed theory of its own body. The environment, actions, payoffs, possible neurons, and mutation process were designed by the investigator. The principle overlaps substantially with known corollary-discharge and robotics research. Do not present the work as a consciousness discovery.'),P('Publication assessment','SubX'),P('Appropriate for an open, transparently labeled computational methods note or educational demonstration once authorship and licensing are settled; not yet established as a novel, peer-review-ready contribution. Recommended next steps: independent replication, new and more ecological environments, alternative agent architectures, sensitivity analysis, comparison against published baselines, and public preregistration before any new confirmatory study.')]
doc.build(story)

# Package useful files, omit raw intermediate images and all previous toy experiments.
files=['README.md','STUDY_PROTOCOL.md','PRE_RUN_CHECKSUMS.sha256','engine.py','run_study.py','run_resumable.py','collate.py','make_artifacts.py','test_engine.py','results_per_seed.csv','metrics.json','traces.json','champions.json','figure_1_payoffs.png','figure_2_variability.png','research_note.md','experiment_06_research_note.pdf','experiment_06_interactive.html']
with zipfile.ZipFile(ROOT/'Emergence_Lab_Experiment_06_Research_Package.zip','w',zipfile.ZIP_DEFLATED) as z:
 for name in files:z.write(ROOT/name,arcname='Experiment_06/'+name)
# Audit source and artifacts.
with (ROOT/'DELIVERABLE_SHA256.txt').open('w') as fp:
 for name in files:
  h=hashlib.sha256((ROOT/name).read_bytes()).hexdigest();fp.write(f'{h}  {name}\n')
print('Files:', ', '.join([f for f in files if f.endswith(('.pdf','.html','.zip'))]));print(f'Mean evolved {mean:.5f} vs random {null:.5f}; AUC {mean_auc:.3f}; champion seed {bestseed}')
