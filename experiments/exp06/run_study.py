"""Run frozen protocol, produce CSV/JSON and figure data. No training labels. """
from __future__ import annotations
import argparse,csv,json,pathlib
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np
from scipy.stats import rankdata
from engine import Settings,evolve,expected_payoff,test_agent,analytic_bound,sensor_output

OUT=pathlib.Path(__file__).resolve().parent
SEEDS=[100003+101*i for i in range(24)]
MODES=('evolve','no_recurrence','random_fitness','no_inheritance')

def calc_auc(y,score):
    y=np.asarray(y);score=np.asarray(score)
    ranks=rankdata(score,method='average')
    n1=int((y==1).sum());n0=len(y)-n1
    return float((ranks[y==1].sum()-n1*(n1+1)/2)/(n0*n1))

def worker(params):
    seed,mode,generations=params
    cfg=Settings(generations=generations)
    a=evolve(seed,cfg,mode)
    p=a['plain'][None,:];r=a['rec'][None,:,:];mask=a['mask'][None,:,:]
    off=expected_payoff(p,r,mask,q=.92,retained=False,recurrent_cost=0)[0]
    q80=expected_payoff(p,r,mask,q=.80,recurrent_cost=0)[0]
    q50=expected_payoff(p,r,mask,q=.50,recurrent_cost=0)[0]
    q08=expected_payoff(p,r,mask,q=.08,recurrent_cost=0)[0]
    orig=expected_payoff(p,r,mask,q=.92,recurrent_cost=0)[0]
    held=test_agent(a,.92,seed+4_000_000, N=25000)
    scrambled=test_agent(a,.92,seed+4_000_000,N=25000,control='scramble_memory')
    auc=calc_auc(held['source'],held['prediction'])
    cues=np.array([-1,-1,1,1]);signals=np.array([-1,1,-1,1])
    q,_=sensor_output(p,r,mask,cues,signals)
    summary=dict(seed=seed,mode=mode, exact_payoff=float(orig),selection_payoff=a['selection_score'],
                 no_memory_payoff=float(off),q80_payoff=float(q80),q50_payoff=float(q50),
                 q08_payoff=float(q08),mc_payoff=held['payoff'],scrambled_payoff=scrambled['payoff'],
                 agency_auc=auc, active_links=a['active_links'],p_negneg=float(q[0,0]),
                 p_negpos=float(q[0,1]),p_posneg=float(q[0,2]),p_pospos=float(q[0,3]))
    agent=dict(seed=seed, mode=mode, plain=a['plain'].tolist(),rec=a['rec'].tolist(),mask=a['mask'].astype(int).tolist())
    return summary,a['trace'],agent

def bootstrap_ci(values, rng, B=12000):
    a=np.asarray(values,dtype=float)
    samples=rng.integers(0,len(a),size=(B,len(a)))
    means=a[samples].mean(axis=1)
    return [float(np.quantile(means,.025)),float(np.quantile(means,.975))]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--workers',type=int,default=4)
    parser.add_argument('--generations',type=int,default=300)
    args=parser.parse_args()
    jobs=[(seed,mode,args.generations) for mode in MODES for seed in SEEDS]
    summaries=[]; traces={};champions={}
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for i,(summary,trace,agent) in enumerate(pool.map(worker,jobs),1):
            summaries.append(summary)
            k=f"{summary['mode']}_{summary['seed']}"
            traces[k]=trace; champions[k]=agent
            if i%12==0: print(f'Completed {i}/{len(jobs)} independent evolutionary runs',flush=True)
    summaries.sort(key=lambda x:(x['mode'],x['seed']))
    with open(OUT/'results_per_seed.csv','w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(summaries[0]));w.writeheader();w.writerows(summaries)
    (OUT/'traces.json').write_text(json.dumps(traces,separators=(',',':')))
    (OUT/'champions.json').write_text(json.dumps(champions,separators=(',',':')))
    rng=np.random.default_rng(58333)
    groups={mode:[s for s in summaries if s['mode']==mode] for mode in MODES}
    metrics={}
    for mode,rows in groups.items():
        metrics[mode]={}
        for key in ('exact_payoff','mc_payoff','scrambled_payoff','agency_auc','active_links','q80_payoff','q50_payoff','q08_payoff'):
            arr=np.array([s[key] for s in rows])
            metrics[mode][key]={'mean':float(arr.mean()), 'sd':float(arr.std(ddof=1)), 'ci95':bootstrap_ci(arr,rng),'min':float(arr.min()), 'max':float(arr.max())}
    reference=np.array([s['exact_payoff'] for s in groups['evolve']])
    metrics['paired_differences']={}
    for mode in MODES[1:]:
        null=np.array([s['exact_payoff'] for s in groups[mode]])
        v=reference-null
        metrics['paired_differences'][f'evolve_minus_{mode}']={'mean':float(v.mean()),'ci95':bootstrap_ci(v,rng), 'n_positive':int((v>0).sum())}
    abl=np.array([s['no_memory_payoff'] for s in groups['evolve']])
    metrics['paired_differences']['evolve_minus_memory_ablated']={'mean':float((reference-abl).mean()), 'ci95':bootstrap_ci(reference-abl,rng)}
    metrics['protocol']={'n_seeds':len(SEEDS),'generations':args.generations,'oracle_bound':analytic_bound(.92),'source_balanced':True,'pilot_seeds_excluded':[5,13,14,21,44], 'external_preregistration':False}
    (OUT/'metrics.json').write_text(json.dumps(metrics,indent=2))
    print('\nPrimary results:')
    for mode in MODES:
        x=metrics[mode]
        print(f'{mode:16} score {x["exact_payoff"]["mean"]:+.4f} 95% bootstrap {x["exact_payoff"]["ci95"]} agency AUC {x["agency_auc"]["mean"]:.3f} links {x["active_links"]["mean"]:.2f}')
    print('Paired:',metrics['paired_differences'])
    return metrics

if __name__=='__main__':main()
