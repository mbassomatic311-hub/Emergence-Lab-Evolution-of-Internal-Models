"""Study 10, *exploratory development only*: multimodal predictive compression.

No consciousness observation or claim. Linear synthetic worlds are intentionally
constructed with either shared or modality-private latent physical variables.
The goal is to test conditional predictive-compression claims and their failures,
not to discover a natural law from a designed generator.

Usage: python study10.py --out output --seeds 24
Dependencies: numpy
"""
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path
import numpy as np

GROUPS = 3
CHANNELS_EACH = 16
CHANNELS = GROUPS*CHANNELS_EACH
K = 4
ALLOCATION = (2,1,1)
REGULARIZATIONS = (0.01, 0.1, 1.0, 10.0, 100.0)
TRAIN_SIZES = (120, 1000)
CONDITIONS = ('shared','independent')
MODEL_NAMES = ('action_only','raw_ridge','joint_pca4','split_pca4','random_projection4','joint_pca8','split_pca8','target_shuffled_joint_pca4','supervised_rank4')
BASE_SEEDS = tuple(310_007 + j*1009 for j in range(24))


def world_parameters(seed: int, condition: str):
    assert condition in CONDITIONS
    rng = np.random.default_rng(seed + 912)
    d = 3 if condition == 'shared' else 9
    # Construct an action-affected, stable physical state, with no neural claims.
    blocks=[]
    for _ in range(d//3):
        Q,_ = np.linalg.qr(rng.normal(size=(3,3)))
        # Negative determinant is harmless for the dynamics.
        blocks.append(0.82*Q)
    A=np.zeros((d,d))
    for j,b in enumerate(blocks): A[j*3:(j+1)*3,j*3:(j+1)*3]=b
    B=rng.normal(0,0.16,size=(d,2))
    maps=[]
    for g in range(GROUPS):
        W=np.zeros((CHANNELS_EACH,d))
        part = slice(0,3) if condition=='shared' else slice(g*3,(g+1)*3)
        W[:,part]=rng.normal(size=(CHANNELS_EACH,3))/np.sqrt(3)
        maps.append(W)
    return A,B,np.concatenate(maps,axis=0)


def generate(seed: int, condition: str, n:int, segment:int):
    """Independent deterministic split-specific noise and initial states.

    Truth (A,B,state) is NEVER used by a fitted model.
    """
    A,B,W=world_parameters(seed,condition)
    rng=np.random.default_rng(seed*1000 + segment*100_003 + 19)
    d=A.shape[0]
    warm=85
    actions=rng.normal(size=(n+warm,2))
    disturbance=rng.normal(0,.28,size=(n+warm,d))
    x=np.zeros((n+warm+1,d),dtype=float)
    x[0]=rng.normal(size=d)
    for t in range(n+warm):
        x[t+1]=A@x[t]+B@actions[t]+disturbance[t]
    # Present noisy multi-modal measurement at t, score independently noisy t+1.
    now=x[warm:warm+n]@W.T + rng.normal(0,.32,size=(n,CHANNELS))
    future=x[warm+1:warm+n+1]@W.T + rng.normal(0,.32,size=(n,CHANNELS))
    return now,actions[warm:],future


def standardization(data):
    mean=data.mean(axis=0)
    sd=data.std(axis=0)
    sd=np.maximum(sd,0.08)
    return mean,sd


def eig_pca(x,k):
    # PCA on development training observations ONLY (no future target labels).
    cov=(x.T@x)/max(1,len(x)-1)
    w,v=np.linalg.eigh(cov)
    return v[:,-k:][:,::-1].copy()


def feature_maps(xtrain, name:str, seed:int):
    if name in ('raw_ridge','action_only','supervised_rank4'):
        return None
    if name=='target_shuffled_joint_pca4':
        return eig_pca(xtrain,4)
    if name.startswith('joint_pca'):
        k=4 if name=='joint_pca4' else 8
        return eig_pca(xtrain,k)
    if name.startswith('split_pca'):
        alloc=ALLOCATION if name=='split_pca4' else (3,3,2)
        mats=[]
        for j,sz in enumerate(alloc):
            block=xtrain[:,j*CHANNELS_EACH:(j+1)*CHANNELS_EACH]
            M=eig_pca(block,sz)
            mat=np.zeros((CHANNELS,sz))
            mat[j*CHANNELS_EACH:(j+1)*CHANNELS_EACH,:]=M
            mats.append(mat)
        return np.concatenate(mats,axis=1)
    if name=='random_projection4':
        rng=np.random.default_rng(seed+78833)
        M=rng.normal(size=(CHANNELS,4))
        Q,_=np.linalg.qr(M)
        return Q[:,:4]
    raise ValueError(name)


def make_features(x,a,name,M):
    if name=='action_only':
        features=a
    elif name in ('raw_ridge','supervised_rank4'):
        features=np.concatenate([x,a],axis=1)
    else:
        features=np.concatenate([x@M,a],axis=1)
    return np.column_stack([np.ones(len(x)),features])


def ridge_fit(design, y, alpha):
    gram=design.T@design
    r=np.eye(gram.shape[0])*alpha
    r[0,0]=0.0  # do not regularize intercept
    return np.linalg.solve(gram+r,design.T@y)


def predictor_performance(xtr,atr,ytr,xval,aval,yval,xt,at,yt,name,seed):
    M=feature_maps(xtr,name,seed)
    X=make_features(xtr,atr,name,M)
    V=make_features(xval,aval,name,M)
    T=make_features(xt,at,name,M)
    candidates=[]
    target=ytr
    if name=='target_shuffled_joint_pca4':
        rng=np.random.default_rng(seed+912361)
        target=ytr[rng.permutation(len(ytr))]
    for alpha in REGULARIZATIONS:
        B=ridge_fit(X,target,alpha)
        if name=='supervised_rank4':
            # Control with a supervised rank-four bottleneck on sensory inputs.
            # The action and intercept coefficients remain unrestricted.
            U,S,VT=np.linalg.svd(B[1:CHANNELS+1,:],full_matrices=False)
            B=B.copy()
            B[1:CHANNELS+1,:]=(U[:,:4]*S[:4])@VT[:4,:]
        candidates.append((float(np.mean((V@B-yval)**2)),alpha,B))
    _,alpha,coef=min(candidates,key=lambda t:(t[0],t[1]))
    pred=T@coef
    reported_dims=(4+at.shape[1]) if name=='supervised_rank4' else (X.shape[1]-1)
    return float(np.mean((pred-yt)**2)),float(alpha),reported_dims


def fit_world(seed, condition, ntrain, corruption=False):
    now,act,out=generate(seed,condition,ntrain,1)
    xv,av,yv=generate(seed,condition,220,2)
    xt,at,yt=generate(seed,condition,480,3)
    xmean,xsd=standardization(now)
    ymean,ysd=standardization(out)
    def sx(x):return (x-xmean)/xsd
    def sy(y):return (y-ymean)/ysd
    # Optional previously unseen observed-sensor corruption. A single modality
    # is corrupted at inference only; target remains the original next signal.
    if corruption:
        rng=np.random.default_rng(seed+421097)
        xt=xt.copy()
        xt[:,0:CHANNELS_EACH]+=rng.normal(0,1.6,size=(len(xt),CHANNELS_EACH))
    train=sx(now); val=sx(xv); test=sx(xt)
    yr=sy(out); yval=sy(yv); yt=sy(yt)
    rows=[]
    for name in MODEL_NAMES:
        mse,alpha,ndim=predictor_performance(train,act,yr,val,av,yval,test,at,yt,name,seed)
        rows.append({'seed':seed,'condition':condition,'ntrain':ntrain,'test_corruption':int(corruption),
                     'model':name,'mse':mse,'ridge_alpha':alpha,'feature_dimensions_excluding_bias':ndim})
    return rows


def paired_bootstrap(x,y,nboot=3000,seed=79931):
    diffs=np.asarray(x)-np.asarray(y)
    rng=np.random.default_rng(seed)
    draws=rng.integers(len(diffs),size=(nboot,len(diffs)))
    means=diffs[draws].mean(axis=1)
    return {'mean_difference':float(diffs.mean()),
            'ci95':[float(v) for v in np.quantile(means,[.025,.975])],
            'n_positive':int(np.sum(diffs>0)),
            'n_negative':int(np.sum(diffs<0)),
            'n_tied':int(np.sum(diffs==0))}


def summarize(rows):
    grouped={}
    for r in rows:
        key=(r['condition'],r['ntrain'],r['test_corruption'],r['model'])
        grouped.setdefault(key,[]).append(r)
    averages=[]
    for key,vals in sorted(grouped.items()):
        averages.append({'condition':key[0],'ntrain':key[1],'test_corruption':key[2],
                         'model':key[3],'mean_mse':float(np.mean([r['mse'] for r in vals])),
                         'n_seeds':len(vals)})
    comparisons=[]
    for condition in CONDITIONS:
      for ntrain in TRAIN_SIZES:
        for corrupt in (0,1):
          part=[r for r in rows if r['condition']==condition and r['ntrain']==ntrain and r['test_corruption']==corrupt]
          by={(r['model'],r['seed']):r['mse'] for r in part}
          seeds=sorted(set(r['seed'] for r in part))
          for a,b in [('joint_pca4','split_pca4'),('joint_pca4','raw_ridge'),('joint_pca4','supervised_rank4'),('joint_pca4','random_projection4'),('joint_pca8','raw_ridge')]:
            c=paired_bootstrap([by[(a,s)] for s in seeds],[by[(b,s)] for s in seeds],seed=6601+ntrain+corrupt)
            comparisons.append({'condition':condition,'ntrain':ntrain,'test_corruption':corrupt,
                                'contrast':f'{a} minus {b}',**c})
    return {'status':'EXPLORATORY DEVELOPMENT ONLY; all worlds generated by researcher, no consciousness measurement',
            'seed_count':len(set(r['seed'] for r in rows)),
            'synthetic_input_channels':CHANNELS,
            'latent_world_factors_shared':3,'latent_world_factors_independent':9,
            'pca_latent_dimensions':[4,8],
            'model_validation':'alpha chosen on separately seeded development validation split',
            'rows':len(rows),'means':averages,'contrasts':comparisons}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--seeds',type=int,default=24)
    p.add_argument('--out',type=Path,default=Path('output'))
    args=p.parse_args()
    if args.seeds<1 or args.seeds>len(BASE_SEEDS):raise ValueError('1 <= seeds <= 24')
    args.out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for condition in CONDITIONS:
      for n in TRAIN_SIZES:
        for seed in BASE_SEEDS[:args.seeds]:
          rows+=fit_world(seed,condition,n,False)
          rows+=fit_world(seed,condition,n,True)
    summary=summarize(rows)
    with (args.out/'per_seed.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    (args.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    for fn in ['per_seed.csv','summary.json']:
        print(fn,hashlib.sha256((args.out/fn).read_bytes()).hexdigest())
    for item in summary['means']:
      if item['test_corruption']==0 and item['ntrain']==120 and item['model'] in ('raw_ridge','joint_pca4','split_pca4','random_projection4'):
        print(item['condition'],item['model'],round(item['mean_mse'],5))

if __name__=='__main__':main()
