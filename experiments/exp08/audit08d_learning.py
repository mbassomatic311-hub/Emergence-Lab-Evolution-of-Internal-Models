"""Experiment 08D exploratory developmental audit: learned structured action-effect model.

No conscious-state measure. Hidden actuator mapping is used as *privileged offline
supervision* for forward-model prototypes; never provided to a deployed agent.
Development-only seeds, not a publicly preregistered confirmatory study.
"""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
import numpy as np
from world2d import World, WorldConfig, ACT, OBS_DIM
from engine import simulate
from controllers import _desired, BayesianController, ComparatorController
from audit08c_learning import initialize, fit, accuracy, T

DEV_SEEDS = (1103,1205,1411)
# These namespaces are *development data*, not confirmatory data. Nonoverlapping.
SEED_OFFSETS={
    'train_stable':14_000_000,'train_shift':15_000_000, 'train_stable_aug':20_000_000,
    'validation_shift':16_000_000,'development_test_stable':17_000_000,
    'development_test_shift':18_000_000}
ROLLOUT_OFFSET=19_000_000


def create_traces(n, group):
    """A trajectory per episode, no stitched lifetimes, no data leakage across splits.

    Hidden label is the rotation currently in effect at the start of observation,
    NOT the future rotation imposed by an unseen reversal inside next World.step.
    This corrects a target leakage-like temporal ambiguity of Experiment 08C.
    """
    if group not in SEED_OFFSETS: raise ValueError('unknown development split')
    base=SEED_OFFSETS[group]
    rng=np.random.default_rng(base+39)
    X=np.zeros((n,T,OBS_DIM),dtype=float)
    Y=np.zeros((n,T),dtype=int)
    W=np.zeros((n,T),dtype=bool)
    seeds=[]
    config=WorldConfig(reversal=('shift' in group),dropout_probability=.12 if 'shift' in group else 0.)
    for i in range(n):
        seed=base+DEV_SEEDS[i%3]+397*i
        seeds.append(seed)
        world=World(seed,config)
        for t in range(T):
            if world.done:break
            ob=world.observe()
            X[i,t]=ob;Y[i,t]=world.rotation;W[i,t]=True
            action=_desired(ob) if rng.random()<.55 else int(rng.integers(4))
            world.step(action)
    return X,Y,W,seeds


def transitions(X,Y,W):
    """Observed consecutive target-relative displacement, conditioned on action.

    Excludes target respawn, collision and sensor dropout from clean emission fit.
    The label at t-1 is the rotation governing step t-1, except when reversal
    occurs *inside* that step. Exclude reversal step (t=25 in 48-step world)
    using known development protocol so labels cannot be assigned incorrectly.
    """
    d=[]; labels=[]; acts=[]
    for i in range(len(X)):
        for t in range(1,T):
            now=X[i,t];prev=X[i,t-1]
            if not (W[i,t] and W[i,t-1] and now[-1] and prev[-1]):continue
            if now[-3] or now[-2]:continue  # food relocation or collision
            if not np.isclose(np.sum(now[7:11]),1):continue
            if t==T//2+1 and Y[i,t]!=Y[i,t-1]:continue  # ambiguous switch at prev step
            d.append((prev[:2]-now[:2])*6.)
            labels.append(int(Y[i,t-1]));acts.append(int(np.argmax(now[7:11])))
    return np.asarray(d),np.asarray(labels,dtype=int),np.asarray(acts,dtype=int)


def fit_prototypes(X,Y,W,regularize=0.):
    """Learn 4x4 displacement prototypes using labeled development trajectories.

    A geometric regularization prior is optional but defaults to ZERO. Even with
    no such prior, the four discrete states, labeled supervision, conditional
    feature structure and Bayesian update are engineered. This is NOT
    'emergent physics' or spontaneous cognitive development.
    """
    steps,y,a=transitions(X,Y,W)
    if len(y)<100:raise ValueError('insufficient clean development transitions')
    counts=np.zeros((4,4),dtype=int); means=np.zeros((4,4,2),dtype=float)
    for rot in range(4):
        for action in range(4):
            selected=steps[(y==rot)&(a==action)]
            counts[rot,action]=len(selected)
            # Retain a *transparent* geometric prior, so sparse classes stay stable.
            prior=ACT[(action+rot)%4].astype(float)
            means[rot,action]=(selected.sum(axis=0)+regularize*prior)/(len(selected)+regularize)
    errors=steps-means[y,a]
    scale=float(np.sqrt(np.mean(np.sum(errors**2,axis=1))/2))
    return {'means':means,'scale':max(scale,.15),'counts':counts,'clean_transitions':len(y)}


def infer_posterior(X,W,model, hazard=.06,memory=True,scramble=False,seed=0):
    """Online causal filter on traces: observation history and previous action only.

    Scramble controls replace recorded previous command across trajectories at
    equal time index. This is an *information ablation*, not a physical rollout.
    """
    means=model['means']; sigma=model['scale']
    rng=np.random.default_rng(seed)
    flags=X[:,:,7:11].copy()
    if scramble:
        for t in range(1,X.shape[1]):
            flags[:,t,:]=X[rng.permutation(len(X)),t,7:11]
    guesses=np.zeros(X.shape[:2],dtype=int)
    prob=np.empty((len(X),X.shape[1],4))
    for i in range(len(X)):
        p=np.full(4,.25)
        for t in range(X.shape[1]):
            if not W[i,t]: continue
            prior=(1-hazard)*p+hazard*.25 if memory else np.full(4,.25)
            if (t>0 and W[i,t-1] and X[i,t,-1]>0.5 and X[i,t-1,-1]>.5 and
                    X[i,t,-3]<.5 and X[i,t,-2]<.5 and flags[i,t].sum()>.5):
                cmd=int(np.argmax(flags[i,t]))
                step=(X[i,t-1,:2]-X[i,t,:2])*6.
                errors=np.sum((means[:,cmd]-step)**2,axis=1)
                ll=-errors/(2*max(sigma,.28)**2)
                like=np.exp(ll-ll.max())
                p=prior*like;p/=p.sum()
            else:
                p=prior
            guesses[i,t]=int(np.argmax(p));prob[i,t]=p
    return guesses,prob


def score(pred,Y,W):
    parts={'overall':W,'pre_shift':W & (np.arange(T)[None,:] <24),
           'first_6_after_shift':W & (np.arange(T)[None,:]>=25) & (np.arange(T)[None,:]<31),
           'late_after_shift':W & (np.arange(T)[None,:]>=31)}
    return {k:{'n':int(v.sum()),'accuracy':float(np.sum((pred==Y)&v)/v.sum()) if v.sum() else None} for k,v in parts.items()}

class LearnedForwardController:
    """Learned supervised action->displacement prototypes and online Bayes update.
    Does NOT receive hidden mapping at deployment, but fit received labels.
    """
    def __init__(self,model,hazard=.06,epsilon=.06):
        self.means=model['means'];self.sigma=max(model['scale'],.28)
        self.hazard=hazard;self.epsilon=epsilon
        self.p=np.full(4,.25);self.prev=None;self.command=None
    def act(self,obs,rng):
        prior=(1-self.hazard)*self.p+self.hazard*.25
        if (self.prev is not None and self.command is not None and self.prev[-1]>.5
            and obs[-1]>.5 and obs[-3]<.5 and obs[-2]<.5):
            difference=(self.prev[:2]-obs[:2])*6.
            errors=np.sum((self.means[:,self.command]-difference)**2,axis=1)
            ll=-errors/(2*self.sigma**2)
            like=np.exp(ll-ll.max())
            self.p=prior*like;self.p/=self.p.sum()
        else:self.p=prior
        direction=_desired(obs);action=(direction-int(np.argmax(self.p)))%4
        if rng.random()<self.epsilon:action=int(rng.integers(4))
        self.prev=obs.copy();self.command=action
        return int(action)


def policy_benchmark(model,n=36):
    results={}
    for name,factory in [('learned_forward',lambda:LearnedForwardController(model)),
                         ('analytic_bayesian',lambda:BayesianController()),
                         ('analytic_comparator',lambda:ComparatorController())]:
        results[name]={}
        for env in ('stable','shift+dropout'):
            vals=[]
            for i in range(n):
                seed=ROLLOUT_OFFSET+DEV_SEEDS[i%3]+397*i
                vals.append(float(simulate(factory(),seed,env=env)[0]))
            results[name][env]={'n':n,'mean_food':float(np.mean(vals)),'median_food':float(np.median(vals)),
                                'fraction_zero':float(np.mean(np.array(vals)==0)), 'episode_food':vals}
    return results


def run(train_n=192,shift_n=192,test_n=72,validation_n=48,epochs=36,policy_n=36):
    A,AY,AW,aseeds=create_traces(train_n,'train_stable')
    B,BY,BW,bseeds=create_traces(shift_n,'train_shift')
    C,CY,CW,cseeds=create_traces(shift_n,'train_stable_aug')
    V,VY,VW,vseeds=create_traces(validation_n,'validation_shift')
    S,SY,SW,sseeds=create_traces(test_n,'development_test_stable')
    D,DY,DW,dseeds=create_traces(test_n,'development_test_shift')
    assert len(set(aseeds+bseeds+cseeds+vseeds+sseeds+dseeds))==sum(map(len,[aseeds,bseeds,cseeds,vseeds,sseeds,dseeds]))
    datasets={'stable_only':(A,AY,AW), 'stable_matched_size':(np.concatenate([A,C]),np.concatenate([AY,CY]),np.concatenate([AW,CW])), 'mixed_training':(np.concatenate([A,B]),np.concatenate([AY,BY]),np.concatenate([AW,BW]))}
    report={'status':'EXPLORATORY DEVELOPMENT ONLY, not preregistered or confirmatory',
       'important_training_privilege':'True motor rotation labels used in offline supervised training; no hidden labels at deployment',
       'temporal_label':'Rotation at observation time, NOT unknowable after upcoming step reversal',
       'sample_counts':{'stable_train':train_n,'shift_train':shift_n,'extra_stable_train':shift_n,'validation_shift':validation_n,
                        'development_test_shift':test_n,'development_test_stable':test_n,'policy_rollouts':policy_n},
       'seed_ranges':{k:[int(min(v)),int(max(v))] for k,v in [('stable_train',aseeds),('shift_train',bseeds),('extra_stable_train',cseeds),('validation',vseeds),('test_stable',sseeds),('test_shift',dseeds)]},
       'structured':{},'neural':{},'neural_initializations':{},'references':{},'prior_sensitivity':{}}
    for key,(X,Y,W) in datasets.items():
        mod=fit_prototypes(X,Y,W)
        pred,_=infer_posterior(D,DW,mod)
        single,_=infer_posterior(D,DW,mod,memory=False)
        scrambled,_=infer_posterior(D,DW,mod,scramble=True,seed=82008)
        report['structured'][key]={'parameters':{'prototype_means':mod['means'].round(7).tolist(),
                  'estimated_sigma':float(mod['scale']),'class_counts':mod['counts'].tolist(),
                  'n_training_clean_transitions':int(mod['clean_transitions'])},
             'validation':score(infer_posterior(V,VW,mod)[0],VY,VW),
             'test_stable':score(infer_posterior(S,SW,mod)[0],SY,SW),
             'test_shift':score(pred,DY,DW),
             'test_shift_no_memory':score(single,DY,DW),
             'test_shift_action_scrambled':score(scrambled,DY,DW),
             'policy_food':policy_benchmark(mod,policy_n)}
    for strength in (0.,4.,100.):
        prior_model=fit_prototypes(A,AY,AW,regularize=strength)
        report['prior_sensitivity'][str(strength)]={
            'test_shift_accuracy':score(infer_posterior(D,DW,prior_model)[0],DY,DW)['overall']['accuracy'],
            'training_transitions':int(prior_model['clean_transitions'])}
    # Supervised neural diagnostic: fixed baseline size/training epochs, broaden training distribution.
    # Training-size differences are clearly declared, so DO NOT interpret as perfectly matched comparison.
    for label,(X,Y,W) in datasets.items():
        report['neural'][label]={}
        for model in ('memoryless','history','recurrent'):
            instances=[]
            for ix,seed in enumerate((80011,80022,80033)):
                pars,curve=fit(model,X,Y,W,seed+(0 if model=='memoryless' else 1000 if model=='history' else 2000),
                               epochs=epochs,batch=24)
                row={'seed':seed, 'n_params':int(sum(np.size(q) for q in pars.values())),
                     'last_train_loss':float(curve[-1]),
                     'shift':score(np.argmax(_forward_logits(model,pars,D),axis=-1),DY,DW),
                     'validation':score(np.argmax(_forward_logits(model,pars,V),axis=-1),VY,VW)}
                instances.append(row)
            report['neural'][label][model]={'initializations':instances,
               'mean_shift_accuracy':float(np.mean([r['shift']['overall']['accuracy'] for r in instances])),
               'min_shift_accuracy':float(min(r['shift']['overall']['accuracy'] for r in instances)),
               'max_shift_accuracy':float(max(r['shift']['overall']['accuracy'] for r in instances))}
    for k in ('development_test_stable','development_test_shift'):
        XX,YY,WW= (S,SY,SW) if k.endswith('stable') else (D,DY,DW)
        counts=np.bincount(YY[WW],minlength=4)
        report['references'][k]={'n_valid_steps':int(WW.sum()),'majority_class_accuracy':float(counts.max()/WW.sum()),'hist':counts.tolist()}
    return report


def _forward_logits(model,params,X):
    from audit08c_learning import forward
    return forward(model,params,X)[0]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',default='development_learning08d')
    parser.add_argument('--stable-train',type=int,default=192)
    parser.add_argument('--shift-train',type=int,default=192)
    parser.add_argument('--test',type=int,default=72)
    parser.add_argument('--val',type=int,default=48)
    parser.add_argument('--epochs',type=int,default=36)
    parser.add_argument('--policy',type=int,default=36)
    args=parser.parse_args()
    if any((args.stable_train>500,args.shift_train>500,args.test>150,args.val>150,args.policy>150)):
        raise ValueError('development only data caps')
    result=run(args.stable_train,args.shift_train,args.test,args.val,args.epochs,args.policy)
    dest=Path(args.out);dest.mkdir(parents=True,exist_ok=True)
    (dest/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    with (dest/'model_comparisons.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['training','model','init_seed','test_shift_accuracy','first6_after_shift','late_after_shift'])
        for training,models in result['neural'].items():
            for model,spec in models.items():
                for r in spec['initializations']:
                    w.writerow([training,model,r['seed'],r['shift']['overall']['accuracy'],
                                r['shift']['first_6_after_shift']['accuracy'],r['shift']['late_after_shift']['accuracy']])
        for training,spec in result['structured'].items():
            for model_key,label in [('test_shift','learned_forward'),('test_shift_no_memory','learned_no_history'),
                                    ('test_shift_action_scrambled','action_scrambled')]:
                outcome=spec[model_key]
                w.writerow([training,label,'n/a',outcome['overall']['accuracy'],
                   outcome['first_6_after_shift']['accuracy'],outcome['late_after_shift']['accuracy']])
    with (dest/'policy_episode_results.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['training','controller','environment','development_world_seed','food'])
        for training,spec in result['structured'].items():
            for controller,envs in spec['policy_food'].items():
                for env,metrics in envs.items():
                    for i,value in enumerate(metrics['episode_food']):
                        w.writerow([training,controller,env,ROLLOUT_OFFSET+DEV_SEEDS[i%3]+397*i,value])
    print(json.dumps({'structured':{k:{'shift_accuracy':v['test_shift']['overall']['accuracy'],
                  'ablation_accuracy':v['test_shift_action_scrambled']['overall']['accuracy'],
                  'policy_food':v['policy_food']} for k,v in result['structured'].items()},
                 'neural':{k:{n:r['mean_shift_accuracy'] for n,r in v.items()} for k,v in result['neural'].items()}},indent=2))

if __name__=='__main__':main()
