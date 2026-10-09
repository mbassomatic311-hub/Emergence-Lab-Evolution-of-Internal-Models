"""Experiment 08I — unlabeled prequential prediction in an independently coded nonlinear toy world.

EXPLORATORY / development only. This is not an agent consciousness test.
The predictor's observable inputs are landmark ranges, its own command, and
(optional) externally supplied *noisy* inertial outcome of previous motion.
It never receives position, true force, change labels, change time, or cause.
"""
from __future__ import annotations
import argparse
import copy
import csv
import json
from pathlib import Path
import numpy as np

ANCHORS = np.array([[-5.,-3.],[5.,-4.],[-3.,6.],[5.,5.]])
ACTIONS = np.array([[0.,0.],[1.,0.],[-1.,0.],[0.,1.],[0.,-1.]])
CAUSES = ('none','motor','external','sensor','motor_external','unknown_nonlinear')
MODELS = ('zero','linear','nonlinear','action_blind','adaptive_nonlinear','knn_all','knn_recent')
TOTAL = 150

class NonlinearWorld:
    """Nonlinear range measurements and position-dependent motor response.

    No exact x-y positions, beacon locations, or causal class are shown to models.
    This is purpose-built physics, NOT an independently authored ecosystem.
    """
    def __init__(self, seed:int, cause:str, noise:float=.025, reference:bool=True):
        if cause not in CAUSES:raise ValueError(cause)
        self.rng=np.random.default_rng(seed)
        self.cause=cause;self.noise=noise;self.reference=reference
        self.pos=self.rng.uniform(-1.,1.,size=2)
        self.rot=int(self.rng.integers(4))
        self.change_at=int(self.rng.integers(70,80))
        th=self.rng.uniform(0,2*np.pi)
        self.current=.23*np.array([np.cos(th),np.sin(th)])
        self.bias=.75*self.rng.choice([-1.,1.])
        self.u_noise=self.rng.normal(0,.014,(TOTAL,2))
        self.s_noise=self.rng.normal(0,noise,(TOTAL+1,4))
        self.z_noise=self.rng.normal(0,noise,(TOTAL,2))
        self.t=0

    def distances(self,t:int):
        truth=np.sqrt(((ANCHORS-self.pos)**2).sum(axis=1)+.36)
        y=truth+self.s_noise[t].copy()
        if self.cause=='sensor' and t>=self.change_at:
            y[0]+=self.bias
        return y

    def begin(self):
        return self.distances(0)

    def step(self, action_index:int):
        if not 0<=action_index<len(ACTIONS):raise ValueError('action invalid')
        if self.t>=TOTAL:raise RuntimeError('episode ended')
        action=ACTIONS[action_index]
        t=self.t
        p=self.pos.copy()
        angle=np.pi/2*(self.rot+(int(t>=self.change_at and self.cause in ('motor','motor_external'))))
        rot=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])
        # The actuator's magnitude is state-dependent, so range increments are
        # nonlinear in command and prior range observations.
        gain=.37*(1+.28*np.sin(.58*p[0]-.33*p[1]))
        delta=rot@action*gain
        delta+=.027*np.array([np.sin(.73*p[1]),np.cos(.51*p[0])])
        if t>=self.change_at and self.cause in ('external','motor_external'):
            delta+=self.current
        if t>=self.change_at and self.cause=='unknown_nonlinear':
            delta+=.17*np.array([np.cos(.8*p[1])*abs(action[0]),np.sin(.9*p[0])*abs(action[1])])
        delta+=self.u_noise[t]
        self.pos=np.clip(self.pos+delta,-6.,6.)
        physical=self.pos-p
        y=self.distances(t+1)
        z=physical+self.z_noise[t] if self.reference else None
        self.t+=1
        return y,z


def features(kind:str,ranges:np.ndarray,action:np.ndarray):
    """Assumed generic feature vocabularies; not learned architectural invention."""
    # Center/scale ranges purely as an engineering inductive bias.
    r=np.tanh((ranges-7.)/5.)
    if kind=='linear': return np.r_[1.,action]
    if kind in ('nonlinear','adaptive_nonlinear'):
        return np.r_[1.,action,r,action[0]*r,action[1]*r]
    if kind=='action_blind':
        # Number of features deliberately matches nonlinear (15).
        return np.r_[1.,r,r**2,r**3, np.sin(r[:2])]
    if kind=='zero':return np.zeros(1)
    raise ValueError(kind)

class KNNPredictor:
    """Model-free local memory, vectorized for fair reproducible runs.

    Matched action, nearest previous observed range patterns; no truth access.
    No outcome for an untried action can be predicted without an assumption.
    """
    def __init__(self,kind:str,reference=True):
        self.kind=kind;self.reference=reference;self.alarms=0;self.n=0
        self.commands=np.empty((TOTAL,2),dtype=float)
        self.ranges=np.empty((TOTAL,4),dtype=float)
        self.outcomes=np.empty((TOTAL,6),dtype=float)
    def predict(self,ranges,action):
        start=max(0,self.n-40) if self.kind=='knn_recent' else 0
        acts=self.commands[start:self.n]
        matching=np.flatnonzero(np.all(acts==action,axis=1))+start
        if not len(matching):return np.zeros(6)
        distances=np.mean((self.ranges[matching]-ranges[None,:])**2,axis=1)
        inds=np.argsort(distances,kind='stable')[:min(7,len(matching))]
        weights=1./(.12+distances[inds])
        return np.average(self.outcomes[matching[inds]],weights=weights,axis=0)
    def update(self,ranges,action,outcome):
        i=self.n
        if i>=TOTAL:raise RuntimeError('episode training exceeded')
        self.commands[i]=action;self.ranges[i]=ranges;self.outcomes[i]=outcome
        self.n+=1

class OnlineRLS:
    """Regularized recursive least squares. No hidden-state or cause labels.

    Target is observed CHANGE in range and (if available) measured inertial
    displacement; outcomes only arrive after predictions have been logged.
    """
    def __init__(self, kind:str, reference:bool=True, forgetting:float=.995):
        self.kind=kind;self.reference=reference
        d=len(features(kind,np.ones(4)*7.,ACTIONS[0]))
        self.w=np.zeros((d,6));self.p=np.eye(d)*4.
        self.forgetting=forgetting;self.seen=0
        self.alarms=0
    def predict(self,ranges,action):
        f=features(self.kind,ranges,action)
        return f@self.w
    def update(self,ranges,action,outcome):
        if self.kind=='zero':return
        f=features(self.kind,ranges,action)
        prediction=f@self.w
        # Adaptive forgetting selected in developmental design; it may cause
        # many false alarms, so measure separately and don't equate with agency.
        lam=self.forgetting
        if self.kind=='adaptive_nonlinear' and self.seen>=15:
            err=outcome[:4]-prediction[:4]
            if np.mean(err*err)>.1:
                lam=.87
                self.alarms+=1
        q=self.p@f
        denom=lam+f@q
        if denom<=0:raise ArithmeticError('invalid covariance')
        k=q/denom
        residual=outcome-prediction
        if not self.reference:residual[4:]=0
        self.w+=np.outer(k,residual)
        self.p=(self.p-np.outer(k,q))/lam
        self.p=(self.p+self.p.T)/2
        self.seen+=1


def run_world(seed:int,cause:str,policy:str='random',noise:float=.025,reference=True):
    w=NonlinearWorld(seed,cause,noise,reference)
    models={name:(KNNPredictor(name,reference) if name.startswith('knn_') else OnlineRLS(name,reference)) for name in MODELS}
    rng=np.random.default_rng(seed+3_889_991)
    y=w.begin();rows=[]
    for t in range(TOTAL):
        if policy=='random':a=int(rng.integers(5))
        elif policy=='cycle':a=[1,3,2,4,0][t%5]
        elif policy=='repeat':a=1
        else:raise ValueError(policy)
        u=ACTIONS[a]
        pre={name:model.predict(y,u) for name,model in models.items()}
        # Evaluator-only counterfactual at a later state. It copies the physical
        # world BEFORE action selection takes effect; no model sees alternate
        # observations and its weights are unchanged by the hypothetical probes.
        if t==120:
            for hypothetical in ACTIONS:
                hypothesis_i=int(np.where(np.all(ACTIONS==hypothetical,axis=1))[0][0])
                alternate=copy.deepcopy(w)
                counter_y,_=alternate.step(hypothesis_i)
                for name,model in models.items():
                    guess=model.predict(y,hypothetical)
                    rows.append({'seed':seed,'cause':cause,'policy':policy,'reference':int(reference),
                                 'noise':noise,'phase':'counterfactual','model':name,
                                 'range_sqerr':float(np.mean((guess[:4]-(counter_y-y))**2)),
                                 'inertial_sqerr':None})
        yn,z=w.step(a)
        target=np.r_[yn-y, z if reference else np.zeros(2)]
        phase=('pre' if t>=30 and t<65 else 'early' if 80<=t<99 else 'late' if 115<=t<150 else 'other')
        for name,model in models.items():
            p=pre[name]
            if phase!='other':
                rows.append({'seed':seed,'cause':cause,'policy':policy,'reference':int(reference),
                             'noise':noise,'phase':phase,'model':name,
                             'range_sqerr':float(np.mean((p[:4]-target[:4])**2)),
                             'inertial_sqerr':float(np.mean((p[4:]-target[4:])**2)) if reference else None})
            model.update(y,u,target.copy())
        y=yn
    return rows,{m:int(q.alarms) for m,q in models.items()}


def grouped_stats(rows):
    sums={};count={}
    for r in rows:
        k=(r['cause'],r['phase'],r['model'])
        sums[k]=sums.get(k,0.)+r['range_sqerr']
        count[k]=count.get(k,0)+1
    return {c:{p:{m:sums[(c,p,m)]/count[(c,p,m)] for m in MODELS}
                for p in ('pre','early','late','counterfactual')}
            for c in CAUSES}

def bootstrap_paired(rows,model='nonlinear',base='linear',phase='late',causes=('motor','external','sensor','motor_external','unknown_nonlinear'),seed=1608):
    """Paired bootstrap clusters on simulated world seed; all cause trials nested."""
    data={}
    for r in rows:
        if r['phase']==phase and r['cause'] in causes and r['model'] in (model,base):
            k=(r['seed'],r['cause'],r['model'])
            data.setdefault(k,[]).append(r['range_sqerr'])
    seeds=sorted({r['seed'] for r in rows})
    delta=[]
    for s in seeds:
        differences=[]
        for c in causes:
            a=data[(s,c,model)];b=data[(s,c,base)]
            differences.append(np.mean(a)-np.mean(b))
        delta.append(float(np.mean(differences)))
    delta=np.array(delta)
    rand=np.random.default_rng(seed)
    bs=np.mean(rand.choice(delta,size=(4000,len(seeds)),replace=True),axis=1)
    return {'contrast':f'{model}_minus_{base}', 'phase':phase, 'n_seed_clusters':len(seeds),
            'mean':float(delta.mean()),'ci95_seed_bootstrap':[float(x) for x in np.quantile(bs,[.025,.975])],
            'model_wins':int(np.sum(delta<0)),'model_losses':int(np.sum(delta>0))}


def run(seeds=48,noise=.025,reference=True,policy='random'):
    rows=[];alarms=[]
    for i in range(seeds):
        seed=9_100_001+i*101
        for cause in CAUSES:
            r,a=run_world(seed,cause,policy,noise,reference)
            rows.extend(r)
            alarms.append({'seed':seed,'cause':cause,'adaptive_alarm_steps':a['adaptive_nonlinear']})
    summary={'status':'EXPLORATORY development ONLY; no preregistration, peer review, or consciousness measure',
             'seed_clusters':seeds,'cause_types':list(CAUSES),'noise':noise,'reference':reference,'policy':policy,
             'model_range_mse':grouped_stats(rows),
             'paired_nonlinear_minus_linear':bootstrap_paired(rows),
             'paired_adaptive_minus_fixed':bootstrap_paired(rows,model='adaptive_nonlinear',base='nonlinear'),
             'paired_nonlinear_minus_action_blind':bootstrap_paired(rows,model='nonlinear',base='action_blind'),
             'paired_nonlinear_minus_knn':bootstrap_paired(rows,model='nonlinear',base='knn_recent'),
             'paired_knn_minus_linear':bootstrap_paired(rows,model='knn_recent',base='linear'),
             'counterfactual_nonlinear_minus_knn':bootstrap_paired(rows,model='nonlinear',base='knn_recent',phase='counterfactual'),
             'alarm_steps_mean_by_cause':{c:float(np.mean([a['adaptive_alarm_steps'] for a in alarms if a['cause']==c])) for c in CAUSES}}
    return rows,alarms,summary


def save(out,rows,alarms,summary):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    for name,data in [('per_prediction.csv',rows),('alarms.csv',alarms)]:
        with (out/name).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    (out/'summary.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n')


def main():
    p=argparse.ArgumentParser();p.add_argument('--seeds',type=int,default=48)
    p.add_argument('--noise',type=float,default=.025);p.add_argument('--no-reference',action='store_true')
    p.add_argument('--policy',choices=['random','cycle','repeat'],default='random')
    p.add_argument('--out',default='development')
    args=p.parse_args()
    rows,alarms,summary=run(args.seeds,args.noise,not args.no_reference,args.policy)
    save(args.out,rows,alarms,summary)
    print(json.dumps({'seeds':args.seeds,'summary':summary['paired_nonlinear_minus_linear'],
                      'adaptive':summary['paired_adaptive_minus_fixed']},indent=2))
if __name__=='__main__':main()
