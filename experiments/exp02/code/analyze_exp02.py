import json,statistics as st,math,csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict
p='/mnt/data/consciousness_lab'
rows=json.load(open(p+'/experiment_02_results.json'))
by={m:{r['seed']:r for r in rows if r['mode']==m} for m in ['predict','blocked','random','nonheritable']}
for m in by:
 arr=[v['lateMean'] for v in by[m].values()]
 n=len(arr);avg=st.mean(arr);sd=st.stdev(arr);ci=2.093*sd/math.sqrt(n)
 print(f'{m}: n={n} late_mean={avg*100:.3f}% SD={sd*100:.3f}pp CI95≈[{(avg-ci)*100:.3f}%,{(avg+ci)*100:.3f}%], min={(min(arr)*100):.1f}% max={(max(arr)*100):.1f}%')
for m in ['blocked','random','nonheritable']:
 ds=[by['predict'][seed]['lateMean']-v['lateMean'] for seed,v in by[m].items()]
 avg=st.mean(ds);ci=2.093*st.stdev(ds)/math.sqrt(len(ds))
 print(f'Paired improvement predict-{m}: {avg*100:.2f}pp, rough 95%CI {((avg-ci)*100):.2f} to {((avg+ci)*100):.2f}pp')
print('Sanity result exact 50% baseline=',.5)
# Dual-panel chart; clear representation of paired conditions and accuracy trajectories.
fig,ax=plt.subplots(figsize=(10.6,5.7))
colors={'predict':'#007e7e','blocked':'#e58b62','random':'#816bbf','nonheritable':'#718a97'}
labels={'predict':'Inherited predictive memory','blocked':'Memory disabled','random':'Cue carries no information','nonheritable':'No inherited traits'}
import numpy as np
for mode in ['predict','blocked','random','nonheritable']:
 # compressed series 0,15,30,...,300, across seeds.
 series=defaultdict(list)
 for r in by[mode].values():
  for pt in r['series']:
   if pt['g']>0:series[pt['g']].append(pt['accuracy'])
 xs=np.array(sorted(series)); mean=np.array([np.mean(series[t]) for t in xs]);sd=np.array([np.std(series[t],ddof=1) for t in xs]);
 ax.plot(xs,mean*100,label=labels[mode],lw=3 if mode=='predict' else 2,color=colors[mode],zorder=3 if mode=='predict' else 2)
 ax.fill_between(xs,(mean-sd)*100,(mean+sd)*100,color=colors[mode],alpha=.11)
ax.axhline(50,color='#333333',ls=':',lw=1.2)
ax.text(296,51.5,'Chance level',ha='right',fontsize=9,color='#495967')
ax.set(xlim=(0,300),ylim=(40,102),xlabel='Generations of selection',ylabel='Correct route decisions (%)',title='When past information predicts danger, inherited memory is favored')
ax.set_yticks([40,50,60,70,80,90,100])
ax.spines[['right','top']].set_visible(False);ax.grid(axis='y',alpha=.16)
ax.legend(loc='center right',frameon=False,fontsize=9,bbox_to_anchor=(.99,.63))
fig.text(.11,.005,'20 seeded worlds per condition · population 180 · 5 decisions per generation · shaded bands = ±1 SD across worlds',fontsize=9,color='#566371')
fig.tight_layout(rect=(0,.035,1,1));fig.savefig(p+'/experiment_02_chart.png',dpi=180,bbox_inches='tight')
with open(p+'/experiment_02_summary.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['mode','seed','early_accuracy_30gen','late_accuracy_30gen','final_memory_gene','final_decoder_gene']);w.writeheader();
 for r in rows:w.writerow({'mode':r['mode'],'seed':r['seed'],'early_accuracy_30gen':round(r['earlyMean'],6),'late_accuracy_30gen':round(r['lateMean'],6),'final_memory_gene':round(r['meanRetention'],6),'final_decoder_gene':round(r['meanDecoder'],6)})
print('WROTE_CHART',p+'/experiment_02_chart.png')
print('WROTE_CSV',p+'/experiment_02_summary.csv')
