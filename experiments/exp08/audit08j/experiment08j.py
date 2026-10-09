"""Experiment 08J: development-only learning-to-probe in nonlinear sensory world.

No hidden state, cause label or change time is given to a policy/model.
The physical simulator is reused from the prior (researcher-authored) Exp08I,
NOT an independent world or an experiment on subjective consciousness.
"""
from __future__ import annotations
import argparse
import copy
import csv
import json
import sys
from pathlib import Path
import numpy as np

# Research repository layout: experiments/exp08/audit08i, audit08j.
# Local development layout: /mnt/data/exp08i, /mnt/data/exp08j.
LOCAL = Path(__file__).resolve().parent.parent
REPO = Path(__file__).resolve().parent.parent / 'audit08i'
if REPO.is_dir():
    sys.path.insert(0,str(REPO))
else:
    sys.path.insert(0,str(LOCAL / 'exp08i'))
from experiment08i import ACTIONS, CAUSES, TOTAL, NonlinearWorld, OnlineRLS, KNNPredictor, features

POLICIES=('uncertainty','random','cycle','least_seen','single_action','no_probes')
PROBE_STEPS=tuple(range(0,TOTAL,5))  # predeclared, 30 slots/150 steps
TEST_TIMES=(110,125,140)  # common reference contexts, after possible change


def policy_action(policy,step,learner,ranges,counts,rng):
    if policy not in POLICIES:raise ValueError('Unrecognized probe policy')
    if step not in PROBE_STEPS or policy=='no_probes':return 0
    if policy=='random':return int(rng.integers(1,5))
    if policy=='cycle':return (1,3,2,4)[(step//5)%4]
    if policy=='single_action':return 1
    if policy=='least_seen':
        xs=np.flatnonzero(counts[1:]==np.min(counts[1:]))+1
        return int(rng.choice(xs))
    # Greedy approximate parameter information: expected feature covariance
    # reduction for action u is increasing in f(u)^T P f(u). No causal oracle.
    vals=[]
    for a in range(1,5):
        f=features('nonlinear',ranges,ACTIONS[a])
        vals.append(float(f @ learner.p @ f))
    choices=np.flatnonzero(np.isclose(vals,np.max(vals),rtol=1.e-12,atol=1.e-12))+1
    return int(rng.choice(choices))


def fixed_test_battery(seed,cause,noise):
    """Evaluator-only reference contexts identical for all competing policies.

    Same physics parameters/seed as each policy's world but with a fixed and
    policy-independent trajectory. None of these outcomes train any agent.
    """
    w=NonlinearWorld(seed,cause,noise,reference=True)
    y=w.begin();battery=[]
    for t in range(TOTAL):
        if t in TEST_TIMES:
            tests=[]
            for a in range(len(ACTIONS)):
                alternative=copy.deepcopy(w)
                yn,z=alternative.step(a)
                tests.append((a,np.r_[yn-y,z]))
            battery.append((t,y.copy(),tests))
        yn,_=w.step((1,3,2,4,0)[t%5])
        y=yn
    return battery


def train_one(seed,cause,policy,noise=.025):
    world=NonlinearWorld(seed,cause,noise,reference=True)
    rng=np.random.default_rng(seed+70439)
    model=OnlineRLS('nonlinear',reference=True)
    knn=KNNPredictor('knn_recent',reference=True)
    counts=np.zeros(5,dtype=np.int64)
    y=world.begin()
    early=[]; late=[]; trace=[]
    for t in range(TOTAL):
        action=policy_action(policy,t,model,y,counts,rng)
        pred=model.predict(y,ACTIONS[action])[:4]
        yn,z=world.step(action)
        actual=np.r_[yn-y,z]
        # PREQUENTIAL: error is computed before any update using this outcome.
        error=float(np.mean((pred-actual[:4])**2))
        if 80<=t<105:early.append(error)
        if 120<=t<150:late.append(error)
        model.update(y,ACTIONS[action],actual.copy())
        knn.update(y,ACTIONS[action],actual.copy())
        counts[action]+=1
        trace.append(action)
        y=yn
    return model,knn,{'prequential_early':float(np.mean(early)),
                      'prequential_late':float(np.mean(late)),
                      'nonzero_probes':int(sum(a!=0 for a in trace)),
                      'distinct_probe_commands':int(sum(counts[1:]>0)),
                      'action_counts':counts.tolist(),
                      'action_trace':trace}


def score_model(model,battery,which='rls'):
    rng_score=[]; inertial_score=[]; by_action={a:[] for a in range(5)}
    for _,y,tests in battery:
        for action,actual in tests:
            p=model.predict(y,ACTIONS[action])
            e=float(np.mean((p[:4]-actual[:4])**2))
            rng_score.append(e)
            inertial_score.append(float(np.mean((p[4:]-actual[4:])**2)))
            by_action[action].append(e)
    return {'range_mse':float(np.mean(rng_score)),
            'inertial_mse':float(np.mean(inertial_score)),
            'counterfactual_by_action':{str(k):float(np.mean(v)) for k,v in by_action.items()}}


def run(nseeds=24,noise=.025):
    rows=[]
    for idx in range(nseeds):
        seed=11_800_041+idx*137  # new development namespace, not confirmatory
        for cause in CAUSES:
            battery=fixed_test_battery(seed,cause,noise)
            for policy in POLICIES:
                learner,knn,metrics=train_one(seed,cause,policy,noise)
                r=score_model(learner,battery)
                k=score_model(knn,battery)
                rows.append({'seed':seed,'cause':cause,'policy':policy,
                             'noise':noise,'range_mse':r['range_mse'],
                             'inertial_mse':r['inertial_mse'],
                             'knn_range_mse':k['range_mse'],
                             'prequential_early':metrics['prequential_early'],
                             'prequential_late':metrics['prequential_late'],
                             'nonzero_probes':metrics['nonzero_probes'],
                             'distinct_probe_commands':metrics['distinct_probe_commands'],
                             'action_counts':json.dumps(metrics['action_counts']),
                             'counterfactual_by_action':json.dumps(r['counterfactual_by_action'],sort_keys=True)})
    return rows,analyze(rows,nseeds,noise)


def analyze(rows,nseeds,noise):
    summary={'status':'EXPLORATORY development only; unregistered; no consciousness measure',
             'n_seed_clusters':nseeds,'noise':noise,'causes':list(CAUSES),
             'probe_slots':len(PROBE_STEPS),'policies':list(POLICIES),
             'common_context_times':list(TEST_TIMES),
             'average':{}}
    for policy in POLICIES:
        rr=[r for r in rows if r['policy']==policy]
        summary['average'][policy]={k:float(np.mean([r[k] for r in rr])) for k in
                  ('range_mse','inertial_mse','knn_range_mse','prequential_early',
                   'prequential_late','nonzero_probes','distinct_probe_commands')}
    for metric in ('range_mse','knn_range_mse'):
        summary['average_by_cause_'+metric]={p:{c:float(np.mean([r[metric] for r in rows if r['policy']==p and r['cause']==c])) for c in CAUSES} for p in POLICIES}
    # Seed-cluster bootstrap, source of uncertainty = Monte Carlo world sampling.
    diffs=[]
    for seed in sorted({r['seed'] for r in rows}):
        for baseline in ('random','cycle','least_seen','single_action'):
            a=np.mean([r['range_mse'] for r in rows if r['seed']==seed and r['policy']=='uncertainty'])
            b=np.mean([r['range_mse'] for r in rows if r['seed']==seed and r['policy']==baseline])
            diffs.append((seed,baseline,float(a-b)))
    rng=np.random.default_rng(1108)
    pairs={}
    for base in ('random','cycle','least_seen','single_action'):
        ds=np.array([v for _,n,v in diffs if n==base])
        bs=rng.choice(ds,size=(5000,len(ds)),replace=True).mean(axis=1)
        pairs[base]={'mean_active_minus_baseline':float(ds.mean()),
                     'ci95_exploratory_seed_bootstrap':[float(x) for x in np.quantile(bs,[.025,.975])],
                     'active_better_seeds':int(np.sum(ds<0)),
                     'active_worse_seeds':int(np.sum(ds>0)),
                     'ties':int(np.sum(ds==0))}
    summary['paired_contrasts']=pairs
    return summary


def save(out,rows,summary):
    p=Path(out);p.mkdir(parents=True,exist_ok=True)
    with (p/'per_world.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0].keys()));w.writeheader();w.writerows(rows)
    (p/'summary.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--seeds',type=int,default=24)
    ap.add_argument('--noise',type=float,default=.025)
    ap.add_argument('--out',default='development')
    args=ap.parse_args()
    if args.seeds<1:raise ValueError('positive seed count required')
    rows,summary=run(args.seeds,args.noise)
    save(args.out,rows,summary)
    print(json.dumps({'seeds':args.seeds,'noise':args.noise,'average':summary['average'],
                      'paired_contrasts':summary['paired_contrasts']},indent=2))

if __name__=='__main__':main()
