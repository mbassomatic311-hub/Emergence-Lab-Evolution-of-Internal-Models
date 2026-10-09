"""Development-only supervised identifiability audit for Experiment 08.

IMPORTANT: true hidden actuator rotation labels are used in OFFLINE TRAINING.
This is NOT evolutionary learning, ecological fitness, emergent selfhood, or
an externally registered confirmatory study. Agents in test rollouts do not
access these labels.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from controllers import _desired, ComparatorController, BayesianController
from engine import simulate
from world2d import World, WorldConfig, OBS_DIM

DEV_SEEDS = (1103, 1205, 1411)
T = 48


def generate_data(n, split='train'):
    """Generate policy-independent, labeled development exploration traces.

    Mapping label corresponds to effective rotation at decision time, taking
    into account the unannounced reversal occurring INSIDE World.step().
    """
    offsets={'train':9_000_000,'validation':9_200_000,'stable':9_400_000,'shift':9_600_000}
    assert split in offsets
    rng_policy=np.random.default_rng(offsets[split]+37)
    X=np.zeros((n,T,OBS_DIM));Y=np.zeros((n,T),dtype=int);valid=np.zeros((n,T),dtype=bool)
    config=WorldConfig(reversal=split=='shift',dropout_probability=.12 if split=='shift' else 0.)
    for i in range(n):
        seed=offsets[split] + DEV_SEEDS[i%len(DEV_SEEDS)] + 397*i
        w=World(seed,config)
        for t in range(T):
            # Never stitch unrelated lifetimes into a single neural sequence.
            # Padding after death is ignored by training loss and accuracy.
            if w.done: break
            obs=w.observe()
            Y[i,t]=(w.rotation+2)%4 if w.cfg.reversal and w.t==T//2 else w.rotation
            X[i,t]=obs
            valid[i,t]=True
            action=_desired(obs) if rng_policy.random()<.55 else int(rng_policy.integers(4))
            w.step(action)
    return X,Y,valid


def inputs_for(model,X):
    if model!='history':return X
    prev=np.concatenate([np.zeros_like(X[:,:1,:]), X[:,:-1,:]],axis=1)
    return np.concatenate([X,prev],axis=-1)


def initialize(model,rng):
    if model=='recurrent':
        h=8
        return {'wi':rng.normal(0,.24,(OBS_DIM,h)), 'wr':rng.normal(0,.14,(h,h)),
                'bh':np.zeros(h),'wo':rng.normal(0,.2,(h,4)),'bo':np.zeros(4)}
    if model in ('history','memoryless'):
        d,h=(OBS_DIM*2,7) if model=='history' else (OBS_DIM,12)
        return {'wi':rng.normal(0,.20,(d,h)), 'bh':np.zeros(h),
                'wo':rng.normal(0,.20,(h,4)),'bo':np.zeros(4)}
    raise ValueError(model)


def forward(model,p,X):
    Z=inputs_for(model,X)
    if model!='recurrent':
        H=np.tanh(Z@p['wi']+p['bh'])
    else:
        h=np.zeros((len(X),p['bh'].size)); hs=[]
        for t in range(X.shape[1]):
            h=np.tanh(X[:,t]@p['wi']+h@p['wr']+p['bh']); hs.append(h)
        H=np.stack(hs,axis=1)
    logits=H@p['wo']+p['bo']
    return logits,H,Z


def loss_and_grad(model,p,X,Y,valid=None):
    logits,H,Z=forward(model,p,X)
    shifted=logits-logits.max(axis=-1,keepdims=True)
    probs=np.exp(shifted); probs/=probs.sum(axis=-1,keepdims=True)
    flat=probs.reshape(-1,4)
    labels=Y.ravel()
    weights=valid.astype(float).ravel() if valid is not None else np.ones(len(labels))
    loss=-np.sum(np.log(np.maximum(flat[np.arange(len(labels)),labels],1e-12))*weights)/weights.sum()
    d=probs.copy().reshape(-1,4)
    d[np.arange(len(labels)),labels]-=1
    d=(d*weights[:,None]).reshape(probs.shape)/weights.sum()
    grad={'wo':np.einsum('nth,ntk->hk',H,d),'bo':d.sum(axis=(0,1))}
    dh=d@p['wo'].T
    if model!='recurrent':
        dpre=dh*(1-H**2)
        grad['wi']=np.einsum('ntd,nth->dh',Z,dpre)
        grad['bh']=dpre.sum(axis=(0,1))
    else:
        grad['wi']=np.zeros_like(p['wi']);grad['wr']=np.zeros_like(p['wr']);grad['bh']=np.zeros_like(p['bh'])
        incoming=np.zeros_like(H[:,0])
        for t in range(X.shape[1]-1,-1,-1):
            dt=(dh[:,t]+incoming)*(1-H[:,t]**2)
            grad['wi']+=X[:,t].T@dt
            if t>0:grad['wr']+=H[:,t-1].T@dt
            grad['bh']+=dt.sum(axis=0)
            incoming=dt@p['wr'].T
    return float(loss),grad


def fit(model,X,Y,W,seed,epochs=36,batch=24,lr=.013):
    rng=np.random.default_rng(seed)
    p=initialize(model,rng)
    m={k:np.zeros_like(v) for k,v in p.items()};v={k:np.zeros_like(x) for k,x in p.items()}
    beta1=.9;beta2=.999;step=0
    curve=[]
    for epoch in range(epochs):
        idx=rng.permutation(len(X)); losses=[]
        for start in range(0,len(idx),batch):
            ids=idx[start:start+batch]
            loss,grad=loss_and_grad(model,p,X[ids],Y[ids],W[ids]);losses.append(loss)
            total=np.sqrt(sum((g*g).sum() for g in grad.values()))
            if total>4:
                grad={k:g*(4/total) for k,g in grad.items()}
            step+=1
            for k in p:
                m[k]=beta1*m[k]+(1-beta1)*grad[k]
                v[k]=beta2*v[k]+(1-beta2)*grad[k]**2
                p[k]-=lr*(m[k]/(1-beta1**step))/(np.sqrt(v[k]/(1-beta2**step))+1e-8)
        curve.append(float(np.mean(losses)))
    return p,curve


def predict(model,p,X):return np.argmax(forward(model,p,X)[0],axis=-1)


def accuracy(model,p,X,Y,W):
    preds=predict(model,p,X)
    def scored(idx):
        matches=(preds[:,idx]==Y[:,idx])
        valid=W[:,idx]
        return float(np.sum(matches*valid)/np.sum(valid)) if np.sum(valid) else None
    return {'accuracy':scored(slice(None)),
            'first_6':scored(slice(0,6)),
            'after_shift_early':scored(slice(24,30)),
            'after_shift_late':scored(slice(30,None)),
            'n_valid_steps':int(np.sum(W))}


class TrainedEstimator:
    """Actuator mapping classifier composed with a fixed greedy goal policy.

    No privileged world state at deployment. Supervision *during training* is
    privileged and makes this a diagnostic reference, not an evolved baseline.
    """
    def __init__(self,model,p,epsilon=.06):
        self.model=model; self.p=p; self.prev_obs=np.zeros(OBS_DIM)
        self.h=np.zeros(len(p['bh']));self.epsilon=epsilon
    def act(self,obs,rng):
        if self.model=='recurrent':
            self.h=np.tanh(obs@self.p['wi']+self.h@self.p['wr']+self.p['bh'])
            logits=self.h@self.p['wo']+self.p['bo']
        else:
            inputs=np.concatenate([obs,self.prev_obs]) if self.model=='history' else obs
            hidden=np.tanh(inputs@self.p['wi']+self.p['bh'])
            logits=hidden@self.p['wo']+self.p['bo']
        rot=int(np.argmax(logits)); cmd=(_desired(obs)-rot)%4
        if rng.random()<self.epsilon:cmd=int(rng.integers(4))
        self.prev_obs=obs.copy()
        return cmd


def rollout_scores(model,p,n=36):
    result={}
    for env in ('stable','shift+dropout'):
        scores=[]
        for i in range(n):
            seed=9_800_000+DEV_SEEDS[i%3]+397*i
            scores.append(simulate(TrainedEstimator(model,p),seed,env=env)[0])
        result[env]=float(np.mean(scores))
    return result


def reference_scores(n=36):
    r={}
    for name,cls in [('comparator',ComparatorController),('bayesian',BayesianController)]:
        r[name]={}
        for env in ('stable','shift+dropout'):
            scores=[]
            for i in range(n):
                seed=9_800_000+DEV_SEEDS[i%3]+397*i
                scores.append(simulate(cls(),seed,env=env)[0])
            r[name][env]=float(np.mean(scores))
    return r

# Deliberately keep the following separate from the study's trained models;
# it is an explanatory, hand-coded identifiability diagnostic.
def offline_action_outcome_reference(X, valid, transition=.06, noise=.55):
    """Bayesian 4-state observer, given only present and preceding observations.

    Uses the same information as a two-frame neural policy and NO true label.
    Unlike BayesianController, it is evaluated on third-party exploration traces
    with recorded (not self-chosen) actions.
    """
    from world2d import ACT
    result=np.zeros(X.shape[:2],dtype=int)
    for i in range(len(X)):
        p=np.full(4,.25)
        for t in range(X.shape[1]):
            if not valid[i,t]: continue
            now=X[i,t]
            if (t>0 and valid[i,t-1] and now[-1] and X[i,t-1,-1]
                    and not now[-3] and not now[-2]):
                last_onehot=now[7:11]
                if np.sum(last_onehot)>.5:
                    action=int(np.argmax(last_onehot))
                    displacement=(X[i,t-1,:2]-now[:2])*6
                    expected=ACT[np.array([(action+k)%4 for k in range(4)])]
                    dif=np.sum((expected-displacement)**2,axis=1)
                    logl=-dif/(2*noise**2)
                    likelihood=np.exp(logl-logl.max())
                    prior=(1-transition)*p+transition*.25
                    post=prior*likelihood
                    p=post/post.sum()
            result[i,t]=int(p.argmax())
    return result



def offline_reference_diagnostics(X,Y,W,seed):
    good=offline_action_outcome_reference(X,W)
    altered=X.copy()
    rng=np.random.default_rng(seed)
    # For each time step randomly permute action-copy flags among episodes,
    # holding bearings, physical dynamics and ground-truth labels unchanged.
    # This is a post-hoc informational ablation, not a realizable intervention.
    for t in range(1,X.shape[1]):
        altered[:,t,7:11]=X[rng.permutation(len(X)),t,7:11]
    corrupt=offline_action_outcome_reference(altered,W)
    return {'intact_accuracy':float(np.sum((good==Y)*W)/W.sum()),
            'scrambled_action_copy_accuracy':float(np.sum((corrupt==Y)*W)/W.sum()),
            'n_valid_decisions':int(W.sum()),
            'majority_class_prior':int(np.argmax(np.bincount(Y[W],minlength=4))),
            'majority_class_accuracy':float(np.max(np.bincount(Y[W],minlength=4))/W.sum()),
            'hidden_rotation_label_histogram':np.bincount(Y[W],minlength=4).tolist()}


def study(train_n=192,val_n=48,test_n=72,epochs=36,rollout_n=36,seed=80808):
    X,Y,W=generate_data(train_n,'train')
    V,VY,VW=generate_data(val_n,'validation')
    A,AY,AW=generate_data(test_n,'stable')
    B,BY,BW=generate_data(test_n,'shift')
    summary={'status':'EXPLORATORY development only; supervised hidden-state labels are privileged at training',
             'train_episodes':train_n,'validation_episodes':val_n,'test_episodes_per_world':test_n,
             'training_epochs':epochs,'pilot_rollout_episodes_per_world':rollout_n,
             'models':{},'reference_rollouts':reference_scores(rollout_n),
             'offline_observation_identifiability':{
                'stable':offline_reference_diagnostics(A,AY,AW,85001),
                'shift+dropout':offline_reference_diagnostics(B,BY,BW,85002)}}
    weights={}
    for i,name in enumerate(('memoryless','history','recurrent')):
        p,curve=fit(name,X,Y,W,seed+100*i,epochs=epochs)
        weights[name]=p
        summary['models'][name]={
            'trainable_parameters':int(sum(np.size(q) for q in p.values())),
            'last_train_loss':curve[-1],
            'validation':accuracy(name,p,V,VY,VW),
            'stable':accuracy(name,p,A,AY,AW),
            'shift+dropout':accuracy(name,p,B,BY,BW),
            'policy_food':rollout_scores(name,p,rollout_n),
            'loss_curve':curve}
    return summary,weights


def main():
    a=argparse.ArgumentParser()
    a.add_argument('--out',default='development_identifiability_08c')
    a.add_argument('--train',type=int,default=192)
    a.add_argument('--val',type=int,default=48)
    a.add_argument('--test',type=int,default=72)
    a.add_argument('--epochs',type=int,default=36)
    a.add_argument('--rollout',type=int,default=36)
    opts=a.parse_args()
    if opts.train>500 or opts.test>150 or opts.rollout>120:raise ValueError('development-only sampling caps')
    summary,weights=study(opts.train,opts.val,opts.test,opts.epochs,opts.rollout)
    path=Path(opts.out);path.mkdir(parents=True,exist_ok=True)
    (path/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (path/'weights.json').write_text(json.dumps({k:{x:y.tolist() for x,y in p.items()} for k,p in weights.items()},indent=2)+'\n')
    print(json.dumps({k:{z:v for z,v in q.items() if z!='loss_curve'} for k,q in summary['models'].items()},indent=2))
    print('Hand-designed references:',summary['reference_rollouts'])

if __name__=='__main__':main()
