"""08E exploratory pilot: label-free, online action/sensation prediction.

This is a hand-written learning rule, not an evolved architecture or consciousness
measurement.  All tuning and experiments are DEVELOPMENT ONLY.  No true hidden
actuator rotation, map coordinates or oracle feedback is read by the policy.
"""
from __future__ import annotations
import argparse
import csv
import json
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from world2d import World, WorldConfig, ACT
from controllers import ComparatorController, BayesianController, GreedyController

# NEW development namespace; not confirmatory; changing these seeds requires recording a new pilot.
DEV_BASE = (23_000_000, 24_000_000, 25_000_000, 26_000_000, 27_000_000, 28_000_000)
T = 48

@dataclass
class StepRecord:
    # This is a test-side instrumentation record, NOT a privileged observation to the agent.
    seed: int
    kind: str
    env: str
    t: int
    valid: bool
    squared_error: float|None
    food: int
    alive: bool


class OnlineSensorimotor:
    """Four action-specific 2D outcome vectors learned *from sensory prediction errors*.

    Each action's effect starts unknown (0). The agent knows only that it has
    four available commands, a vector bearing observation, and previous actions.
    It does not assume rotation symmetry or have access to hidden motor labels.

    Variants are controlled information ablations, NOT distinct evolved lineages.
    """
    def __init__(self, kind='action_model', learning_rate=.60, epsilon=.12, seed=0):
        if kind not in ('action_model','shuffled_action','action_blind','reset_memory'):
            raise ValueError(kind)
        self.kind=kind; self.rate=learning_rate;self.epsilon=epsilon
        self.vectors=np.zeros((4,2),dtype=float)
        self.counts=np.zeros(4,dtype=int)
        self.global_mean=np.zeros(2,dtype=float)
        self.n_global=0
        self.prev=None;self.last_action=None;self.last_pred=None
        self.rng=np.random.default_rng(seed+53_811)
        self.n_valid=0;self.squared_errors=[]
        self.history=[]

    def act(self,obs,rng):
        obs=np.asarray(obs,dtype=float)
        if self.kind=='reset_memory':
            self.vectors[:]=0;self.counts[:]=0;self.global_mean[:]=0;self.n_global=0
        if self.prev is not None and self.last_action is not None:
            valid=(self.prev[-1]>.5 and obs[-1]>.5 and obs[-3]<.5 and obs[-2]<.5)
            # both observations are relative to the *same target* after excluding respawns
            if valid:
                observed=(self.prev[:2]-obs[:2])*6.
                if self.last_pred is not None:
                    self.squared_errors.append(float(np.sum((observed-self.last_pred)**2)))
                self.n_valid+=1
                if self.kind=='action_blind':
                    self.n_global+=1
                    self.global_mean+=self.rate*(observed-self.global_mean)
                    self.vectors[:]=self.global_mean
                else:
                    idx=self.last_action
                    if self.kind=='shuffled_action':
                        # Wrong action key, sampled independently of the original command.
                        idx=int(self.rng.integers(4))
                    self.vectors[idx]+=self.rate*(observed-self.vectors[idx])
                    self.counts[idx]+=1
        self.prev=obs.copy()
        direction=obs[:2]
        if obs[-1]>.5 and np.linalg.norm(direction)>.04:
            utilities=self.vectors@direction
            if self.kind=='action_blind' or (self.counts.sum()==0):
                action=int(rng.integers(4))
            elif self.kind=='reset_memory':
                action=int(rng.integers(4))
            elif self.counts.min()<2:
                # Exposure to all actions, with no oracle about their outcomes.
                least=np.flatnonzero(self.counts==self.counts.min())
                action=int(rng.choice(least))
            elif rng.random()<self.epsilon:
                action=int(rng.integers(4))
            else:
                action=int(np.argmax(utilities))
        else:
            action=int(rng.integers(4))
        self.last_action=action
        self.last_pred=self.vectors[action].copy()
        self.history.append((action,self.vectors.copy()))
        return action


def run_episode(seed,kind,env='shift+dropout',config=None):
    cfg=config or WorldConfig(steps=T,reversal=(env=='shift+dropout'),dropout_probability=.12 if env=='shift+dropout' else 0.)
    w=World(seed,cfg)
    rng=np.random.default_rng(seed+99991)
    if kind=='comparator':controller=ComparatorController()
    elif kind=='bayesian':controller=BayesianController()
    elif kind=='greedy':controller=GreedyController()
    else:controller=OnlineSensorimotor(kind,seed=seed)
    while not w.done:
        obs=w.observe()
        cmd=controller.act(obs,rng)
        w.step(cmd)
    result={'seed':seed,'controller':kind,'environment':env,'food':int(w.food),
            'survival_fraction':round(w.alive_steps/cfg.steps,8)}
    if isinstance(controller,OnlineSensorimotor):
        errors=controller.squared_errors
        result['valid_prediction_events']=len(errors)
        result['prequential_mse']=float(np.mean(errors)) if errors else None
        result['learned_action_vectors']=controller.vectors.tolist()
    return result


def open_loop_probe(seed,kind='action_model',env='shift+dropout',noise=.025,dropout=.12):
    """Causal *prequential* prediction on shared random command/episode trajectories.

    The learner produces a predicted outcome BEFORE the action is applied;
    its estimate can only update when the next observation arrives.
    Every arm sees identical world seed + actions; different arms have separate RNG.
    Scoring excludes respawned target, observed collision, and invisible bearing.
    """
    if kind not in ('action_model','shuffled_action','action_blind','reset_memory'):
        raise ValueError(kind)
    cfg=WorldConfig(reversal=env=='shift+dropout',dropout_probability=dropout,
                    observation_noise=noise,energy_start=200.)
    world=World(seed,cfg)
    action_rng=np.random.default_rng(seed+62_000)
    policy_rng=np.random.default_rng(seed+99991)
    agent=OnlineSensorimotor(kind,seed=seed)
    events=[]
    for t in range(cfg.steps):
        obs=world.observe()
        # Important: agent.act observes and learns from past ONLY. Command generated
        # by independent fixed random stream: same physical trajectory in each arm.
        agent.act(obs,policy_rng)
        cmd=int(action_rng.integers(4))
        agent.last_action=cmd
        agent.last_pred=agent.vectors[cmd].copy()
        world.step(cmd)
        if len(agent.squared_errors)>len(events):
            # not used: events aren't all steps; compute predictive loss separately below
            pass
        events.append({'t':t,'obs':obs.copy(),'command':cmd,'pred':agent.last_pred.copy()})
        if world.done:break
    errors=[]
    # Predictions issued at t, validated at t+1; zero look-ahead, no hidden labels.
    for i in range(len(events)-1):
        pre=events[i]; post=events[i+1]
        a,b=pre['obs'],post['obs']
        if a[-1]>.5 and b[-1]>.5 and b[-3]<.5 and b[-2]<.5:
            observed=(a[:2]-b[:2])*6.
            # prediction computed at timestep i, prior to observing event i+1
            errors.append({'t':i+1,'squared_error':float(np.sum((observed-pre['pred'])**2)),
                           'phase':'pre' if i+1<=24 else 'post'})
    return {'seed':seed,'kind':kind,'env':env,'events':errors,
            'pre_mse':float(np.mean([x['squared_error'] for x in errors if x['phase']=='pre'])) if any(x['phase']=='pre' for x in errors) else None,
            'post_mse':float(np.mean([x['squared_error'] for x in errors if x['phase']=='post'])) if any(x['phase']=='post' for x in errors) else None,
            'n_valid':len(errors)}


def study(seeds_per_group=24,nav_per_group=24):
    names=('action_model','shuffled_action','action_blind','reset_memory')
    probe_rows=[]
    for group,base in enumerate(DEV_BASE):
        for i in range(seeds_per_group):
            seed=base+i*7919
            for kind in names:
                row=open_loop_probe(seed,kind=kind)
                probe_rows.append({k:v for k,v in row.items() if k!='events'})
    navigation=[]
    for group,base in enumerate(DEV_BASE):
        for i in range(nav_per_group):
            seed=base+1_000_003+i*107
            for env in ('stable','shift+dropout'):
                for kind in (*names,'greedy','comparator','bayesian'):
                    result=run_episode(seed,kind,env=env)
                    navigation.append({k:v for k,v in result.items() if k!='learned_action_vectors'})
    by={}
    for r in probe_rows:
        by.setdefault(r['kind'],{'pre':[],'post':[]})
        for phase in ('pre','post'):
            x=r[f'{phase}_mse']
            if x is not None:by[r['kind']][phase].append(x)
    summary={'status':'EXP08E EXPLORATORY DEVELOPMENT, not pre-registered, no consciousness outcome',
             'nature':'hand-designed label-free online action-specific forward model',
             'seeds_per_group':seeds_per_group,'nav_per_group':nav_per_group,
             'n_seed_groups':len(DEV_BASE),
             'probe':{k:{p:{'n_worlds':len(d),'mean_mse':float(np.mean(d))} for p,d in v.items()} for k,v in by.items()},
             'navigation':{}}
    for kind in (*names,'greedy','comparator','bayesian'):
        summary['navigation'][kind]={}
        for env in ('stable','shift+dropout'):
            data=[r['food'] for r in navigation if r['controller']==kind and r['environment']==env]
            summary['navigation'][kind][env]={'n_episodes':len(data),'mean_food':float(np.mean(data)),
                                             'fraction_no_food':float(np.mean(np.asarray(data)==0))}
    return probe_rows,navigation,summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',default='development_selfsupervised08e')
    p.add_argument('--probes',type=int,default=24)
    p.add_argument('--navigation',type=int,default=24)
    args=p.parse_args()
    dest=Path(args.out); dest.mkdir(parents=True,exist_ok=True)
    probes,nav,summary=study(args.probes,args.navigation)
    for filename,data in [('probe_per_seed.csv',probes),('navigation_per_seed.csv',nav)]:
        with (dest/filename).open('w',newline='') as f:
            columns=sorted(set().union(*(r.keys() for r in data)))
            writer=csv.DictWriter(f,fieldnames=columns);writer.writeheader();writer.writerows(data)
    (dest/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
