"""Build reproducible publication-style exploratory note and figures for Experiment 07."""
import json, csv, hashlib, zipfile, textwrap, statistics
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import inch
p=Path(__file__).resolve().parent
primary=p/'primary'; summary=json.loads((primary/'summary.json').read_text()); curves=json.loads((primary/'trajectories.json').read_text()); rows=list(csv.DictReader((primary/'results_per_seed.csv').open()))
name={'full':'Evolved action history','reactive':'Reactive only','random_selection':'Random selection','no_inheritance':'No inheritance'}
# Single-axis data figure
fig,ax=plt.subplots(figsize=(9.0,4.6))
order=['full','reactive','random_selection','no_inheritance']
labels=[name[c] for c in order]
values=[summary['conditions'][c]['reversal_food'] for c in order]
ax.bar(labels,values)
ax.set(ylabel='Mean food rewards / 40-step held-out reversal',title='Experiment 07: Transfer after unexpected actuator reversal')
ax.set_ylim(0,max(values)*1.25)
ax.tick_params(axis='x',labelrotation=12)
for i,v in enumerate(values):ax.text(i,v+0.05,f'{v:.2f}',ha='center',va='bottom',fontsize=9)
ax.text(.02,.96,'32 evolutionary seeds per condition; test data never used in selection',transform=ax.transAxes,va='top',fontsize=9)
fig.tight_layout();fig.savefig(p/'experiment07_reversal.png',dpi=190);plt.close(fig)

fig,ax=plt.subplots(figsize=(9,4.5))
for mode in order:
    matches=[np.array(v) for k,v in curves.items() if k.endswith('_'+mode)]
    # Some suffix overlap impossible except mode full etc
    data=np.stack(matches)
    ax.plot(data[:,:,0].mean(axis=0),data[:,:,1].mean(axis=0),label=name[mode])
ax.set(title='Training rewards during simulated evolution',xlabel='Generation',ylabel='Mean food collected per lifetime')
ax.legend(fontsize=8); fig.tight_layout();fig.savefig(p/'experiment07_learning_curves.png',dpi=190);plt.close(fig)

h1=summary['paired_differences']['full_minus_reactive'];h2=summary['paired_differences']['full_minus_scrambled']
support=h1['mean']>0 and h1['ci95'][0]>0
pairs=summary['paired_differences']
f=lambda n: f'{n:.3f}'

paper=f'''# Emergence Lab Experiment 07
## Evolving action-conditioned adaptation under uncertain motor effects: an exploratory computational study

**Status: exploratory independent computational simulation. NOT peer-reviewed, externally replicated, or publicly preregistered.**

### Abstract
We simulated populations of agents who chose discrete motor commands in a noisy, one-dimensional resource world. The relationship between motor commands and movement was initially hidden and randomized across individual lifetimes. Controllers were selected using finite stochastic lifetime outcomes over 90 generations. A locally frozen protocol specified 32 independent evolutionary seeds, four arms and a held-out evaluation in which actuator polarity reversed unexpectedly halfway through a lifetime. The primary comparison was evolved controllers with an engineered action-conditioned recurrent state against reactive controllers. Evolved recurrent controllers collected {f(summary['conditions']['full']['reversal_food'])} food rewards per 40-step held-out reversal lifetime versus {f(summary['conditions']['reactive']['reversal_food'])} for reactive controls. The paired seed mean difference was {f(h1['mean'])} (95% seed-bootstrap CI {f(h1['ci95'][0])}, {f(h1['ci95'][1])}); the prespecified positive-difference criterion {'was met' if support else 'was NOT met'}. Test-time scrambling of the action-effect feedback yielded an observed mean difference of {f(h2['mean'])} (95% CI {f(h2['ci95'][0])}, {f(h2['ci95'][1])}); interpretation is limited by unequal downstream random draws in this ablation. These synthetic results address adaptability in evolutionary computation, NOT subjective experience or the emergence of consciousness.

### Research aim
Determine whether stochastic selection over actual simulated lifetimes can favor an action-conditioned feedback representation and produce transfer to an untrained actuator reversal, relative to appropriate controls. The study was motivated by questions about precursors to evolved self/world modeling, but measures only action choices, food rewards, and survival.

### Prior art
Body modeling and sensorimotor prediction in robotics have been studied for decades. Bongard, Zykov & Lipson (2006) demonstrated resilient robot adaptation using continuous self-modeling (doi:10.1126/science.1133687). Nguyen et al. (2020) surveyed sensorimotor representations of an active self (arXiv:2011.12860). Kahl et al. (2021) modeled sense of control in situated artificial agents (arXiv:2112.05577). Accordingly, we make NO priority, novelty, or phenomenal-consciousness claim.

### Protocol timeline and status
An exploratory two-seed implementation pilot (seeds 4100 and 4171) was viewed BEFORE freezing the primary protocol and source. The protocol and source were locally frozen and hashed before main analysis; hashes reside in FROZEN_SHA256.txt. The 32 primary seeds were disjoint from the pilot: 870000 + 71i for i = 0,...,31. **Local hashing is not OSF preregistration.** No later parameters were optimized based on main-study results.

### World and genetic controller
- Population: 64 eight-parameter genotypes. 90 generations, each with three stochastic 40-step lifetimes per genotype; selection based on actual food rewards and time alive, not an expected-fitness oracle.
- At each step each agent selects a left/right action. A hidden, episode-specific actuator polarity determines physical movement. Food appears 3–6 units to either side. Agents see a noisy relative bearing to food (not the hidden actuator setting). Actions consume energy, while collecting food restores energy.
- Agents can evolve weights for a fixed, provided memory unit using an engineered action-conditioned sensory-difference feature. They do NOT evolve their own sensors, a body morphology, or the connection architecture itself.
- A food relocation resets the previous-command signal so that new target creation is not mistaken for self-caused movement.
- Final candidate selection: six controllers chosen using 16 new *development* lifetimes in the training distribution. Held-out tests: 128 fresh episodes per selected controller. Test results are never used for selection.

### Arms and comparisons
1. Full: action-conditioned memory capable of integrating previous action effects.
2. Reactive: same overall genome representation, memory silenced.
3. Random selection: memory available but reproduction parent choice independent of fitness.
4. No inheritance: fresh genome population every generation (not compute-matched to inherited search).
5. Full with test-time scrambled action-copy: action feedback corrupted only during held-out evaluation. This is a test-time intervention, not a fifth independently evolved lineage.

### Prespecified analyses
The primary outcome is food collected per 40-step episode following an untrained actuator reversal at step 20. Primary contrast: full minus reactive, 32 paired evolutionary seeds. Secondary contrasts: random-selection, no-inheritance, and scrambled feedback. Bootstrap: 10,000 resamples of seed-level paired differences, fixed bootstrap seed 50607, percentile 95% intervals. These are within-model seed intervals and do not quantify biological uncertainty. The primary directional support criterion required a positive estimated mean and a 95% interval lower bound greater than zero.

### Results (held-out)
| Condition | Mean reversal food | Mean stable food | Reversal survival fraction |
|---|---:|---:|---:|
'''
for mode in order:
 d=summary['conditions'][mode]
 paper+=f"| {name[mode]} | {f(d['reversal_food'])} | {f(d['stable_food'])} | {f(d['reversal_survival'])} |\n"
paper+='''
Paired mean effects on reversal food rewards (full minus comparison):
'''
for mode,label in [('reactive','reactive'),('random_selection','random-selection'),('no_inheritance','no-inheritance'),('scrambled','scrambled feedback')]:
 k='full_minus_'+mode;d=pairs[k]
 paper+=f"- **{label}:** {f(d['mean'])} (95% bootstrap CI [{f(d['ci95'][0])}, {f(d['ci95'][1])}]); seed outcomes: {d['positive']} positive, {d['negative']} negative, {d['zero']} ties.\n"
paper+='''
### Sensitivity checks and limitations
1. This is a task intentionally designed to reward learning an unknown actuator mapping; transfer is tested within the same synthetic world family. We did not compare independently authored simulators, ecological tasks, controller families, or mutation-rate regimes.
2. The critical sensorimotor term and recurrent memory unit were included by design. Favorable outcomes cannot be described as a system inventing selfhood, a new network architecture, or basic awareness.
3. The reactive control is inherently less expressive, and the random/no-inheritance controls have different search dynamics. A complexity-matched nonrecurrent network, alternative policies (e.g. hand-coded Bayes) and reparameterizations should be added in follow-up work.
4. Unexpected actuator polarity inversion is a simplified distribution shift; it does not establish general world-model learning. Other transfer tests (sensor dropout, actuator latency, target dynamics, 2D worlds) are needed.
5. Within-agent scramble draws extra random numbers from the same generator, so full-vs-scrambled outcomes are not matched on exactly the same downstream environmental randomness; treat that secondary ablation as suggestive only.
6. Seed-bootstrap intervals represent outcomes under one invented world and fixed hyperparameters. They are not probability statements about consciousness or natural evolution.
7. Development-pilot observations preceded the local protocol freeze; there is no independent preregistration or third-party code audit.
8. Multiple comparisons were not adjusted, and secondary differences are descriptive.

### Interpretation and publication decision
This study is reproducible exploratory work in artificial evolution. If replicated with independent code and new environmental families, the result could support a narrow educational or methods-focused technical note about action-conditioned adaptation. It does NOT demonstrate an origin of consciousness, subjective experience, or a breakthrough in evolutionary neuroscience. For an externally credible research submission, publicly preregister an independently reimplemented Experiment 08 before any new data collection, compare architectural and reward alternatives, and invite an experienced evolutionary-robotics researcher to audit the design.

### Sources and provenance
- Bongard, Zykov, Lipson (2006), *Resilient Machines Through Continuous Self-Modeling*, Science. https://pubmed.ncbi.nlm.nih.gov/17110570/
- Nguyen et al. (2020), *Sensorimotor representation learning for an active self in robots: A model survey*. https://arxiv.org/abs/2011.12860
- Kahl et al. (2021), *Towards autonomous artificial agents with an active self*. https://arxiv.org/abs/2112.05577
- OSF preregistration documentation, including simulation-specific templates: https://help.osf.io/article/330-welcome-to-registrations
- Reproduce: `python -m unittest -q test_engine07.py && python engine07.py --seeds 32 --seed-start 870000 --out primary`
'''
(p/'RESEARCH_NOTE.md').write_text(paper)

styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='TitleCustom',parent=styles['Title'],fontName='Helvetica-Bold',fontSize=19,leading=23,spaceAfter=12));styles.add(ParagraphStyle(name='BodyCustom',parent=styles['BodyText'],leading=13,spaceAfter=8));styles.add(ParagraphStyle(name='SmallCustom',parent=styles['BodyText'],fontSize=8.7,leading=11.6,spaceAfter=6));styles.add(ParagraphStyle(name='HeadingCustom',parent=styles['Heading2'],fontSize=11,leading=15,spaceBefore=13,spaceAfter=7))
N=lambda k: summary['conditions'][k]
story=[Paragraph('EMERGENCE LAB | EXPERIMENT 07',styles['TitleCustom']),Paragraph('Evolving action-conditioned adaptation under unknown motor effects',styles['HeadingCustom']),Paragraph('Exploratory computational research note · 2026-10-08 · Not peer-reviewed or publicly preregistered',styles['SmallCustom']),Spacer(1,9)]
story.append(Paragraph('<b>Question.</b> Can evolution favor information-processing controllers that adapt to unexpected changes in the effects of their own actions?',styles['BodyCustom']))
story.append(Paragraph('<b>Design.</b> 32 evolutionary seeds per arm; 64 candidate controllers; 90 generations; each controller chooses its own left/right actions and encounters noisy food signals and unknown actuator polarity. Final selection uses separate development lifetimes; evaluation uses unseen episodes where actuator direction reverses halfway through.',styles['BodyCustom']))
story.append(Paragraph('<b>Important boundary.</b> The memory unit and its action-conditioned input were engineered by us. We measure adaptive behavior, not consciousness.',styles['BodyCustom']))
story.append(Image(str(p/'experiment07_reversal.png'),width=7.0*inch,height=3.6*inch))
story.append(Paragraph(f"<b>Primary comparison.</b> Evolved memory: {f(N('full')['reversal_food'])} vs reactive: {f(N('reactive')['reversal_food'])} food rewards per 40-step reversal episode. Mean seed-paired difference: {f(h1['mean'])}, 95% percentile bootstrap CI [{f(h1['ci95'][0])}, {f(h1['ci95'][1])}]. {'Criterion met' if support else 'Criterion NOT met'}.",styles['BodyCustom']))
story.append(PageBreak())
story.append(Paragraph('METHODS AND RESULTS',styles['TitleCustom']))
tdata=[['Condition','Unseen reversal','Stable world','Reversal survival']]
for mode in order:
 d=N(mode);tdata.append([name[mode], f(d['reversal_food']),f(d['stable_food']),f(d['reversal_survival'])])
t=Table(tdata,colWidths=[175,96,92,106],repeatRows=1)
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8edf1')),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#cdd4dc')),('FONTSIZE',(0,0),(-1,-1),8.5),('LEADING',(0,0),(-1,-1),11),('BOTTOMPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),8)]))
story.append(t);story.append(Spacer(1,10))
for mode in ['reactive','random_selection','no_inheritance','scrambled']:
 d=pairs['full_minus_'+mode];story.append(Paragraph(f"<b>Full minus {mode.replace('_',' ')}:</b> {f(d['mean'])} [95% CI {f(d['ci95'][0])}, {f(d['ci95'][1])}], with {d['positive']}/{summary['n_seeds']} seeds favoring full.",styles['SmallCustom']))
story.append(Image(str(p/'experiment07_learning_curves.png'),width=6.9*inch,height=3.4*inch))
story.append(Paragraph('Training data, test data, and random seeds are included in the accompanying ZIP. Code and protocol SHA-256 hashes were recorded before the primary run.',styles['SmallCustom']))
story.append(PageBreak())
story.append(Paragraph('INTERPRETATION & LIMITATIONS',styles['TitleCustom']))
sections=[('What this shows','Selection in a designed artificial world can favor a controller that uses action-conditioned feedback. The intervention is informative about task performance, not the presence of subjective experience.'),('What we built in','We specified the reward rules, sensorimotor feature, memory update architecture, genetic mutation process, and surprise reversal. Agents did not invent neurons, bodies, or the concept of self.'),('What remains unresolved','This is a one-dimensional synthetic benchmark with a limited controller family. Reactive and memory arms differ in representational capacity. Test-time scrambling also alters downstream pseudorandom-number draws, so this ablation is not perfectly paired.'),('Publication status','This is suitable for an openly labeled exploratory computational report, not a peer-reviewed finding about consciousness. Independent replication, broader environment families, and a PUBLIC pre-run registration would be necessary for stronger claims.'),('Sources','Bongard, Zykov & Lipson (2006), Science, doi:10.1126/science.1133687; Nguyen et al. (2020), arXiv:2011.12860; Kahl et al. (2021), arXiv:2112.05577; Center for Open Science simulation preregistration guidance.')]
for h,para in sections:
 story.append(Paragraph(h,styles['HeadingCustom']));story.append(Paragraph(para,styles['BodyCustom']))
story.append(Spacer(1,9))
story.append(Paragraph('Replication: python -m unittest -q test_engine07.py; python engine07.py --seeds 32 --seed-start 870000 --out primary',styles['SmallCustom']))
doc=SimpleDocTemplate(str(p/'experiment_07_research_note.pdf'),pagesize=(612,792),rightMargin=51,leftMargin=51,topMargin=46,bottomMargin=48,title='Emergence Lab: Experiment 07 exploratory research note')
doc.build(story)
readme='''# Emergence Lab / Experiment 07 reproducibility package\n\nStatus: Exploratory toy evolutionary simulation. Not biological research, not evidence of consciousness, not publicly preregistered.\n\n1. Install Python 3.10+, numpy, matplotlib, reportlab.\n2. Run `python -m unittest -q test_engine07.py`.\n3. Reproduce 32-seed primary data: `python engine07.py --seeds 32 --seed-start 870000 --out primary`.\n4. Regenerate paper, PDF and figures: `python build_report.py`.\n5. Check original file hashes in `FROZEN_SHA256.txt`.\n\nRead `PROTOCOL_FROZEN_BEFORE_MAIN.md` and `RESEARCH_NOTE.md` for design, limitations, and prior literature. All runs are simulated.\n\nThe pilot was run before freezing the protocol; the 32-seed study was later run from locally frozen source. Public preregistration has NOT occurred.\n'''
(p/'README.md').write_text(readme)
# no bundled primary pilot overwrite: records retained with disclosure
archive=p/'Experiment_07_Audited_Research_Package.zip'
include=['engine07.py','test_engine07.py','build_report.py','PROTOCOL_FROZEN_BEFORE_MAIN.md','FROZEN_SHA256.txt','RESEARCH_NOTE.md','README.md','experiment_07_research_note.pdf','experiment07_reversal.png','experiment07_learning_curves.png','pilot_stdout.txt','primary/results_per_seed.csv','primary/summary.json','primary/trajectories.json','primary/run.log']
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
 for fpath in include:z.write(p/fpath,arcname=fpath)
assert zipfile.ZipFile(archive).testzip() is None
(p/'DELIVERABLE_SHA256.txt').write_text('\n'.join(f'{hashlib.sha256((p/item).read_bytes()).hexdigest()}  {item}' for item in include+[archive.name])+'\n')
print('REPORT BUILT')
print('H1 support:',support)
print('ZIP:',archive,archive.stat().st_size)
print('PDF:',p/'experiment_07_research_note.pdf')
