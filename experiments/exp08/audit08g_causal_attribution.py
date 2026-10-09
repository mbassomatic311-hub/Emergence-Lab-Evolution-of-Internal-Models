"""Experiment 08G: controlled causal identifiability from sensorimotor feedback.

EXPLORATORY DEVELOPMENT ONLY. No evolution, conscious experience, or novel
self-model is demonstrated. This is a from-scratch experiment independent of
Experiment 08's 13x13 navigation environment.

An observer compares three PRE-DEFINED mechanistic hypotheses, without being
shown true causal labels: ACTUATOR rotation, WORLD drift, VISUAL sensor drift.
The observer is cued that a post-change diagnostic window began; it does not
learn change-point timing autonomously. We investigate when cause is *not*
identifiable, and what sensor/action interventions resolve it.
"""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
import numpy as np

BASE_SEED = 80_800_000
N = 192
STEPS = 12
SIGMA = .18
CLASS_NAMES = ('actuator', 'world', 'visual')
DIRECTIONS = np.array([[1.,0.],[0.,1.],[-1.,0.],[0.,-1.]])
ROTATIONS = np.stack((np.array([[0.,-1.],[1.,0.]]), np.array([[0.,1.],[-1.,0.]])))
# Every 90-degree rotation of a cardinal command yields a drift in this set.
DRIFTS = np.array([(x,y) for x in (-1.,0.,1.) for y in (-1.,0.,1.) if x or y], dtype=float)


def planned_actions(primary, active, steps=STEPS):
    """Intervention schedule fixed in advance; independent of hidden cause."""
    v=np.asarray(primary, dtype=float)
    if not active:return np.tile(v,(steps,1))
    right=np.array([-v[1],v[0]])
    cycle=(v,np.zeros(2),right,v,np.zeros(2),-v,right,-right,
           np.zeros(2),v,-right,np.zeros(2))
    return np.stack([cycle[i%len(cycle)] for i in range(steps)])


def world(seed: int, true_cause: str, *, active=False, reference=True, steps=STEPS, sigma=SIGMA):
    """Generate action/optical-flow readings, never reveal hidden cause to estimator.

    primary and hidden rotation are drawn from the world seed independently of
    true cause; by design all three causes have identical primary visual-flow
    distributions in passive runs, under exactly matched noise samples.
    """
    if true_cause not in CLASS_NAMES:raise ValueError(true_cause)
    rng=np.random.default_rng(seed)
    p=DIRECTIONS[int(rng.integers(4))].copy()
    rotated=ROTATIONS[int(rng.integers(2))]
    b=rotated@p-p
    actions=planned_actions(p,active,steps)
    noise_main=rng.normal(0,sigma,size=(steps,2))
    noise_aux=rng.normal(0,sigma,size=(steps,2))
    observed=[]
    for i,a in enumerate(actions):
        physical=rotated@a if true_cause=='actuator' else a+(b if true_cause=='world' else 0)
        visual_drift=b if true_cause=='visual' else np.zeros(2)
        main=physical+visual_drift+noise_main[i]
        aux=physical+noise_aux[i]
        observed.append(np.r_[main,aux] if reference else main)
    return actions,np.asarray(observed),p,b


def catalog(action, reference):
    """Known hypothesis classes; NO learned or evolved architecture.

    Sensor access is exactly as specified by reference. Candidate parameters
    are not privileged hidden labels, but a manually supplied model family.
    """
    action=np.asarray(action)
    reps={k:[] for k in CLASS_NAMES+('no_change',)}
    reps['no_change'].append(np.c_[action,action] if reference else action)
    for r in ROTATIONS:
        motor=action@r.T
        reps['actuator'].append(np.c_[motor,motor] if reference else motor)
    for drift in DRIFTS:
        motion=action+drift
        reps['world'].append(np.c_[motion,motion] if reference else motion)
        reps['visual'].append(np.c_[action+drift,action] if reference else action+drift)
    return reps


def infer(actions, observations, reference=True, sigma=SIGMA):
    """Class-profile maximum Gaussian likelihood, equal *class score* weights.

    Normalized profile-likelihood supports are NOT calibrated Bayesian
    posteriors: nuisance parameters are maximized instead of integrated.

    Uses a *maximum* rather than marginalizing over unequal hypothesis counts:
    if distinct classes can generate exactly the same readings, no confidence
    preference should arise purely from the number of parameter candidates.
    """
    a=np.asarray(actions,dtype=float); o=np.asarray(observations,dtype=float)
    if len(a)!=len(o) or len(a)<1:raise ValueError('missing data')
    if a.shape[1]!=2 or o.shape[1]!=(4 if reference else 2):raise ValueError('sensor dimensions')
    c=catalog(a,reference)
    scores=[]
    candidates=CLASS_NAMES+('no_change',)
    for k in candidates:
        squared=[np.sum((o-h)**2) for h in c[k]]
        scores.append(-min(squared)/(2*sigma**2))
    s=np.asarray(scores)
    weights=np.exp(s-s.max()); posterior=weights/weights.sum()
    rank=int(np.argmax(posterior))
    # abstain rather than guessing when observations leave hypotheses tied.
    label=candidates[rank] if posterior[rank]>=.8 else 'undetermined'
    return {'label':label,'posterior':dict(zip(candidates,posterior.tolist())),
            'confidence':float(posterior[rank]),'best_fit':candidates[rank]}


def run(n=N, steps=STEPS):
    if n<=0 or steps<4:raise ValueError('invalid study size')
    rows=[]
    for seed in range(BASE_SEED,BASE_SEED+n):
        for active in (False,True):
            for reference in (False,True):
                for truth in CLASS_NAMES:
                    actions,observation,p,b=world(seed,truth,active=active,reference=reference,steps=steps)
                    estimated=infer(actions,observation,reference)
                    rows.append({'seed':seed,'truth':truth,'active_probe':int(active),
                        'second_sensor':int(reference),'estimate':estimated['label'],
                        'argmax':estimated['best_fit'],'confidence':estimated['confidence'],
                        'correct':int(estimated['label']==truth),'resolved':int(estimated['label']!='undetermined'),
                        'argmax_correct':int(estimated['best_fit']==truth),
                        'posterior_true':estimated['posterior'][truth]})
    return rows,aggregate(rows)


def aggregate(rows):
    result={'classification':'EXPLORATORY developmental counterfactual simulator, not preregistered',
        'worlds':len({x['seed'] for x in rows}), 'steps_per_diagnostic':len(planned_actions([1.,0.],True)),
        'classes':list(CLASS_NAMES),'decision_threshold':0.8,'model_hypotheses':list(CLASS_NAMES+('no_change',)),'conditions':{}}
    for act in (0,1):
        for ref in (0,1):
            name=('active' if act else 'passive')+'_'+('dual' if ref else 'single')
            selected=[x for x in rows if x['active_probe']==act and x['second_sensor']==ref]
            result['conditions'][name]={
                'n_trials':len(selected),'mean_accuracy_with_abstention':float(np.mean([x['correct'] for x in selected])),
                'mean_argmax_accuracy':float(np.mean([x['argmax_correct'] for x in selected])),
                'fraction_resolved':float(np.mean([x['resolved'] for x in selected])),
                'accuracy_given_resolution':float(np.mean([x['correct'] for x in selected if x['resolved']])) if any(x['resolved'] for x in selected) else None,
                'mean_true_class_probability':float(np.mean([x['posterior_true'] for x in selected])),
                'confusion':{truth:{pred:sum(x['truth']==truth and x['estimate']==pred for x in selected)
                    for pred in CLASS_NAMES+('no_change','undetermined')} for truth in CLASS_NAMES}}
    return result


def write_outputs(rows,summary,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    with (out/'per_world.csv').open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=rows[0].keys());wr.writeheader();wr.writerows(rows)
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--worlds',type=int,default=N)
    parser.add_argument('--out',default='development_causal08g')
    args=parser.parse_args()
    rows,summary=run(args.worlds)
    write_outputs(rows,summary,args.out)
    for k,v in summary['conditions'].items():
        print(k, 'argmax',round(v['mean_argmax_accuracy'],4), 'resolved',round(v['fraction_resolved'],4), 'accuracy all',round(v['mean_accuracy_with_abstention'],4))

if __name__=='__main__':main()
