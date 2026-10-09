"""Exploratory robustness and out-of-model falsification checks for Exp08G."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from audit08g_causal_attribution import (BASE_SEED,CLASS_NAMES,DRIFTS,DIRECTIONS,
    ROTATIONS,SIGMA,planned_actions,world,infer,catalog)


def hybrid_world(seed, cause, steps=12, sigma=SIGMA):
    """Unknown combined cause/unchanged baseline. Same seed noise across causes."""
    if cause not in ('actuator_plus_wind','world_plus_visual','none'):
        raise ValueError(cause)
    rng=np.random.default_rng(seed)
    p=DIRECTIONS[int(rng.integers(4))]
    rotated=ROTATIONS[int(rng.integers(2))]
    b=rotated@p-p
    actions=planned_actions(p,True,steps)
    main_noise=rng.normal(0,sigma,(steps,2));aux_noise=rng.normal(0,sigma,(steps,2))
    if cause=='actuator_plus_wind':movement=actions@rotated.T+b;extra=np.zeros(2)
    elif cause=='world_plus_visual':movement=actions+b;extra=b
    else:movement=actions;extra=np.zeros(2)
    return actions,np.c_[movement+extra+main_noise,movement+aux_noise]


def profile_mse(actions,observations,reference=True):
    options=catalog(actions,reference)
    return float(min(np.mean((observations-predicted)**2) for candidates in options.values() for predicted in candidates))


def run(n=192):
    if n<1:raise ValueError('worlds must be positive')
    sweep=[];unmodeled=[]
    for seed in range(BASE_SEED+10000,BASE_SEED+10000+n):
        for noise in (.18,.5,1.0):
            for steps in (4,6,12):
                for truth in CLASS_NAMES:
                    actions,readings,_,_=world(seed,truth,active=True,reference=True,steps=steps,sigma=noise)
                    result=infer(actions,readings,reference=True,sigma=noise)
                    sweep.append({'seed':seed,'noise_sigma':noise,'steps':steps,'truth':truth,
                        'resolved':int(result['label']!='undetermined'),
                        'correct':int(result['label']==truth),
                        'support':result['confidence'],
                        'mse':profile_mse(actions,readings)})
        for truth in ('actuator_plus_wind','world_plus_visual','none'):
            a,o=hybrid_world(seed,truth)
            x=infer(a,o)
            residual=profile_mse(a,o)
            unmodeled.append({'seed':seed,'truth':truth,'label':x['label'],
                'relative_support':x['confidence'],'mse':residual,
                'resolved':int(x['label']!='undetermined'),
                'labeled_no_change':int(x['label']=='no_change'),
                'reject_model_at_mse_0_2':int(residual>.2)})
    summary={'classification':'EXPLORATORY sensitivity analysis after initial dev results, not preregistered',
             'world_seeds':n,'class_definitions_engineered':True,
             'model_fit_rejection_rule':'absolute residual MSE > 0.2 (heuristic, post-hoc)',
             'sweep':{},'out_of_family':{}}
    for noise in (.18,.5,1.0):
        for steps in (4,6,12):
            subset=[x for x in sweep if x['noise_sigma']==noise and x['steps']==steps]
            summary['sweep'][f'sigma_{noise}_steps_{steps}']={
                'n':len(subset), 'fraction_correct_and_resolved':float(np.mean([x['correct'] for x in subset])),
                'fraction_resolved':float(np.mean([x['resolved'] for x in subset])),
                'mean_profile_mse':float(np.mean([x['mse'] for x in subset]))}
    for truth in ('actuator_plus_wind','world_plus_visual','none'):
        subset=[x for x in unmodeled if x['truth']==truth]
        summary['out_of_family'][truth]={
            'n':len(subset),
            'fraction_resolved_without_fit_check':float(np.mean([x['resolved'] for x in subset])),
            'fraction_correct_null':float(np.mean([x['labeled_no_change'] for x in subset])) if truth=='none' else None,
            'rejected_by_post_hoc_mse_0_2':float(np.mean([x['reject_model_at_mse_0_2'] for x in subset])),
            'mean_mse':float(np.mean([x['mse'] for x in subset]))}
    return sweep,unmodeled,summary


def save(out,sweep,unmodeled,summary):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    for name,rows in [('noise_sweep.csv',sweep),('outside_model.csv',unmodeled)]:
        with (out/name).open('w',newline='') as f:
            writer=csv.DictWriter(f,rows[0].keys());writer.writeheader();writer.writerows(rows)
    (out/'stress_summary.json').write_text(json.dumps(summary,indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--worlds',type=int,default=192)
    p.add_argument('--out',default='development_causal08g')
    a=p.parse_args();q=run(a.worlds);save(a.out,*q)
    print(json.dumps(q[2],indent=2))
