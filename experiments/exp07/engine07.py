"""Emergence Lab Experiment 07. Artificial evolutionary control of unknown action effects.
All scores are simulated behavior, never consciousness measurements.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, os
from pathlib import Path
import numpy as np

D=8  # genotype: baseline memory, carry, action-effect, sensory, reactive, interaction, memory-only, action bias
POP=64
GENS=90
TRAIN_EPISODES=3
STEPS=40
ELITE=6
SEED_BASE=870000


def init_pop(rng, n):
    return rng.normal(0, 1.25, (n,D))


def episodes(params, rng, episodes=3, switch=False, mode='full', noise=0.04, return_trace=False):
    """Vectorized stochastic agent lifetimes. Each agent chooses its own action.
    No explicit labels for actuator polarity are supplied to agents.
    Every agent sees a noisy signed bearing to food; action effects have hidden polarity.
    """
    n=len(params)
    all_food=np.zeros(n); all_alive=np.zeros(n)
    for ep in range(episodes):
        x=np.zeros(n, dtype=float)
        target=(rng.choice(np.array([-1.,1.]), size=n)*rng.integers(3,7,size=n)).astype(float)
        polarity=rng.choice(np.array([-1.,1.]),size=n)
        energy=np.full(n,20.,dtype=float)
        alive=np.ones(n,dtype=bool)
        memory=np.zeros(n); prev_obs=np.zeros(n); prev_action=np.zeros(n)
        fed=np.zeros(n)
        count=np.zeros(n)
        for t in range(STEPS):
            if switch and t==20:
                polarity=-polarity
            obs=(target-x)/6.0 + rng.normal(0,noise,size=n)
            if t>0:
                # observable consequence of preceding action: relative bearing shift, normalized by step size
                eff=-(obs-prev_obs)*prev_action*6.
                if mode=='scrambled':
                    eff=-(obs-prev_obs)*rng.choice(np.array([-1.,1.]),size=n)*6.
                upd=np.tanh(params[:,0]+params[:,1]*memory+params[:,2]*eff+params[:,3]*obs)
                if mode!='reactive':
                    memory=np.where(alive,upd,memory)
            m=np.zeros_like(memory) if mode=='reactive' else memory
            logits=params[:,4]*obs + params[:,5]*obs*m + params[:,6]*m + params[:,7]
            action=np.where(logits>=0,1.,-1.)
            x=np.where(alive, x+polarity*action, x)
            energy=np.where(alive,energy-1.,energy)
            eaten=alive & (np.abs(target-x)<0.5)
            fed+=eaten.astype(float)
            energy=np.where(eaten,np.minimum(27.,energy+12.),energy)
            # do not confuse newly spawned food with travel from the last motor command
            new_target=x+rng.choice(np.array([-1.,1.]),size=n)*rng.integers(3,7,size=n)
            target=np.where(eaten,new_target,target)
            # Store only actual pre-movement observation and action as sensorimotor history
            # On food relocation suppress spurious effect input by restarting memory next tick
            prev_obs=np.where(eaten,(target-x)/6.,obs)
            prev_action=np.where(eaten,0.,action)
            count+=alive.astype(float)
            alive=alive & (energy>0)
        all_food+=fed; all_alive+=count
    return all_food/episodes, all_alive/(episodes*STEPS)


def train_one(seed, mode='full'):
    rng=np.random.default_rng(seed)
    pop=init_pop(rng,POP)
    trajectories=[]
    for g in range(GENS):
        # Stochastic fitness from finite experiences, not a deterministic payoff oracle
        foods, alive=episodes(pop,rng,TRAIN_EPISODES,False,'reactive' if mode=='reactive' else 'full')
        fitness=foods+0.15*alive
        trajectories.append([g,float(np.mean(foods)),float(np.max(foods)),float(np.mean(alive))])
        # Selection and inheritance are separate interventions
        if mode=='no_inheritance':
            pop=init_pop(rng,POP)
            continue
        probabilities=np.maximum(fitness,0)+0.06
        probabilities=probabilities/probabilities.sum()
        if mode=='random_selection':
            probabilities=np.full(POP,1/POP)
        # In all inherited conditions, introduce heritable mutations and crossover
        offspring=[]
        for i in range(POP):
            p=rng.choice(POP,p=probabilities)
            q=rng.choice(POP,p=probabilities)
            child=np.where(rng.random(D)<0.5,pop[p],pop[q]).copy()
            selected=rng.random(D)<0.19
            child+=selected * rng.normal(0,0.50,size=D)
            child=np.clip(child,-8,8)
            offspring.append(child)
        pop=np.array(offspring)
    # Evaluate final population on fresh development episodes. Select elites ONLY using development score.
    dev_rng=np.random.default_rng(seed+75_000_000)
    score,_=episodes(pop,dev_rng,16,False,'reactive' if mode=='reactive' else 'full')
    indices=np.argsort(-score,kind='stable')[:ELITE]
    return pop[indices], np.array(trajectories), float(np.mean(score[indices]))


def evaluate(elites, seed, mode):
    # All conditions evaluated on stable and unexpected reversal episodes. No test-task selection.
    # Repeat each elite across 128 independent, common test episodes.
    npop=elites.repeat(128,axis=0)
    out={}
    for env in ['stable','reversal']:
        rng=np.random.default_rng(seed+ (100_000_000 if env=='stable' else 200_000_000))
        food, alive=episodes(npop,rng,1,env=='reversal', 'reactive' if mode=='reactive' else 'full')
        out[env+'_food']=float(food.mean())
        out[env+'_survival']=float(alive.mean())
    if mode=='full':
        rng=np.random.default_rng(seed+200_000_000)
        food,alive=episodes(npop,rng,1,True,'scrambled')
        out['scrambled_reversal_food']=float(food.mean())
        out['scrambled_reversal_survival']=float(alive.mean())
    return out


def run(seed, modes):
    result=[]; curves={}
    for mode in modes:
        elites, trajectory, develop=train_one(seed,mode)
        summary={'seed':seed,'condition':mode,'development_food':develop}
        summary.update(evaluate(elites,seed,mode))
        result.append(summary)
        curves[mode]=trajectory
    return result,curves


def summarize(rows):
    # Seed is the independent analysis unit. Retain negative and zero differences.
    rng=np.random.default_rng(50607)
    keys=['full','reactive','random_selection','no_inheritance']
    by={(int(r['seed']),r['condition']):r for r in rows}
    seeds=sorted(set(int(r['seed']) for r in rows))
    res={'n_seeds':len(seeds),'conditions':{},'paired_differences':{}}
    for key in keys:
        items=[by[(s,key)] for s in seeds]
        res['conditions'][key]={field:float(np.mean([float(i[field]) for i in items]))
             for field in ['stable_food','reversal_food','stable_survival','reversal_survival','development_food']}
    for ctrl in ['reactive','random_selection','no_inheritance']:
        dif=np.array([float(by[(s,'full')]['reversal_food'])-float(by[(s,ctrl)]['reversal_food']) for s in seeds])
        bs=np.mean(rng.choice(dif,size=(10000,len(dif)),replace=True),axis=1)
        res['paired_differences'][f'full_minus_{ctrl}']={'mean':float(dif.mean()),'ci95':[float(x) for x in np.quantile(bs,[.025,.975])], 'positive':int(np.sum(dif>0)), 'negative':int(np.sum(dif<0)),'zero':int(np.sum(dif==0))}
    dif=np.array([float(by[(s,'full')]['reversal_food'])-float(by[(s,'full')]['scrambled_reversal_food']) for s in seeds])
    bs=np.mean(rng.choice(dif,size=(10000,len(dif)),replace=True),axis=1)
    res['paired_differences']['full_minus_scrambled']={'mean':float(dif.mean()),'ci95':[float(x) for x in np.quantile(bs,[.025,.975])], 'positive':int(sum(dif>0)), 'negative':int(sum(dif<0)),'zero':int(sum(dif==0))}
    return res


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--seeds',type=int,default=32)
    parser.add_argument('--seed-start',type=int,default=SEED_BASE)
    parser.add_argument('--out',type=str,default='.')
    opts=parser.parse_args()
    modes=['full','reactive','random_selection','no_inheritance']
    dest=Path(opts.out);dest.mkdir(parents=True,exist_ok=True)
    allrows=[]; curves={}
    for i in range(opts.seeds):
        seed=opts.seed_start+i*71
        results,history=run(seed,modes)
        allrows.extend(results)
        for k,v in history.items(): curves[f'{seed}_{k}']=v.tolist()
        if (i+1)%4==0: print(f'seeds completed: {i+1}/{opts.seeds}',flush=True)
    with (dest/'results_per_seed.csv').open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(allrows[0].keys())); wr.writeheader();wr.writerows(allrows)
    (dest/'trajectories.json').write_text(json.dumps(curves))
    summary=summarize(allrows)
    (dest/'summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(summary,indent=2))

if __name__=='__main__': main()
