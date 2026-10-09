"""Experiment 06: evolutionary emergence of an action-outcome comparator.

Self-caused motor consequences and external events produce individually
indistinguishable momentary sensory signals. Only a retained efference copy
can make those signals useful for survival.

This is a MODEL OF SENSORIMOTOR COMPUTATION. Not a consciousness assay.
Dependencies: numpy; analysis additionally requires scipy/matplotlib.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import numpy as np

H = 4
# For genome: 4 cue-input, 4 event-input, 4 biases, 4 outputs, 1 output bias,
# plus 16 independently mutable recurrent connections, initially absent.
D = H * 4 + 1

@dataclass(frozen=True)
class Settings:
    population: int = 192
    generations: int = 400
    elite_count: int = 24
    parent_pool: int = 64
    q: float = .92
    mutation_sd: float = .32
    mutation_prob: float = .23
    new_recurrent_prob: float = .045
    recurrent_cut_prob: float = .008
    recurrent_cost: float = .0008
    initial_sd: float = .8


def initialize(rng: np.random.Generator, config: Settings):
    plain = rng.normal(0, config.initial_sd, size=(config.population, D))
    recurrence = np.zeros((config.population,H,H))
    mask = np.zeros((config.population,H,H),dtype=bool)
    return plain, recurrence, mask


def sensor_output(plain,rec, mask, cue, signal, retained=True):
    """Two phase RNN, same generic hidden state, no self/other label as input.
    cue,signal scalar or vector; return predicted probability of entering.
    """
    cue=np.asarray(cue, dtype=float)
    signal=np.asarray(signal,dtype=float)
    Wc=plain[:,0:H]; Ws=plain[:,H:2*H]
    bias=plain[:,2*H:3*H]; out=plain[:,3*H:4*H]; outbias=plain[:,-1]
    if cue.ndim==0: cue=np.full((1,), cue)
    if signal.ndim==0: signal=np.full((1,), signal)
    memory=np.tanh(cue[None,:,None]*Wc[:,None,:]+bias[:,None,:])
    if retained:
        feed=np.einsum('pkh,phj->pkj',memory,rec*mask,optimize=True)
    else:
        feed=np.zeros_like(memory)
    z=np.tanh(signal[None,:,None]*Ws[:,None,:]+feed+bias[:,None,:])
    logits=np.einsum('pkh,ph->pk',z,out,optimize=True)+outbias[:,None]
    return 1/(1+np.exp(-np.clip(logits,-45,45))),z


def expected_payoff(plain,rec,mask,q=.92, retained=True,recurrent_cost=0.0):
    # Four sensory configurations; this is exact expected payoff, not Monte Carlo.
    cues=np.array([-1,-1,1,1]); signals=np.array([-1,1,-1,1])
    p,_=sensor_output(plain,rec,mask,cues,signals,retained=retained)
    matching=(cues==signals)
    # For each cue, P(self,signal) = .25*(q if matching else 1-q)
    # and P(external,signal) = .125, with P(cue)=P(source)=.5.
    percase=.25*np.where(matching,q,1-q)-.125
    gains=(p*percase[None,:]).sum(axis=1)
    costs=recurrent_cost*mask.sum(axis=(1,2)) if retained else 0.0
    return gains-costs


def evolve(seed: int, config: Settings=Settings(), control: str='evolve'):
    assert control in ('evolve','no_recurrence','random_fitness','no_inheritance')
    rng=np.random.default_rng(seed)
    plain,rec,mask=initialize(rng,config)
    trace=[]
    for generation in range(config.generations):
        scores=expected_payoff(plain,rec,mask,q=config.q,recurrent_cost=config.recurrent_cost)
        effective=np.copy(scores)
        if control=='random_fitness': effective=rng.random(config.population)
        idx=np.argsort(effective)[::-1]
        # Save top performers. This is truncation selection, not gradient descent.
        parent_idx=idx[:config.parent_pool]
        new_plain=np.empty_like(plain);new_rec=np.empty_like(rec);new_mask=np.empty_like(mask)
        e=config.elite_count if control!='no_inheritance' else 0
        if e:
            new_plain[:e]=plain[idx[:e]];new_rec[:e]=rec[idx[:e]];new_mask[:e]=mask[idx[:e]]
        for j in range(e,config.population):
            if control=='no_inheritance':
                new_plain[j]=rng.normal(0,config.initial_sd,size=D)
                new_rec[j]=0;new_mask[j]=False
                continue
            parent=int(rng.choice(parent_idx))
            new_plain[j]=plain[parent]
            mutations=rng.random(D)<config.mutation_prob
            new_plain[j,mutations]+=rng.normal(0,config.mutation_sd,size=np.sum(mutations))
            new_plain[j]=np.clip(new_plain[j],-8,8)
            new_mask[j]=mask[parent]
            new_rec[j]=rec[parent]
            if control=='no_recurrence':
                new_mask[j]=False;new_rec[j]=0
            else:
                # Mutation may construct previously absent recurrence (no pre-installed comparator).
                births=(~new_mask[j])&(rng.random((H,H))<config.new_recurrent_prob)
                deaths=new_mask[j]&(rng.random((H,H))<config.recurrent_cut_prob)
                new_mask[j][births]=True;new_rec[j][births]=rng.normal(0,.7,size=births.sum())
                new_mask[j][deaths]=False;new_rec[j][deaths]=0
                modifications=new_mask[j]&(rng.random((H,H))<config.mutation_prob)
                new_rec[j][modifications]+=rng.normal(0,config.mutation_sd,size=modifications.sum())
                new_rec[j]=np.clip(new_rec[j],-8,8)
        plain,rec,mask=new_plain,new_rec,new_mask
        if generation%10==0 or generation==config.generations-1:
            p=expected_payoff(plain,rec,mask,q=config.q,recurrent_cost=0)
            trace.append((generation+1,float(np.max(p)),float(np.mean(p)),float(np.mean(mask.sum(axis=(1,2))))))
    scores=expected_payoff(plain,rec,mask,q=config.q,recurrent_cost=config.recurrent_cost)
    best=int(np.argmax(scores))
    return {'seed':seed,'control':control,'plain':plain[best].copy(),'rec':rec[best].copy(),
            'mask':mask[best].copy(),'selection_score':float(scores[best]),
            'active_links':int(mask[best].sum()), 'trace':trace,
            'settings':asdict(config)}


def analytic_bound(q=.92):
    # max conditional-survival reward on four cue / event combinations.
    match= .25*q-.125; opposite=.25*(1-q)-.125
    return 2*max(0,match)+2*max(0,opposite)


def test_agent(agent, q, seed, N=40000, control='normal'):
    """Out-of-sample simulated episodes, generator independent of evolution.
    Returns actual realized net payoff and action-outcome classification AUC ingredients.
    """
    rng=np.random.default_rng(seed)
    cue=rng.choice([-1,1],size=N)
    source=rng.integers(0,2,size=N) # 1 self-caused, 0 external
    effective=rng.random(N)<q
    ext=rng.choice([-1,1],size=N)
    sensory=np.where(source==1,np.where(effective,cue,-cue),ext)
    retained=control!='no_memory'
    if control=='scramble_memory':
        memory_cue=rng.permutation(cue)
    else: memory_cue=cue
    p,hidden=sensor_output(agent['plain'][None,:],agent['rec'][None,:,:], agent['mask'][None,:,:],memory_cue,sensory,retained=retained)
    p=p[0];hidden=hidden[0]
    # Averaging expected action payoff suppresses decision-sampling noise.
    payoff=np.mean(p*np.where(source==1,1,-1))
    # Exact 4-combination payoff is reported separately from sampled payoff.
    return dict(payoff=float(payoff), cue=cue, event=sensory, source=source, prediction=p, hidden=hidden)

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--seed',type=int,default=14);parser.add_argument('--gens',type=int,default=400); args=parser.parse_args()
    cfg=Settings(generations=args.gens)
    for control in ('evolve','no_recurrence','random_fitness'):
        a=evolve(args.seed,cfg,control)
        print(control,a['selection_score'],a['active_links'],a['trace'][-1])
