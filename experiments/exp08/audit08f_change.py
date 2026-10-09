"""Exp 08F DEVELOPMENT: action-conditioned error monitoring and adaptive forgetting.

All learning is online from visible relative bearings and previous commands; no
hidden actuator state or reversal time is shown to the learners. Designs and
hyperparameters are investigator-chosen. This is not a consciousness measure.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import numpy as np
from world2d import World, WorldConfig
from controllers import BayesianController, ComparatorController, GreedyController

# Distinct from 08E, but these are STILL exploratory/development seeds.
DEV_SEED_BASES = (31_000_000, 32_000_000, 33_000_000, 34_000_000, 35_000_000, 36_000_000)
MODES = ('slow', 'fast', 'adaptive_gain', 'surprise_reset', 'memoryless')
ALL_NAV = MODES + ('bayesian','comparator','greedy')

class ActionPredictor:
    """Learn a two-vector action-outcome model for each of four commands.

    Surprise thresholds are determined by current action prediction error only.
    Neither motor polarity nor actual motor displacement nor goal location is read.
    """
    def __init__(self, mode='slow'):
        if mode not in MODES:raise ValueError(mode)
        self.mode=mode
        self.vectors=np.zeros((4,2),dtype=float)
        self.counts=np.zeros(4,dtype=int)
        self.errors=[]
        self.n_updates=0
        self.alarms=0
        self.consecutive_surprises=0
        self.alarm_steps=[]

    def predict(self, action:int):
        if not 0 <= action < 4:raise ValueError('action out of range')
        return self.vectors[action].copy() if self.mode!='memoryless' else np.zeros(2)

    def observe_effect(self, action:int, actual, t:int):
        """Updates the model AFTER scored prequential prediction. Returns alarm flag."""
        actual=np.asarray(actual,dtype=float)
        if actual.shape!=(2,):raise ValueError('sensor displacement must be 2-vector')
        if self.mode=='memoryless':return False
        residual=actual-self.vectors[action]
        sq=float(residual@residual)
        self.n_updates+=1
        self.errors.append(sq)
        alarm=False
        if self.mode=='surprise_reset':
            # Ignore early calibration as a source of reset signals.
            trained=bool(self.counts.sum()>=8 and self.counts[action]>=1)
            surprising=trained and sq>2.25
            self.consecutive_surprises = self.consecutive_surprises+1 if surprising else 0
            if self.consecutive_surprises>=2:
                self.vectors[:]=0
                self.counts[:]=0
                self.consecutive_surprises=0
                self.alarms+=1
                self.alarm_steps.append(t)
                alarm=True
        if self.mode=='slow':alpha=.25
        elif self.mode=='fast':alpha=.75
        elif self.mode=='adaptive_gain':alpha=.85 if sq>2.25 and self.counts[action]>=2 else .25
        else:alpha=.25
        self.vectors[action] += alpha*(actual-self.vectors[action])
        self.counts[action]+=1
        return alarm


def valid_displacement(prev,obs):
    """Only if same visible target, and no known food respawn/collision."""
    return bool(prev[-1]>.5 and obs[-1]>.5 and obs[-3]<.5 and obs[-2]<.5)


def phase(t:int):
    if t<=24:return 'before_change'
    if t<=32:return 'after_change_early'
    return 'after_change_late'


def probe(seed, mode, shifted=True, dropout=.12, steps=48):
    """Matched open-loop action sequence, with prequential forecast scoring.

    Same physical world/random commands for all modes. This prevents controller
    differences from changing food placement or future movement histories.
    """
    w=World(seed,WorldConfig(steps=steps,reversal=shifted,dropout_probability=dropout,
                             energy_start=200.))
    actor=np.random.default_rng(seed+62_000)
    p=ActionPredictor(mode)
    previous=None; action_before=None; forecast_before=None
    rows=[]
    while not w.done:
        obs=w.observe()
        if previous is not None and valid_displacement(previous,obs):
            outcome=(previous[:2]-obs[:2])*6.
            sq=float(np.sum((outcome-forecast_before)**2))
            event={'seed':seed,'mode':mode,'shifted':int(shifted),'t':w.t,
                   'phase':phase(w.t),'squared_error':sq,'alarm':0}
            alarm=p.observe_effect(action_before,outcome,w.t)
            event['alarm']=int(alarm)
            rows.append(event)
        command=int(actor.integers(4))
        prediction=p.predict(command)
        previous=obs.copy();action_before=command;forecast_before=prediction
        w.step(command)
    return rows,{'seed':seed,'mode':mode,'shifted':int(shifted),'n_predictions':len(rows),
                 'n_alarms':p.alarms,'alarm_steps':p.alarm_steps}


class NavigatingLearner:
    def __init__(self, mode):
        self.model=ActionPredictor(mode)
        self.prev=None;self.prev_action=None;self.last_pred=None;self.t=0
    def act(self,obs,rng):
        if self.prev is not None and valid_displacement(self.prev,obs):
            displacement=(self.prev[:2]-obs[:2])*6.
            self.model.observe_effect(self.prev_action,displacement,self.t)
        self.prev=np.asarray(obs,dtype=float).copy()
        direction=obs[:2]
        if obs[-1]>.5 and np.linalg.norm(direction)>.04:
            # Uniform exploration and identical goal-directed policy for all arms.
            if self.model.counts.min()<2:
                least=np.flatnonzero(self.model.counts==self.model.counts.min())
                action=int(rng.choice(least))
            elif rng.random()<.12:
                action=int(rng.integers(4))
            else:
                action=int(np.argmax(self.model.vectors@direction))
        else:
            action=int(rng.integers(4))
        self.last_pred=self.model.predict(action)
        self.prev_action=action
        self.t+=1
        return action


def navigate(seed,mode,shifted=True,dropout=.12):
    cfg=WorldConfig(steps=48,reversal=shifted,dropout_probability=dropout)
    w=World(seed,cfg)
    rng=np.random.default_rng(seed+99991)
    if mode in MODES:agent=NavigatingLearner(mode)
    elif mode=='bayesian':agent=BayesianController()
    elif mode=='comparator':agent=ComparatorController()
    elif mode=='greedy':agent=GreedyController()
    else:raise ValueError(mode)
    while not w.done:
        a=agent.act(w.observe(),rng)
        w.step(a)
    result={'seed':seed,'mode':mode,'shifted':int(shifted),'food':int(w.food),
            'fraction_alive':float(w.alive_steps/cfg.steps)}
    if mode in MODES:result['alarms']=agent.model.alarms
    return result


def paired_bootstrap(diffs, rng_seed=81080):
    d=np.asarray(diffs,dtype=float)
    rng=np.random.default_rng(rng_seed)
    estimates=rng.choice(d,size=(10000,len(d)),replace=True).mean(axis=1)
    return {'mean':float(d.mean()),'ci95':[float(x) for x in np.quantile(estimates,[.025,.975])],
            'positive':int(np.sum(d>0)),'negative':int(np.sum(d<0)),'ties':int(np.sum(d==0))}


def run(per_group=24, include_navigation=True):
    if per_group<1:raise ValueError('per_group must be >0')
    seeds=[base+i*479 for base in DEV_SEED_BASES for i in range(per_group)]
    events=[]; alarms=[]; navigation=[]
    for seed in seeds:
        for changed in (False,True):
            for mode in MODES:
                steps, stats=probe(seed,mode,changed)
                events.extend(steps);alarms.append(stats)
                if include_navigation:
                    navigation.append(navigate(seed+10_000_003,mode,changed))
            if include_navigation:
                for mode in ALL_NAV[len(MODES):]:
                    navigation.append(navigate(seed+10_000_003,mode,changed))
    means={}; seed_level={}
    for changed in (False,True):
        for mode in MODES:
            for ph in ('before_change','after_change_early','after_change_late'):
                sel=[e for e in events if e['shifted']==int(changed) and e['mode']==mode and e['phase']==ph]
                # Primary descriptive aggregation: world average, not step-pooled.
                worlds={s:np.mean([r['squared_error'] for r in sel if r['seed']==s])
                        for s in seeds if any(r['seed']==s for r in sel)}
                means[f'{mode}_{int(changed)}_{ph}']={'mean_of_world_mse':float(np.mean(list(worlds.values()))) if worlds else None,
                          'n_worlds':len(worlds),'n_steps':len(sel)}
                seed_level[(changed,mode,ph)]=worlds
    summary={'status':'EXP08F EXPLORATORY DEVELOPMENT ONLY; NOT PREREGISTERED; NO CONSCIOUSNESS CLAIM',
             'n_independent_seed_worlds':len(seeds),'total_open_loop_valid_events':len(events),
             'world_level_mse':means,'alarms':{},'comparisons':{},'navigation':{}}
    for mode in MODES:
        for changed in (False,True):
            data=[a for a in alarms if a['mode']==mode and a['shifted']==int(changed)]
            summary['alarms'][f'{mode}_{int(changed)}']={
                'n_worlds_with_alarm':sum(a['n_alarms']>0 for a in data),
                'n_total_alarms':sum(a['n_alarms'] for a in data),
                'n_worlds':len(data)}
    for ph in ('before_change','after_change_early','after_change_late'):
        for ctrl in ('slow','fast','memoryless'):
            a=seed_level[(True,'surprise_reset',ph)];b=seed_level[(True,ctrl,ph)]
            common=sorted(a.keys()&b.keys())
            if common:
                summary['comparisons'][f'reset_minus_{ctrl}_{ph}']=paired_bootstrap([a[s]-b[s] for s in common])
    if include_navigation:
        for changed in (False,True):
            for mode in ALL_NAV:
                rows=[a for a in navigation if a['shifted']==int(changed) and a['mode']==mode]
                summary['navigation'][f'{mode}_{int(changed)}']={'n_worlds':len(rows),'mean_food':float(np.mean([a['food'] for a in rows])),'mean_survival':float(np.mean([a['fraction_alive'] for a in rows]))}
    return events,alarms,navigation,summary


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--per-group',type=int,default=24)
    ap.add_argument('--out',default='development_change08f')
    ap.add_argument('--no-navigation',action='store_true')
    args=ap.parse_args()
    events,alarms,navigation,summary=run(args.per_group,not args.no_navigation)
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    for name,rows in [('prediction_events.csv',events),('alarm_per_world.csv',alarms),('navigation_per_world.csv',navigation)]:
        if not rows:continue
        with (out/name).open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=sorted(set().union(*(r.keys() for r in rows))))
            writer.writeheader()
            for r in rows:
                row=r.copy()
                if 'alarm_steps' in row:row['alarm_steps']='|'.join(map(str,row['alarm_steps']))
                writer.writerow(row)
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({'n_worlds':summary['n_independent_seed_worlds'],'total_steps':len(events),
                      'alarms':summary['alarms'],'navigation':summary['navigation']},indent=2))

if __name__=='__main__':main()
