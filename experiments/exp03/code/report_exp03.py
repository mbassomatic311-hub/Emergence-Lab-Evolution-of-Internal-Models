import json,csv,statistics as st,math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from collections import defaultdict
P=Path('/mnt/data/consciousness_lab')
rows=json.loads((P/'experiment_03_results.json').read_text())
modes=['evolve','locked','scrambled','no_loop','nonheritable']
labels={'evolve':'Evolved structural memory','locked':'Structural mutations blocked','scrambled':'Warnings random','no_loop':'Feedback disabled','nonheritable':'Inheritance blocked'}
with (P/'experiment_03_summary.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=['condition','seed','mean_accuracy_last40','final_accuracy','final_complete_circuit_fraction','final_useful_circuit_fraction','first_complete_generation','first_majority_generation','first_90percent_generation']);w.writeheader()
 for r in rows:w.writerow({'condition':r['mode'],'seed':r['seed'],'mean_accuracy_last40':round(r['lateAccuracy'],6),'final_accuracy':round(r['finalAccuracy'],6),'final_complete_circuit_fraction':round(r['finalComplete'],6),'final_useful_circuit_fraction':round(r['finalUseful'],6),'first_complete_generation':r['firstComplete'],'first_majority_generation':r['firstMajority'],'first_90percent_generation':r['first90']})
colors={'evolve':'#16a085','locked':'#b67952','scrambled':'#7b70ba','no_loop':'#c55178','nonheritable':'#567a94'}
fig,ax=plt.subplots(figsize=(10.5,5.5))
for mode in modes:
 series=defaultdict(list)
 for r in rows:
  if r['mode']!=mode:continue
  for point in r['history']:series[point['gen']].append(point['accuracy']*100)
 ts=sorted(series);m=[st.mean(series[t]) for t in ts];dev=[st.stdev(series[t]) for t in ts]
 ax.plot(ts,m,lw=3.2 if mode=='evolve' else 1.7,label=labels[mode],color=colors[mode])
 if mode=='evolve':ax.fill_between(ts,[v-d for v,d in zip(m,dev)],[v+d for v,d in zip(m,dev)],color=colors[mode],alpha=.15,label='Evolving worlds ±1 SD')
ax.axhline(50,color='#6d7885',linestyle=':',linewidth=1)
ax.set_xlim(0,400);ax.set_ylim(40,103)
ax.set_xlabel('Generation');ax.set_ylabel('Correct choices (%)')
ax.set_title('Mutations assemble a working memory circuit under selective pressure',fontsize=14,pad=12)
ax.spines[['top','right']].set_visible(False);ax.grid(axis='y',alpha=.15)
ax.legend(loc='center right',frameon=False,fontsize=9)
fig.text(.105,.006,'20 seeded worlds per condition · 180 agents · 7 choices per generation · same model across all conditions',fontsize=9,color='#6d7885')
fig.tight_layout(rect=(0,.035,1,1))
fig.savefig(P/'experiment_03_results_chart.png',dpi=170,bbox_inches='tight')
# paired differences and rough confidence intervals (between synthetic seeds not real-world generalization)
by={m:{r['seed']:r for r in rows if r['mode']==m} for m in modes}
print('FILES',P/'experiment_03_results_chart.png',P/'experiment_03_summary.csv')
for m in modes:
 a=[r['lateAccuracy'] for r in by[m].values()]
 ci=2.093*st.stdev(a)/math.sqrt(len(a))
 print(m,'n',len(a),'mean late accuracy',round(st.mean(a)*100,3),'CI approx',round((st.mean(a)-ci)*100,3),round((st.mean(a)+ci)*100,3),'final circuit%',round(st.mean([r['finalComplete'] for r in by[m].values()])*100,3))
for m in modes[1:]:
 ds=[by['evolve'][k]['lateAccuracy']-by[m][k]['lateAccuracy'] for k in by['evolve']]
 print('paired improvement evolve vs',m,round(st.mean(ds)*100,2),'pp')
