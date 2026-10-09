"""Experiment 08 exploratory audit: fitness noise, unequal initial worlds, and selection.

Development seeds only. NEVER cite as confirmatory or evidence for consciousness.
Does not modify the original Experiment 08 engine or its pilot data.
"""
from __future__ import annotations
import argparse, csv, json
from pathlib import Path
import numpy as np
from controllers import random_genome, mutate, NeuralController
from engine import fitness, simulate, DEV_SEEDS


def rank_corr(a, b):
    """Pearson correlation of mid-ranks; return None if ranks are degenerate."""
    def ranks(x):
        values = np.asarray(x, dtype=float)
        order = np.argsort(values, kind='stable')
        result = np.zeros(len(values), dtype=float)
        i = 0
        while i < len(values):
            j = i+1
            while j < len(values) and values[order[j]] == values[order[i]]: j += 1
            result[order[i:j]] = (i+j-1)/2.
            i = j
        return result
    x, y = ranks(a), ranks(b)
    if x.std() == 0 or y.std() == 0: return None
    return float(np.corrcoef(x,y)[0,1])


def initial_fitness_audit(seed, n=18, high_eval=16):
    """Compare noisy 2-episode selection scores with a separate many-episode estimate.

    Original: candidate i gets seed+i*13; common-conditions variant removes
    that index, so at least initial world/reset PRNG seeds are comparable.
    High precision evaluation uses independent development seeds (NOT holdout).
    """
    rng=np.random.default_rng(seed)
    pop=[random_genome(rng) for _ in range(n)]
    original=np.array([fitness(g,seed+i*13,True,episodes=2) for i,g in enumerate(pop)])
    common=np.array([fitness(g,seed,True,episodes=2) for g in pop])
    high=np.array([fitness(g,seed+550000,True,episodes=high_eval) for g in pop])
    def overlap(v):
        k=min(4,n)
        return len(set(np.argsort(v)[-k:])&set(np.argsort(high)[-k:]))
    row={
      'seed':int(seed), 'n_genomes':n, 'high_eval_episodes':high_eval,
      'original_zero_food_proxy_fraction':float(np.mean(original <= .3+1e-12)),
      'common_zero_food_proxy_fraction':float(np.mean(common <= .3+1e-12)),
      'original_std':float(np.std(original)),
      'common_std':float(np.std(common)),
      'high_eval_std':float(np.std(high)),
      'spearman_original_vs_high':rank_corr(original,high),
      'spearman_common_vs_high':rank_corr(common,high),
      'top4_overlap_original_vs_high':overlap(original),
      'top4_overlap_common_vs_high':overlap(common),
      'mean_original':float(np.mean(original)), 'mean_common':float(np.mean(common)),
      'mean_high':float(np.mean(high))
    }
    return row


def train_common_conditions(seed, recurrent=True, n=18, generations=14, fitness_episodes=2):
    """Development-only comparison of candidate-common initial stochastic worlds.

    Isolates the seed-per-candidate difference and candidate evaluation fairness.
    Does NOT test architectural superiority or change original training source.
    """
    rng=np.random.default_rng(seed)
    pop=[random_genome(rng) for _ in range(n)]
    trajectories=[]
    for g in range(generations):
        # Critical intervention: same episode seed schedule for all candidates.
        scores=np.array([fitness(p,seed+g*2213,recurrent,episodes=fitness_episodes) for p in pop])
        edges=np.array([p[1].sum() for p in pop])
        adjusted=scores-.002*edges
        trajectories.append({'seed':seed,'generation':g,'mean_fitness':float(scores.mean()),
          'best_fitness':float(scores.max()),'mean_edges':float(edges.mean()),
          'score_spread':float(np.std(scores))})
        order=np.argsort(adjusted,kind='stable')
        ranks=np.empty_like(order,dtype=float);ranks[order]=np.arange(n)
        probs=(1.+ranks)**2;probs/=probs.sum()
        parents=[pop[int(rng.choice(n,p=probs))] for _ in range(n)]
        pop=[mutate(rng,p) for p in parents]
    # Also use a shared development-world schedule for the final selection.
    scores=[fitness(p,seed+320000,recurrent,episodes=3) for p in pop]
    return pop[int(np.argmax(scores))],trajectories


def pilot(seeds=DEV_SEEDS[:3],n=18,generations=14,eval_n=12,high_eval=16):
    rows=[]; noise=[]; curves=[]
    for seed in seeds:
        noise.append(initial_fitness_audit(seed,n,high_eval))
        champ,trajectory=train_common_conditions(seed,n=n,generations=generations)
        curves+=trajectory
        for env in ('stable','shift+dropout'):
            scores=[simulate(NeuralController(champ),seed+1200000+i*733,env=env)
                    for i in range(eval_n)]
            rows.append({'seed':seed,'training':'candidate_common_initial_conditions',
                  'environment':env,'mean_food':float(np.mean([p[0] for p in scores])),
                  'mean_survival':float(np.mean([p[1] for p in scores])),
                  'recurrent_edges':int(champ[1].sum())})
    return rows,noise,curves


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',default='development_fitness_audit')
    ap.add_argument('--seeds',type=int,default=3)
    ap.add_argument('--population',type=int,default=18)
    ap.add_argument('--generations',type=int,default=14)
    ap.add_argument('--eval-n',type=int,default=12)
    ap.add_argument('--high-eval',type=int,default=16)
    args=ap.parse_args()
    assert 1<=args.seeds<=len(DEV_SEEDS), 'only enumerated development seeds are allowed'
    path=Path(args.out);path.mkdir(parents=True,exist_ok=True)
    a,b,c=pilot(DEV_SEEDS[:args.seeds],args.population,args.generations,args.eval_n,args.high_eval)
    for name,rows in [('pilot_results.csv',a),('fitness_noise.csv',b),('learning_curves.csv',c)]:
        with (path/name).open('w',newline='') as f:
            wr=csv.DictWriter(f,fieldnames=rows[0].keys());wr.writeheader();wr.writerows(rows)
    means={env:float(np.mean([r['mean_food'] for r in a if r['environment']==env])) for env in ('stable','shift+dropout')}
    summary={'status':'development-only exploratory audit; not preregistered',
      'seeds':list(DEV_SEEDS[:args.seeds]),'population':args.population,
      'generations':args.generations,'fitness_episodes':2,'high_eval':args.high_eval,
      'mean_food_by_environment':means,
      'noise_diagnostics':{
       'mean_rank_corr_original':float(np.mean([r['spearman_original_vs_high'] for r in b if r['spearman_original_vs_high'] is not None])) if any(r['spearman_original_vs_high'] is not None for r in b) else None,
       'mean_rank_corr_common':float(np.mean([r['spearman_common_vs_high'] for r in b if r['spearman_common_vs_high'] is not None])) if any(r['spearman_common_vs_high'] is not None for r in b) else None,
       'mean_original_zero_food_proxy_fraction':float(np.mean([r['original_zero_food_proxy_fraction'] for r in b]))}}
    (path/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
