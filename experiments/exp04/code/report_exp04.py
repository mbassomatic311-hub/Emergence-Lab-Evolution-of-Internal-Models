from pathlib import Path
import json,csv,statistics as stats
from matplotlib import pyplot as plt
from matplotlib.ticker import PercentFormatter
base=Path('/mnt/data/consciousness_lab')
all=json.loads((base/'experiment_04_results.json').read_text())
with open(base/'experiment_04_summary.csv','w',newline='') as f:
 w=csv.writer(f)
 w.writerow(['environment','generation','icons_share_pct','detailed_share_pct','adaptive_share_pct','blind_share_pct','seeded_runs'])
 for item in all:
  name=item['summary']['scenario'];traces=item['frequencies'];num=len(traces)
  for g in range(160):
   avg=[sum(t[g][i] for t in traces)/num*100 for i in range(4)]
   w.writerow([name,g+1,*[f'{x:.4f}' for x in avg],num])
fig,axes=plt.subplots(1,3,figsize=(12,3.7),sharey=True,layout='constrained')
labels=['Simplified icons','Detailed sensing','Switching','Random']
scenarios=['stable','variable','shock']
for ax,item,title in zip(axes,all,['Stable environment','Changing conditions','Stable → changing']):
 traces=item['frequencies'];num=len(traces)
 for i,label in enumerate(labels):
  data=[sum(t[g][i] for t in traces)/num for g in range(160)]
  ax.plot(range(1,161),data,label=label,linewidth=1.9)
 if item['summary']['scenario']=='shock': ax.axvline(80,ls='--',lw=1,alpha=.65)
 ax.set_title(title,fontsize=11)
 ax.set_xlabel('Generation')
 ax.set_xlim(0,160);ax.set_ylim(0,1);ax.grid(alpha=.2)
axes[0].set_ylabel('Mean population share')
axes[0].yaxis.set_major_formatter(PercentFormatter(1))
handles,labels=axes[-1].get_legend_handles_labels()
fig.legend(handles,labels,loc='outside lower center',ncol=4,frameon=False)
fig.suptitle('Evolution of perceptual strategies · 24 independent worlds each',fontsize=13)
fig.savefig(base/'experiment_04_results_chart.png',dpi=160,bbox_inches='tight')
plt.close(fig)
for item in all:
 scen=item['summary']['scenario'];n=item['summary']['runs'];tr=item['frequencies']
 print(scen,'runs',n,'at 80',item['summary']['at80'],'at 160',item['summary']['final'])
print('OUTPUT_FILES',[(p.name,p.stat().st_size) for p in [base/'experiment_04_perception.html',base/'experiment_04_results_chart.png',base/'experiment_04_summary.csv']])
