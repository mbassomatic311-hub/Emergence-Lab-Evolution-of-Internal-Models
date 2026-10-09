"""Explicit post-pilot stress checks. All seeds are exploratory development seeds."""
from __future__ import annotations
import argparse,csv,json
from pathlib import Path
import numpy as np
from exp08h import CAUSES,run_world

SEED_START=9_120_000

def main():
    p=argparse.ArgumentParser();p.add_argument('--seeds',type=int,default=48);p.add_argument('--out',default='stress');opt=p.parse_args()
    rows=[]
    for i in range(opt.seeds):
        seed=SEED_START+53*i
        for noise in (.13,.35,.65):
            for reference in (True,False):
                for policy in ('adaptive','cycle'):
                    for detector in (False,True):
                        for cause in CAUSES:
                            rows.append(run_world(seed,cause,policy,noise,reference,detector))
    summary={}
    for noise in (.13,.35,.65):
        for reference in (True,False):
            for policy in ('adaptive','cycle'):
              for detector in ('fixed','calibrated'):
                r=[x for x in rows if x['noise']==noise and x['reference']==int(reference) and x['policy']==policy and x['detector']==detector]
                k=f'{noise:.2f}/'+('two_sensors' if reference else 'one_sensor')+'/'+policy+'/'+detector
                normal=[x for x in r if x['cause'] not in ('none','nonlinear')]
                novel=[x for x in r if x['cause']=='nonlinear']
                unchanged=[x for x in r if x['cause']=='none']
                external_sensor=[x for x in r if x['cause'] in ('external','sensor')]
                summary[k]={
                    'exact_cause_accuracy':float(np.mean([x['correct'] for x in normal])),
                    'coverage':float(np.mean([x['identified'] for x in normal])),
                    'external_sensor_correct':float(np.mean([x['correct'] for x in external_sensor])),
                    'nonlinear_unknown_rate':float(np.mean([x['diagnosis']=='unknown' for x in novel])),
                    'false_alarm_rate':float(np.mean([x['alarm'] for x in unchanged])),
                    'mean_counterfactual_mse':float(np.mean([x['counterfactual_mse'] for x in normal])),
                    'avg_probe_cost':float(np.mean([x['probe_cost'] for x in r])),
                    'n_synthetic_worlds':len(r)
                }
    out=Path(opt.out);out.mkdir(parents=True,exist_ok=True)
    with (out/'per_world.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (out/'summary.json').write_text(json.dumps({'status':'post-pilot exploratory stress test','seeds':opt.seeds,'conditions':summary},indent=2,sort_keys=True)+'\n')
    for k,v in summary.items():print(k, 'exact',round(v['exact_cause_accuracy'],3),'novel unknown',round(v['nonlinear_unknown_rate'],3),'false alarm',round(v['false_alarm_rate'],3))
if __name__=='__main__':main()
