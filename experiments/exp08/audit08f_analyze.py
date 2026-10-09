"""Post-hoc descriptive analysis of Experiment 08F developmental results.

Tests treat independently seeded worlds as experimental units, NOT per-step
prediction errors. Interpret all intervals as exploratory and task-specific.
"""
from pathlib import Path
import csv,json
import numpy as np
from audit08f_change import paired_bootstrap

def load_csv(p):return list(csv.DictReader(open(p,newline='')))

def analyze(directory='development_change08f'):
    base=Path(directory)
    a=load_csv(base/'alarm_per_world.csv')
    n=load_csv(base/'navigation_per_world.csv')
    alarms={}
    for changed in ('0','1'):
        x=[r for r in a if r['mode']=='surprise_reset' and r['shifted']==changed]
        steps=[int(z) for row in x for z in row['alarm_steps'].split('|') if z]
        alarms[changed]={'worlds':len(x),'worlds_any_alarm':sum(int(r['n_alarms'])>0 for r in x),
                         'alarms_pre_change_boundary':sum(v<=24 for v in steps),
                         'alarms_after_change_boundary':sum(v>=25 for v in steps),
                         'median_post_change_detection_delay':float(np.median([v-24 for v in steps if v>=25])) if any(v>=25 for v in steps) else None}
    p={ (int(r['seed']),r['shifted'],r['mode']):float(r['food']) for r in n }
    seeds=sorted(set(int(r['seed']) for r in n if r['shifted']=='1'))
    comparison={}
    for other in ('slow','fast','adaptive_gain','memoryless','bayesian','comparator','greedy'):
        comparison[f'surprise_reset_minus_{other}']=paired_bootstrap([p[(s,'1','surprise_reset')]-p[(s,'1',other)] for s in seeds])
    return {'analysis_status':'POST-HOC, exploratory only; no significance/novelty/consciousness claim',
            'n_worlds':len(seeds),'alarm_diagnostic':alarms,
            'paired_shifted_navigation_differences':comparison}

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--data-dir',default='development_change08f')
    args=p.parse_args();result=analyze(args.data_dir)
    (Path(args.data_dir)/'exploratory_intervals.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
