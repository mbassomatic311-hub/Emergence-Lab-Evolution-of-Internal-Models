"""Experiment 08 development-only world audit and privileged performance reference.

This oracle is intentionally forbidden to ordinary controllers: it sees the
hidden rotation, complete obstacle map, exact positions, and current target.
It is an engineering reference, never a fair baseline or theoretical maximum.
"""
from __future__ import annotations
from collections import deque
import argparse, csv, json
from pathlib import Path
import numpy as np
from world2d import World, WorldConfig, ACT, N
from engine import simulate, DEV_SEEDS
from controllers import GreedyController, ComparatorController, BayesianController


def oracle_action(world):
    """Choose a feasible shortest-path physical move, invert hidden motor mapping."""
    start=tuple(int(v) for v in world.pos)
    goal=tuple(int(v) for v in world.target)
    queue=deque([start]); parents={start:None}; first_action={}
    while queue:
        cur=queue.popleft()
        if cur==goal:break
        for k,v in enumerate(ACT):
            candidate=(cur[0]+int(v[0]),cur[1]+int(v[1]))
            if not world._blocked(candidate) and candidate not in parents:
                parents[candidate]=cur
                first_action[candidate]=k if cur==start else first_action[cur]
                queue.append(candidate)
    if goal in first_action:
        physical=first_action[goal]
    else:
        # Disconnected board: choose the unblocked neighboring cell nearest to target.
        choices=[(abs((start[0]+int(v[0]))-goal[0])+abs((start[1]+int(v[1]))-goal[1]),k)
                 for k,v in enumerate(ACT) if not world._blocked(np.array(start)+v)]
        physical=min(choices)[1] if choices else 0
    rotation=int(world.rotation)
    if world.cfg.reversal and world.t==world.cfg.steps//2:
        rotation=(rotation+2)%4   # unannounced intervention, known only to oracle
    return (physical-rotation)%4


def oracle_rollout(seed,env):
    world=World(seed, WorldConfig(reversal=env!='stable',dropout_probability=.12 if env=='shift+dropout' else 0.))
    while not world.done:
        world.step(oracle_action(world))
    return {'food':float(world.food),'survival':float(world.alive_steps/world.cfg.steps)}


def run(seeds=DEV_SEEDS[:3],eval_n=12):
    rows=[]
    for seed in seeds:
        for env in ('stable','shift+dropout'):
            for i in range(eval_n):
                world_seed=seed+1200000+i*733
                for name,con in [('greedy',GreedyController),('comparator',ComparatorController),('bayesian',BayesianController)]:
                    food,survival=simulate(con(),world_seed,env=env)
                    rows.append({'population_seed':seed,'world_seed':world_seed,'environment':env,
                                 'controller':name,'food':food,'survival':survival})
                out=oracle_rollout(world_seed,env)
                rows.append({'population_seed':seed,'world_seed':world_seed,'environment':env,
                             'controller':'privileged_pathfinding_reference','food':out['food'], 'survival':out['survival']})
    summary={'status':'DEVELOPMENT ONLY; privileged ceiling is not a fair information-matched baseline',
       'n_population_seeds':len(seeds),'episodes_per_population':eval_n,
       'mean_food':{c:{e:float(np.mean([r['food'] for r in rows if r['controller']==c and r['environment']==e]))
                        for e in ('stable','shift+dropout')}
            for c in ('greedy','comparator','bayesian','privileged_pathfinding_reference')}}
    return rows,summary


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',default='development_world_audit')
    p.add_argument('--eval-n',type=int,default=12)
    args=p.parse_args();out=Path(args.out);out.mkdir(exist_ok=True,parents=True)
    rows,summary=run(eval_n=args.eval_n)
    with (out/'reference_episode_results.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    (out/'reference_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
