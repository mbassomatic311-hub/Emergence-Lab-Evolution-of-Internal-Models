"""Compare regenerated experiment summaries and seed-level data against archives.

Floating-point comparisons permit cross-platform last-bit differences but require
exact seed/method/cause/phase counts and outputs with tight absolute tolerance.
"""
import argparse,csv,json,math
from pathlib import Path


def close(a,b,path='root'):
    if isinstance(a,dict):
        assert isinstance(b,dict) and a.keys()==b.keys(),path
        for k in a:close(a[k],b[k],path+'.'+k)
    elif isinstance(a,list):
        assert isinstance(b,list) and len(a)==len(b),path
        for i,(x,y) in enumerate(zip(a,b)):close(x,y,path+'['+str(i)+']')
    elif isinstance(a,(float,int)) and not isinstance(a,bool):
        assert math.isclose(float(a),float(b),abs_tol=1e-10,rel_tol=0),(path,a,b)
    else: assert a==b,(path,a,b)


def check(reference,candidate):
    ref=Path(reference);rep=Path(candidate)
    close(json.loads((ref/'summary.json').read_text()),json.loads((rep/'summary.json').read_text()),'summary')
    for name in ('alarms.csv','per_world.csv'):
        with (ref/name).open(newline='') as f,(rep/name).open(newline='') as g:
            a=list(csv.DictReader(f));b=list(csv.DictReader(g))
        assert len(a)==len(b),(name,len(a),len(b))
        assert list(a[0])==list(b[0]),(name,'schema')
        for i,(x,y) in enumerate(zip(a,b)):
            for k in x:
                if k in ('mean_range_sqerr','noise'):
                    assert math.isclose(float(x[k]),float(y[k]),abs_tol=1e-10,rel_tol=0),(name,i,k)
                else:assert x[k]==y[k],(name,i,k,x[k],y[k])
    print('Verified:',reference,'==',candidate)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--reference',default='.')
    for flag in ('main','repeat','noise'):p.add_argument('--candidate-'+flag,required=True)
    opt=p.parse_args()
    for label,path in (('development',opt.candidate_main),('restricted_actions',opt.candidate_repeat),('high_noise',opt.candidate_noise)):
        check(Path(opt.reference)/label,path)
