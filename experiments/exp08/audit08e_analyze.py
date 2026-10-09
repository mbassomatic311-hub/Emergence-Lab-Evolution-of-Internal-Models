"""Post-hoc descriptive uncertainty analysis for 08E, clustered at world seed."""
import argparse,csv,json
from pathlib import Path
import numpy as np

PAIR_PROBES=[('action_model','shuffled_action'),('action_model','action_blind'),('action_model','reset_memory')]
PAIR_NAV=[('action_model','greedy'),('action_model','comparator'),('action_model','bayesian'),('action_model','shuffled_action')]

def paired_ci(diff,seed=82508,replicates=20000):
    diff=np.asarray(diff,dtype=float)
    if not np.isfinite(diff).all():raise ValueError('Nonfinite diff')
    rng=np.random.default_rng(seed)
    means=np.array([diff[rng.integers(len(diff),size=len(diff))].mean() for _ in range(replicates)])
    return {'n_worlds':len(diff),'mean':float(diff.mean()),'bootstrap_95':[float(x) for x in np.quantile(means,[.025,.975])],
            'positive_worlds':int((diff>0).sum()),'negative_worlds':int((diff<0).sum()),'ties':int((diff==0).sum())}

def analyze(probes,nav):
    out={'status':'POST-HOC DESCRIPTIVE CLUSTER BOOTSTRAP, exploratory only',
         'unit':'simulated world seed (not timestep, not a biological organism)',
         'probe_pairs':{},'navigation_pairs':{}}
    ps={(int(r['seed']),r['kind']):r for r in probes}
    ns={(int(r['seed']),r['environment'],r['controller']):r for r in nav}
    for a,b in PAIR_PROBES:
        for phase in ('pre','post'):
            seeds=sorted(set(s for s,k in ps if k==a)&set(s for s,k in ps if k==b))
            diff=[float(ps[s,a][phase+'_mse'])-float(ps[s,b][phase+'_mse']) for s in seeds
                  if ps[s,a][phase+'_mse'] and ps[s,b][phase+'_mse']]
            out['probe_pairs'][f'{a}_minus_{b}_{phase}_mse']=paired_ci(diff)
    for a,b in PAIR_NAV:
        for env in ('stable','shift+dropout'):
            seeds=sorted(set(s for s,e,k in ns if k==a and e==env)&set(s for s,e,k in ns if k==b and e==env))
            dif=[int(ns[s,env,a]['food'])-int(ns[s,env,b]['food']) for s in seeds]
            out['navigation_pairs'][f'{a}_minus_{b}_{env}_food']=paired_ci(dif)
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--data-dir',default='development_selfsupervised08e')
    args=p.parse_args();folder=Path(args.data_dir)
    def read(f):
        with (folder/f).open(newline='') as io:return list(csv.DictReader(io))
    result=analyze(read('probe_per_seed.csv'),read('navigation_per_seed.csv'))
    (folder/'exploratory_intervals.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
