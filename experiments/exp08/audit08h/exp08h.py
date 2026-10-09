"""Emergence Lab 08H: development-only, unlabeled linear mechanism identification.

The learner is NOT given cause identities/timing or truth parameters. It IS given
our linear action/constant-offset two-sensor factorization and intervention design.
These are artificial dynamics. Nothing here tests subjective consciousness.
"""
from __future__ import annotations
import argparse, csv, json, hashlib
from collections import deque
from pathlib import Path
import numpy as np

# The fifth command is 'do nothing' (zero actuation); environment may still drift.
ACTIONS = np.array([[1.,0.],[-1.,0.],[0.,1.],[0.,-1.],[0.,0.]])
CAUSES = ('none','motor','external','sensor','motor_external','external_sensor','nonlinear')
POLICIES = ('repeat','random','cycle','adaptive')
T = 60
CALIBRATION = 22
NOISE = .13


def rotation(k):
    return [np.eye(2),np.array([[0.,-1.],[1.,0.]]),-np.eye(2),np.array([[0.,1.],[-1.,0.]])][k % 4]


def phi(u):
    return np.array([u[0],u[1],1.])


def fit_linear(rows, reference=True):
    """Least squares of observed displacement vs motor command; no truth labels."""
    if not rows: return np.zeros((2,3)), 0, float('nan')
    X=np.array([phi(r['u']) for r in rows])
    Y=np.array([r['z'] if reference else r['y'] for r in rows])
    rank=int(np.linalg.matrix_rank(X,tol=1e-8))
    mat=np.linalg.lstsq(X,Y,rcond=None)[0].T
    resid=Y-X@mat.T
    mse=float(np.mean(np.sum(resid**2,axis=1)))
    return mat,rank,mse


class World:
    def __init__(self, seed:int, cause:str, noise=NOISE):
        assert cause in CAUSES
        self.seed=seed;self.cause=cause;self.noise=noise
        rng=np.random.default_rng(seed)
        # All cause types use same seed, prechange samples, and change timing.
        self.M0=rotation(int(rng.integers(4)))
        self.M1=rotation(1) @ self.M0
        theta=rng.uniform(0,2*np.pi)
        self.d=np.array([np.cos(theta),np.sin(theta)])*.9
        self.s=self.d.copy() # deliberate observational equivalent external/sensor case
        self.q=np.array([.95,-.7])
        self.change_at=int(rng.integers(27,35))
        # Draw environmental noise independent of actions and cause, for counterfactual parity.
        self.nz=rng.normal(0,noise,(T,2))
        self.ny=rng.normal(0,noise,(T,2))
        self.baseline_actions=np.array([0,2,1,3,4]*5)[:CALIBRATION]

    def truth(self,t,u):
        changed=t>=self.change_at
        M=self.M1 if changed and 'motor' in self.cause else self.M0
        d=self.d if changed and 'external' in self.cause else np.zeros(2)
        s=self.s if changed and 'sensor' in self.cause else np.zeros(2)
        extra=self.q*np.abs(u) if changed and self.cause=='nonlinear' else np.zeros(2)
        return M@u+d+extra, s

    def step(self,t,u):
        displacement,bias=self.truth(t,u)
        z=displacement+self.nz[t]
        y=displacement+bias+self.ny[t]
        return {'u':u,'y':y,'z':z, 't':t}


def choose_action(policy,t,rows,alarm, rng):
    if t<CALIBRATION:
        return int([0,2,1,3,4][t%5])
    if policy=='repeat': return 0
    if policy=='random': return int(rng.integers(5))
    if policy=='cycle': return int([0,2,1,3,4][(t-CALIBRATION)%5])
    if policy=='adaptive':
        if alarm is None: return 0
        post=[r for r in rows if r['t']>=alarm]
        X=np.array([phi(r['u']) for r in post]) if post else np.empty((0,3))
        gram=np.eye(3)*.2+X.T@X
        inv=np.linalg.inv(gram)
        leverages=np.array([phi(u)@inv@phi(u) for u in ACTIONS])
        return int(np.argmax(leverages))
    raise ValueError(policy)


def diagnose(baseline,post,has_reference=True,noise_calibrated=False):
    """Returns structure *of our pre-specified additive model*, not discovered cause ontology.

    Rejects explanations when data rank is deficient or residuals large.
    Uses no cause label or scheduled change time.
    """
    if not post:return ('none', False, {})
    measured=post[-24:]
    base=baseline['z'] if has_reference else baseline['y']
    measured_model,rank,residual=fit_linear(measured,reference=has_reference)
    if rank!=3 or len(measured)<9:
        return ('undetermined',False,{'rank':rank,'n':len(measured)})
    # Signal not captured by the linear additive model: abstain on attribution.
    # Static residual cutoff is intentionally stress-tested; noise-scaled version
    # estimates uncertainty only from calibration observations, never truth labels.
    residual_cutoff=max(.24, 6.*baseline['sigma_hat']**2) if noise_calibrated else .24
    if residual>residual_cutoff:
        return ('unknown',False,{'rank':rank,'mse':residual})
    dM=float(np.linalg.norm(measured_model[:,:2]-base[:,:2]))
    dd=float(np.linalg.norm(measured_model[:,2]-base[:,2]))
    ds=0.
    if has_reference:
        diff=np.array([r['y']-r['z'] for r in measured]).mean(axis=0)
        ds=float(np.linalg.norm(diff-baseline['sensor_bias']))
    else:
        # Cannot separate a physically external offset from an offset in only one sensor.
        if dd>.38:return ('undetermined',False,{'identifiability':'external vs sensor alias','dM':dM,'dd':dd})
    flags=[]
    if dM>.4:flags.append('motor')
    if dd>.38:flags.append('external')
    if ds>.38:flags.append('sensor')
    prediction='_'.join(flags) if flags else 'none'
    return prediction,True,{'dM':dM,'dd':dd,'ds':ds,'rank':rank,'mse':residual}


def run_world(seed,cause,policy,noise=NOISE,has_reference=True,noise_calibrated=False):
    w=World(seed,cause,noise)
    rng=np.random.default_rng(seed+980303)
    rows=[];alarm=None;resid_history=deque(maxlen=3)
    baseline=None; alarm_history=[]
    for t in range(T):
        ai=choose_action(policy,t,rows,alarm,rng)
        item=w.step(t,ACTIONS[ai]);item['action']=ai
        if t==CALIBRATION:
            z,rz,_=fit_linear(rows,True)
            y,ry,_=fit_linear(rows,False)
            if min(rz,ry)!=3:raise AssertionError('calibration rank deficient')
            # Residual variance adjusted for the 3 fitted linear coefficients.
            # Both streams contain 2 independent coordinates.
            sigma_hat=float(np.sqrt(sum(np.sum((np.array([r[k] for r in rows])-
                   np.array([phi(r['u']) for r in rows])@m.T)**2)
                   for k,m in [('z',z),('y',y)])/(4*(len(rows)-3))))
            baseline={'z':z,'y':y,'sensor_bias':(y[:,2]-z[:,2]),'sigma_hat':sigma_hat}
        if baseline is not None:
            prior=baseline['z' if has_reference else 'y']
            # Correlated baseline residual is removed in reference mode, but not oracle latent noise.
            dz=item['z']-prior@phi(item['u']) if has_reference else item['y']-prior@phi(item['u'])
            error=float(np.linalg.norm(dz))
            if has_reference:
                dy=(item['y']-item['z'])-baseline['sensor_bias']
                error=max(error,float(np.linalg.norm(dy)))
            alarm_limit=max(.55,4.4*baseline['sigma_hat']) if noise_calibrated else .55
            resid_history.append(error>alarm_limit)
            if alarm is None and len(resid_history)==3 and sum(resid_history)>=2:
                alarm=t
                alarm_history.append(t)
        rows.append(item)
    assert baseline is not None
    # Change detection is decided only from observations, not w.change_at.
    selected=[r for r in rows if alarm is not None and r['t']>=alarm]
    label,identified,info=diagnose(baseline,selected,has_reference,noise_calibrated)
    # Strict truth metric for evaluator ONLY; learner never receives it.
    attribution=label==cause
    # Independent evaluator: prediction error for all unseen hypothetical actions using
    # true world dynamics at end, rather than the particular actions the policy selected.
    M,rank,mse=fit_linear(selected,True) if selected else (baseline['z'],0,0.)
    current_effects=np.array([w.truth(T-1,u)[0] for u in ACTIONS])
    predicted=np.array([M@phi(u) for u in ACTIONS])
    cf_mse=float(np.mean(np.sum((current_effects-predicted)**2,axis=1)))
    probe_cost=sum(int(r['action']!=0) for r in rows[CALIBRATION:])
    return {'seed':seed,'cause':cause,'policy':policy,'reference':int(has_reference),
            'noise':noise,'detector':'calibrated' if noise_calibrated else 'fixed','actual_change':int(cause!='none'), 'change_time':w.change_at,
            'alarm_time':alarm if alarm is not None else '',
            'alarm':int(alarm is not None),'correct':int(attribution),'identified':int(identified),
            'diagnosis':label,'counterfactual_mse':cf_mse,'probe_cost':probe_cost,
            'linear_residual':mse,'n_post':len(selected)}


def evaluate(seeds=96,noise=NOISE,reference=True):
    rows=[]
    for i in range(seeds):
        seed=8_800_000+i*47
        for cause in CAUSES:
            for p in POLICIES:
                rows.append(run_world(seed,cause,p,noise,reference))
    stats={}
    for p in POLICIES:
        sub=[r for r in rows if r['policy']==p]
        changed=[r for r in sub if r['cause'] not in ('none','nonlinear')]
        null=[r for r in sub if r['cause']=='none']
        nonlinear=[r for r in sub if r['cause']=='nonlinear']
        stats[p]={
            'changed_exact_attribution':float(np.mean([r['correct'] for r in changed])),
            'changed_coverage':float(np.mean([r['identified'] for r in changed])),
            'changed_counterfactual_mse':float(np.mean([r['counterfactual_mse'] for r in changed])),
            'false_alarm_rate':float(np.mean([r['alarm'] for r in null])),
            'unknown_abstain_rate':float(np.mean([r['diagnosis']=='unknown' for r in nonlinear])),
            'mean_probe_cost':float(np.mean([r['probe_cost'] for r in sub])),
            'n_worlds':len(sub)
        }
    return rows,stats


def summarize_compare(rows,first='adaptive',other='cycle',seed=182271):
    """Seed is statistical unit, nesting all related causes within each seed."""
    seeds=sorted({r['seed'] for r in rows})
    d=[]
    for s in seeds:
        a=[r for r in rows if r['seed']==s and r['policy']==first and r['cause'] not in ('none','nonlinear')]
        b=[r for r in rows if r['seed']==s and r['policy']==other and r['cause'] not in ('none','nonlinear')]
        d.append(float(np.mean([r['correct'] for r in a])-np.mean([r['correct'] for r in b])))
    rng=np.random.default_rng(seed)
    ci=np.quantile(np.mean(rng.choice(d,size=(10000,len(d)),replace=True),axis=1),[.025,.975])
    return {'contrast':f'{first}_minus_{other}','mean_accuracy_difference':float(np.mean(d)),
        'percentile_seed_bootstrap_95ci':[float(ci[0]),float(ci[1])],
        'n_seeds':len(seeds)}


def save(out,rows,summary):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    with (out/'per_world.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0].keys()));writer.writeheader();writer.writerows(rows)
    (out/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--seeds',type=int,default=96)
    ap.add_argument('--noise',type=float,default=NOISE);ap.add_argument('--out',default='development_outputs')
    opt=ap.parse_args()
    rows,stats=evaluate(opt.seeds,opt.noise)
    summary={'status':'exploratory development only; no preregistration or consciousness measure',
        'seeds':opt.seeds,'noise':opt.noise,'n_cases':len(rows), 'by_policy':stats,
        'adaptive_minus_cycle':summarize_compare(rows,'adaptive','cycle'),
        'adaptive_minus_random':summarize_compare(rows,'adaptive','random')}
    save(opt.out,rows,summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
