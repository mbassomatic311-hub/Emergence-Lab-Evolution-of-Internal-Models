"""Creates one developmental error-trajectory chart, no inferential status."""
import json
from pathlib import Path
import matplotlib.pyplot as plt
root=Path(__file__).resolve().parent/'development_change08f'
s=json.loads((root/'summary.json').read_text())['world_level_mse']
phases=['before_change','after_change_early','after_change_late']
fig,ax=plt.subplots(figsize=(10,5.7))
for name,lab in [('slow','Slow EMA'),('fast','Fast EMA'),('adaptive_gain','Adaptive gain'),('surprise_reset','Surprise reset'),('memoryless','No memory')]:
 ax.plot(phases,[s[f'{name}_1_{t}']['mean_of_world_mse'] for t in phases],marker='o',linewidth=2,label=lab)
ax.set_ylim(0,2.65)
ax.set_ylabel('Mean squared sensory prediction error (per world)')
ax.set_title('Experiment 08F • Development-only predictions after motor reversal')
ax.legend(ncol=2,fontsize=9)
ax.grid(axis='y',alpha=.3)
fig.text(.5,.02,'144 simulated development worlds · Models and thresholds hand-designed · Not a consciousness measure',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.05,1,1))
fig.savefig(root/'prediction_error.png',dpi=170)
plt.close(fig)
