import json, numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
p=Path('/mnt/data/consciousness_lab');d=json.loads((p/'experiment_05_results.json').read_text());fig,ax=plt.subplots(figsize=(11.5,5.8),layout='constrained')
for name,label in [('truthful','Informative sensor'),('shuffled','Random sensor'),('disabled','Sensor unavailable'),('noinherit','No inheritance')]:
 series=d['experiments'][name]['series']; y=np.array([[t['quality'] for t in s['trace']] for s in series]);
 # moving average smooth noise across generation and seed
 means=y.mean(axis=0);width=9; sm=np.convolve(np.pad(means,(width//2,width//2),mode='edge'),np.ones(width)/width,mode='valid');ax.plot(range(1,len(sm)+1),sm*100,label=label,linewidth=2.1)
ax.axvline(120,linestyle='--',linewidth=1.2,label='Environment changes');ax.set(xlim=(0,240),ylim=(25,100),xlabel='Evolutionary generation',ylabel='Correct decisions (%)',title='Experiment 05 · Evolving instruments for hidden information');ax.grid(alpha=.16);ax.legend(frameon=False,ncol=2,loc='lower left');fig.savefig(p/'experiment_05_results_chart.png',dpi=160)
print('CHART_CREATED',p/'experiment_05_results_chart.png', (p/'experiment_05_results_chart.png').stat().st_size)
print('RUNS',len(d['experiments']['truthful']['series']))
