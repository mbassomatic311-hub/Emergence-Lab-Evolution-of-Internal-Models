"""Generate seed-cluster level tidy data from complete prequential event logs."""
from __future__ import annotations
import argparse,csv
from collections import defaultdict
from pathlib import Path

def aggregate(src,dest):
    sums=defaultdict(float); counts=defaultdict(int)
    with Path(src).open(newline='') as f:
        for r in csv.DictReader(f):
            k=(r['seed'],r['cause'],r['policy'],r['reference'],r['noise'],r['phase'],r['model'])
            sums[k]+=float(r['range_sqerr']);counts[k]+=1
    out=Path(dest);out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('w',newline='') as f:
        fields=['seed','cause','policy','reference','noise','phase','model','n_steps','mean_range_sqerr']
        w=csv.writer(f);w.writerow(fields)
        for k in sorted(sums):w.writerow([*k,counts[k],sums[k]/counts[k]])
    return len(sums)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--directory',required=True);a=p.parse_args()
    d=Path(a.directory)
    print(aggregate(d/'per_prediction.csv',d/'per_world.csv'))
