"""Verify all primary rows and aggregate summaries of 08J (no statistical claims)."""
import argparse
import csv
import json
import math
from pathlib import Path

CATEGORICAL={'seed','cause','policy','action_counts','counterfactual_by_action'}

def check(reference,candidate):
    ref=Path(reference);cand=Path(candidate)
    orig=list(csv.DictReader((ref/'per_world.csv').open(newline='')))
    new=list(csv.DictReader((cand/'per_world.csv').open(newline='')))
    assert len(orig)==len(new) and len(orig)>0,(len(orig),len(new))
    assert orig[0].keys()==new[0].keys()
    for i,(a,b) in enumerate(zip(orig,new)):
        for col,x in a.items():
            y=b[col]
            if col=='counterfactual_by_action':
                aa,bb=json.loads(x),json.loads(y)
                assert aa.keys()==bb.keys()
                for key in aa: assert math.isclose(aa[key],bb[key],rel_tol=1e-10,abs_tol=1e-10),(i,col,key)
            elif col in CATEGORICAL:assert x==y,(i,col,x,y)
            else:assert math.isclose(float(x),float(y),rel_tol=1e-10,abs_tol=1e-10),(i,col,x,y)
    aa=json.loads((ref/'summary.json').read_text())
    bb=json.loads((cand/'summary.json').read_text())
    def recursive(a,b,path='root'):
        assert type(a)==type(b),path
        if isinstance(a,dict):
            assert a.keys()==b.keys(),path
            for k in a:recursive(a[k],b[k],path+'.'+k)
        elif isinstance(a,list):
            assert len(a)==len(b),path
            for k,(x,y) in enumerate(zip(a,b)):recursive(x,y,path+str(k))
        elif isinstance(a,float):assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10),(path,a,b)
        else:assert a==b,(path,a,b)
    recursive(aa,bb)
    return len(orig)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--reference',required=True)
    p.add_argument('--candidate',required=True)
    args=p.parse_args()
    n=check(args.reference,args.candidate)
    print(f'PASS: {n} complete rows and aggregate summary reproducible within 1e-10 tolerance')
if __name__=='__main__':main()
