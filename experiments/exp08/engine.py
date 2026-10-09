"""Development-only simulation. NOT A PREREGISTERED OR CONFIRMATORY EXPERIMENT."""
import argparse
import csv
import json
from pathlib import Path
import numpy as np
from world2d import World,WorldConfig
from controllers import random_genome,mutate,NeuralController,RandomController,GreedyController,ComparatorController,BayesianController,HIDDEN

DEV_SEEDS=(1103,1205,1411,1607,1801,2003)
CONDITIONS=('evolved_recurrent','evolved_feedforward','random_selection')


def simulate(controller,seed,env='stable', config=None,return_progress=False):
    cfg=config or WorldConfig(reversal=(env!='stable'),dropout_probability=.12 if env=='shift+dropout' else 0.)
    world=World(seed,cfg)
    rng=np.random.default_rng(seed+99991)
    while not world.done:
        obs=world.observe()
        cmd=controller.act(obs,rng)
        world.step(cmd)
    return (world.food, world.alive_steps/world.cfg.steps, world.goal_progress) if return_progress else (world.food, world.alive_steps/world.cfg.steps)


def fitness(genome, seed, recurrent, episodes=2, signal='sparse'):
    """Selection fitness is a designed experimental variable; NEVER consciousness.

    The shaped variant uses a privileged training-only simulator statistic
    (target-distance progress) not directly available to agents. This tests
    sparse-selection failure, not naturalistic reproduction.
    """
    if signal not in ('sparse','shaped'):raise ValueError(signal)
    scores=[]
    for i in range(episodes):
        food,survival,progress=simulate(NeuralController(genome,recurrent),seed+i*137,return_progress=True)
        scores.append(food + .3*survival + (.25*progress if signal=='shaped' else 0))
    return float(np.mean(scores))


def train_population(seed,condition,pop_size=22,generations=18,selection_signal='sparse'):
    if condition not in CONDITIONS:raise ValueError(condition)
    rng=np.random.default_rng(seed)
    pop=[random_genome(rng) for _ in range(pop_size)]
    progression=[]
    for g in range(generations):
        score=np.array([fitness(p,seed+g*2213+i*13,condition!='evolved_feedforward',signal=selection_signal) for i,p in enumerate(pop)])
        edges=np.array([p[1].sum() for p in pop])
        adjusted=score-0.002*edges
        progression.append({'seed':seed,'condition':condition,'generation':g,'mean_score':float(score.mean()),'best_score':float(score.max()),'mean_recurrent_edges':float(edges.mean())})
        if condition=='random_selection':probs=np.ones(pop_size)/pop_size
        else:
            order=np.argsort(adjusted)
            ranks=np.empty_like(order,dtype=float);ranks[order]=np.arange(pop_size)
            probs=(1.+ranks)**2;probs=probs/probs.sum()
        parents=[pop[int(rng.choice(pop_size,p=probs))] for _ in range(pop_size)]
        pop=[mutate(rng,p) for p in parents]
    # pick candidate using only new stable development episodes, not shifted test results
    scored=[fitness(p,seed+320000+i*13,condition!='evolved_feedforward',episodes=3,signal=selection_signal) for i,p in enumerate(pop)]
    return pop[int(np.argmax(scored))],progression


def benchmark(seed, controller, env):
    controllers={'random':RandomController,'greedy':GreedyController,'comparator':ComparatorController,'bayesian':BayesianController}
    return simulate(controllers[controller](),seed,env=env)


def pilot(seeds=DEV_SEEDS,pop_size=22,generations=18,eval_n=12,selection_signal='sparse'):
    rows=[];curves=[]
    for seed in seeds:
        for condition in CONDITIONS:
            champ,trajectory=train_population(seed,condition,pop_size,generations,selection_signal)
            curves.extend(trajectory)
            agents=[NeuralController(champ,recurrent=(condition!='evolved_feedforward')) for _ in range(eval_n)]
            for env in ('stable','shift+dropout'):
                scores=[simulate(agent,seed+1200000+i*733,env=env) for i,agent in enumerate(agents)]
                rows.append({'seed':seed,'condition':condition,'environment':env,'mean_food':float(np.mean([a[0] for a in scores])),'mean_survival':float(np.mean([a[1] for a in scores])),'recurrent_edges':int(champ[1].sum())})
        for condition in ('random','greedy','comparator','bayesian'):
            for env in ('stable','shift+dropout'):
                scores=[benchmark(seed+1200000+i*733,condition,env) for i in range(eval_n)]
                rows.append({'seed':seed,'condition':condition,'environment':env,'mean_food':float(np.mean([a[0] for a in scores])),'mean_survival':float(np.mean([a[1] for a in scores])),'recurrent_edges':''})
        print('pilot development seed complete:',seed,flush=True)
    return rows,curves


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',default='development')
    parser.add_argument('--generations',type=int,default=18)
    parser.add_argument('--population',type=int,default=22)
    parser.add_argument('--seeds',type=int,default=3)
    parser.add_argument('--eval-n',type=int,default=12)
    parser.add_argument('--selection-signal',choices=('sparse','shaped'),default='sparse')
    args=parser.parse_args()
    dest=Path(args.out);dest.mkdir(parents=True,exist_ok=True)
    seeds=DEV_SEEDS[:args.seeds]
    rows,curves=pilot(seeds,args.population,args.generations,args.eval_n,args.selection_signal)
    with (dest/'pilot_results.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    with (dest/'pilot_learning_curves.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=curves[0].keys());w.writeheader();w.writerows(curves)
    summary={c:{e:float(np.mean([r['mean_food'] for r in rows if r['condition']==c and r['environment']==e])) for e in ('stable','shift+dropout')} for c in CONDITIONS+('random','greedy','comparator','bayesian')}
    (dest/'pilot_summary.json').write_text(json.dumps({'status':'development only, NOT preregistered','selection_signal':args.selection_signal,'seeds':seeds,'generations':args.generations,'population':args.population,'episodes_per_evaluation':args.eval_n,'food_means':summary},indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
