import json,statistics as st,math
from collections import defaultdict
r=json.load(open('/mnt/data/consciousness_lab/test_results.json')) + json.load(open('/mnt/data/consciousness_lab/memoryless_results.json'))
by={m:{x['seed']:x for x in r if x['mode']==m} for m in ('evolve','random','blind','memoryless')}
for m,group in by.items():
 vals=list(group.values())
 pop=[x['population'] for x in vals]
 damage_rate=[]
 for x in vals:
  h=x['history']
  exposure=sum((h[i]['t']-h[i-1]['t'])*(h[i]['n']+h[i-1]['n'])/2 for i in range(1,len(h)))
  damage_rate.append(x['hazardHits']*1000/exposure)
 print(f'{m}: end population mean {st.mean(pop):.1f} SD {st.stdev(pop):.1f}, min {min(pop)}, max {max(pop)}, hazard encounters /1000 agent-time {st.mean(damage_rate):.2f}')
 for trait,idx in [('food',0),('risk',1),('persistence',2),('reward-memory',3)]:
  print('  '+trait+': '+str(round(st.mean(x['meanGenes'][idx] for x in vals),3)))
for other in ('random','blind','memoryless'):
 diffs=[by['evolve'][s]['population']-by[other][s]['population'] for s in by['evolve']]
 ci=(st.mean(diffs)-1.96*st.stdev(diffs)/math.sqrt(len(diffs)),st.mean(diffs)+1.96*st.stdev(diffs)/math.sqrt(len(diffs)))
 print(f'paired evolve-{other} population delta: {st.mean(diffs):.1f}, rough normal 95% CI {ci}')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size':11})
fig,ax=plt.subplots(figsize=(8.6,4.6))
names=['Heritable + mutation','Non-heritable control','Blind sensing','No memory']
means=[st.mean(x['population'] for x in by[m].values()) for m in by]
sd=[st.stdev(x['population'] for x in by[m].values()) for m in by]
xs=range(4)
ax.bar(xs,means,color=['#278b83','#8797a7','#b88661','#7c73b2'])
ax.errorbar(xs,means,yerr=sd,fmt='none',ecolor='black',capsize=5)
ax.set_xticks(list(xs),names)
ax.set_ylabel('Living agents after 1,000 steps')
ax.set_title('Population outcome across 10 random worlds per condition')
ax.text(0.99,0.98,'Bars = mean   ·   whiskers = ±1 SD',transform=ax.transAxes,ha='right',va='top',color='#58636e',fontsize=9)
ax.spines[['top','right']].set_visible(False)
ax.set_ylim(0,575)
for i,m in enumerate(means):ax.text(i,m+sd[i]+12,f'{m:.1f}',ha='center',fontsize=11,fontweight='bold')
fig.tight_layout()
fig.savefig('/mnt/data/consciousness_lab/results_chart.png',dpi=180,bbox_inches='tight')
print('CHART_SAVED /mnt/data/consciousness_lab/results_chart.png')
