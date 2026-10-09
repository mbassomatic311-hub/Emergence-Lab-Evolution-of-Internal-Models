"""Development-only probe of baseline dependence on sensor fidelity."""
import csv,json
from pathlib import Path
import numpy as np
from world2d import WorldConfig
from controllers import RandomController,GreedyController,ComparatorController,BayesianController
from engine import simulate,DEV_SEEDS


def main():
    out=Path('development_diagnostics');out.mkdir(exist_ok=True)
    rows=[]
    conditions={
      'normal':WorldConfig(reversal=True,dropout_probability=.12),
      'corrupted':WorldConfig(reversal=True,dropout_probability=.35,observation_noise=.07,gust_probability=.18,hazard_slip=.28)
    }
    ctls={'random':RandomController,'greedy':GreedyController,'one_step':ComparatorController,'bayesian':BayesianController}
    for seed in DEV_SEEDS[:3]:
        for condition,cfg in conditions.items():
            for name,cls in ctls.items():
                outcomes=[simulate(cls(),seed+1200000+i*733,config=cfg) for i in range(12)]
                rows.append({'seed':seed,'condition':condition,'agent':name,'food':float(np.mean([o[0] for o in outcomes])),'survival':float(np.mean([o[1] for o in outcomes]))})
    with (out/'sensor_stress_pilot.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    summary={c:{a:float(np.mean([r['food'] for r in rows if r['condition']==c and r['agent']==a])) for a in ctls} for c in conditions}
    (out/'sensor_stress_summary.json').write_text(json.dumps({'status':'Exploratory development seeds only','means':summary},indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
