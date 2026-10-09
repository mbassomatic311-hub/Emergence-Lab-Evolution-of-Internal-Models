"""Validate newly generated seed outputs against versioned development artifacts."""
from pathlib import Path
import csv,json,math,sys

ROOT=Path(__file__).resolve().parent

def compare(a,b,path='$'):
    if isinstance(a,float):
        if not math.isclose(a,b,rel_tol=0,abs_tol=1e-8):
            raise AssertionError((path,a,b))
    elif isinstance(a,dict):
        assert a.keys()==b.keys(),path
        for k in a:compare(a[k],b[k],path+'.'+str(k))
    elif isinstance(a,list):
        assert len(a)==len(b),path
        for i,(x,y) in enumerate(zip(a,b)):compare(x,y,path+f'[{i}]')
    else:assert a==b,(path,a,b)


def verify(expected,actual):
    for name in ('summary.json','per_world.csv'):
        a=Path(expected)/name;b=Path(actual)/name
        if name.endswith('json'):
            compare(json.loads(a.read_text()),json.loads(b.read_text()))
        else:
            with a.open(newline='') as fa,b.open(newline='') as fb:
                x=list(csv.DictReader(fa));y=list(csv.DictReader(fb))
            assert len(x)==len(y),(name,len(x),len(y))
            for i,(ra,rb) in enumerate(zip(x,y)):
                assert ra.keys()==rb.keys()
                for k in ra:
                    if k in ('noise','counterfactual_mse','linear_residual'):
                        compare(float(ra[k]),float(rb[k]),f'{name}/{i}/{k}')
                    else:assert ra[k]==rb[k],(name,i,k,ra[k],rb[k])
    print('Reproduced',Path(expected).name)

if __name__=='__main__':
    if len(sys.argv)!=5:raise SystemExit('Usage: python check_reproduction.py saved-main new-main saved-stress new-stress')
    verify(sys.argv[1],sys.argv[2]);verify(sys.argv[3],sys.argv[4]);print('Both studies verified')
