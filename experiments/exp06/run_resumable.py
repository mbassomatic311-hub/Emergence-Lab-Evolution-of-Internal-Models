"""Resumable run of Experiment 06: writes every independent replicate."""
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
from run_study import SEEDS,MODES,worker
import json
DIR=Path(__file__).resolve().parent/'runs';DIR.mkdir(exist_ok=True)

def run_one(task):
    seed,mode,gens=task
    p=DIR/f'{mode}_{seed}.json'
    if p.exists(): return f'cached {p.stem}'
    row,tr,agent=worker(task)
    temp=DIR/f'{mode}_{seed}.partial'
    temp.write_text(json.dumps({'summary':row,'trace':tr,'agent':agent},separators=(',',':')))
    temp.replace(p)
    return p.stem

if __name__=='__main__':
    tasks=[(seed,mode,300) for mode in MODES for seed in SEEDS]
    missing=[t for t in tasks if not (DIR/f'{t[1]}_{t[0]}.json').exists()]
    print(f'{len(tasks)-len(missing)} cached; {len(missing)} remaining',flush=True)
    with ProcessPoolExecutor(max_workers=2) as pool:
        fs={pool.submit(run_one,t):t for t in missing}
        for i,f in enumerate(as_completed(fs),1):
            print(f'Finished {i}/{len(missing)}: {f.result()}',flush=True)
