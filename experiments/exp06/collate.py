from pathlib import Path
import csv,json,hashlib
import numpy as np
from scipy.stats import rankdata
from run_study import SEEDS,MODES,bootstrap_ci
from engine import analytic_bound
D=Path(__file__).resolve().parent
rundir=D/'runs'
records={}
for mode in MODES:
 for seed in SEEDS:
  path=rundir/f'{mode}_{seed}.json'
  if not path.exists(): raise RuntimeError(f'Missing {path}; cannot label study complete')
  x=json.loads(path.read_text()); records[f'{mode}_{seed}']=x
rows=[records[f'{mode}_{seed}']['summary'] for mode in MODES for seed in SEEDS]
with open(D/'results_per_seed.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(D/'traces.json').write_text(json.dumps({k:v['trace'] for k,v in records.items()},separators=(',',':')))
(D/'champions.json').write_text(json.dumps({k:v['agent'] for k,v in records.items()},separators=(',',':')))
rng=np.random.default_rng(58333)
groups={mode:[records[f'{mode}_{seed}']['summary'] for seed in SEEDS] for mode in MODES}
m={}
for mode, rr in groups.items():
 m[mode]={}
 for key in ('exact_payoff','mc_payoff','scrambled_payoff','agency_auc','active_links','q80_payoff','q50_payoff','q08_payoff'):
  arr=np.array([z[key] for z in rr]);m[mode][key]={'mean':float(arr.mean()),'sd':float(arr.std(ddof=1)), 'ci95':bootstrap_ci(arr,rng),'min':float(arr.min()),'max':float(arr.max())}
ref=np.array([s['exact_payoff'] for s in groups['evolve']])
m['paired_differences']={}
for mode in MODES[1:]:
 v=ref-np.array([s['exact_payoff'] for s in groups[mode]])
 m['paired_differences'][f'evolve_minus_{mode}']={'mean':float(v.mean()),'ci95':bootstrap_ci(v,rng),'n_positive':int((v>0).sum())}
abl=np.array([s['no_memory_payoff'] for s in groups['evolve']])
m['paired_differences']['evolve_minus_memory_ablated']={'mean':float((ref-abl).mean()),'ci95':bootstrap_ci(ref-abl,rng)}
m['protocol']={'n_seeds':len(SEEDS),'generations':300,'oracle_bound':analytic_bound(.92),'source_balanced':True,'pilot_seeds_excluded':[5,13,14,21,44], 'external_preregistration':False}
(D/'metrics.json').write_text(json.dumps(m,indent=2))
print('RESULTS')
for mode in MODES:
 x=m[mode];print(mode,'payoff',round(x['exact_payoff']['mean'],5),'CI',x['exact_payoff']['ci95'],'AUC',round(x['agency_auc']['mean'],3),'links',round(x['active_links']['mean'],2))
print('paired',m['paired_differences'])
print('CHECK montecarlo absmax',max(abs(s['mc_payoff']-s['exact_payoff']) for s in rows))
print('SUCCESS',sum(s['exact_payoff']>.15 for s in groups['evolve']),'of',len(SEEDS),'runs above .15')
