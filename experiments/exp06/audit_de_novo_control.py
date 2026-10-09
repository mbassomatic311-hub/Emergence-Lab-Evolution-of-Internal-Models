"""Post-hoc sensitivity control for Experiment 06 (NOT part of frozen protocol).
Each generation has a fresh, unrelated population. New recurrent links CAN arise by mutation;
no genotypes are inherited from a previous generation. Evaluate final-generation best.
No training labels, no long-term evolutionary accumulation.
"""
from pathlib import Path
import numpy as np, csv, json
from engine import Settings, initialize, expected_payoff

D=Path(__file__).resolve().parent
SEEDS=[100003+101*i for i in range(24)]
CFG=Settings(generations=300)
def fresh_population(seed):
    rng=np.random.default_rng(seed)
    # Use independent fresh genomes with a mutational opportunity in each generation.
    # No information or genotype transfers between generations.
    for generation in range(CFG.generations):
        plain,rec,mask=initialize(rng,CFG)
        mask=(rng.random((CFG.population,4,4))<CFG.new_recurrent_prob)
        rec=rng.normal(0,.7,size=(CFG.population,4,4))*mask
    scores=expected_payoff(plain,rec,mask,q=CFG.q,recurrent_cost=CFG.recurrent_cost)
    best=int(np.argmax(scores))
    gross=expected_payoff(plain[best:best+1],rec[best:best+1],mask[best:best+1],q=CFG.q,recurrent_cost=0)[0]
    return float(gross),int(mask[best].sum())

rows=[dict(seed=s,mode='de_novo_no_inheritance_with_mutation',exact_payoff=p,active_links=n) for s in SEEDS for p,n in [fresh_population(s)]]
with (D/'audit_de_novo_control.csv').open('w',newline='') as f:
    w=csv.DictWriter(f, fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
a=np.array([x['exact_payoff'] for x in rows]); rng=np.random.default_rng(9942)
boots=a[rng.integers(0,len(a),size=(12000,len(a)))].mean(axis=1)
import csv as csvmod
with (D/'results_per_seed.csv').open() as f:
    legacy=list(csvmod.DictReader(f))
e={int(z['seed']):float(z['exact_payoff']) for z in legacy if z['mode']=='evolve'}
diff=np.array([e[z['seed']]-z['exact_payoff'] for z in rows]);b2=diff[rng.integers(0,len(a),size=(12000,len(a)))].mean(axis=1)
out=dict(n=24,mean=float(a.mean()),ci95=np.quantile(boots,[.025,.975]).tolist(),min=float(a.min()),max=float(a.max()),difference_mean=float(diff.mean()),difference_ci95=np.quantile(b2,[.025,.975]).tolist(),evolve_wins=int((diff>0).sum()),nonzero=int((a>1e-8).sum()),mean_links=float(np.mean([z['active_links'] for z in rows])),status='POST-HOC, not frozen protocol')
(D/'audit_de_novo_metrics.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
