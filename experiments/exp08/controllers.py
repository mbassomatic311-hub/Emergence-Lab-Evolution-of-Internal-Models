"""Fixed baselines and topology-mutating recurrent candidate for Experiment 08 development."""
import numpy as np
from world2d import OBS_DIM

HIDDEN=5
PARAMS=OBS_DIM*HIDDEN+HIDDEN*HIDDEN+HIDDEN+OBS_DIM*4+HIDDEN*4+4
# recurrent edges are all initially absent; heritable changes can enable/disable them

def random_genome(rng):
    w=rng.normal(0,.45, PARAMS)
    mask=np.zeros((HIDDEN,HIDDEN),dtype=bool)
    return (w, mask)


def mutate(rng,genome):
    w,mask=genome
    w=w.copy();mask=mask.copy()
    change=rng.random(PARAMS)<.10
    w[change]+=rng.normal(0,.22,np.count_nonzero(change))
    np.clip(w,-4,4,out=w)
    for _ in range(int(rng.poisson(.85))):
        a,b=map(int,rng.integers(HIDDEN,size=2));mask[a,b]=not mask[a,b]
    return (w,mask)

class NeuralController:
    def __init__(self,genome,recurrent=True):
        flat,mask=genome
        index=0
        def take(shape):
            nonlocal index
            n=int(np.prod(shape));value=flat[index:index+n].reshape(shape);index+=n
            return value
        self.wi=take((OBS_DIM,HIDDEN));self.wr=take((HIDDEN,HIDDEN))*mask
        self.bias=take((HIDDEN,));self.w_direct=take((OBS_DIM,4))
        self.w_out=take((HIDDEN,4));self.out_bias=take((4,))
        assert index==PARAMS
        self.recurrent=recurrent
        self.h=np.zeros(HIDDEN)
        self.last_predicted_displacement=None
        self.prediction_count=0

    def act(self,obs,rng):
        h=np.tanh(obs@self.wi + (self.h@self.wr if self.recurrent else 0) +self.bias)
        self.h=h
        scores=obs@self.w_direct + h@self.w_out+self.out_bias
        return int(np.argmax(scores))

class RandomController:
    def act(self,obs,rng):return int(rng.integers(4))

class GreedyController:
    def act(self,obs,rng):
        return _desired(obs)


def _desired(obs):
    dr,dc=obs[:2]
    if abs(dr)>abs(dc):return 2 if dr>0 else 0
    return 1 if dc>0 else 3

class ComparatorController:
    """One-step action-consequence compass: no neural memory or evolution.
    Estimates 4 possible motor rotations from differences in the observed target vector.
    Rejects transitions where the target respawned or visibility was lost.
    """
    def __init__(self,forget=.77,noise_floor=.13,epsilon=.10):
        self.loglik=np.zeros(4)
        self.prev=None;self.prev_cmd=None
        self.forget=forget;self.noise_floor=noise_floor;self.epsilon=epsilon
    def act(self,obs,rng):
        from world2d import ACT
        if self.prev is not None and self.prev_cmd is not None and obs[-1] and self.prev[-1] and not obs[-3]:
            measured=(self.prev[:2]-obs[:2])*6
            expected=np.array([ACT[(self.prev_cmd+k)%4] for k in range(4)], dtype=float)
            err=np.sum((expected-measured)**2,axis=1)
            self.loglik=self.forget*self.loglik-err/(2*self.noise_floor**2)
            self.loglik-=np.max(self.loglik)
        self.prev=obs.copy()
        rotation=int(np.argmax(self.loglik))
        desired=_desired(obs)
        cmd=(desired-rotation)%4
        if rng.random()<self.epsilon:cmd=int(rng.integers(4))
        self.prev_cmd=cmd
        return cmd

class RecentHistoryController:
    """Nonrecurrent controller with 2 observations worth of explicit history.
    Strong alternative to a memory-unit architecture. Not optimized in the pilot.
    """
    def __init__(self):self.comp=ComparatorController()
    def act(self,obs,rng):return self.comp.act(obs,rng)

class BayesianController:
    """Explicit 4-state actuator-rotation posterior (hand designed, not evolved).

    Transition prior allows changes; likelihood permits slipping/gust noise.
    Sensor history after food respawn/dropout is intentionally discarded.
    """
    def __init__(self,transition=.06,movement_noise=.55,epsilon=.06):
        self.p=np.ones(4)/4
        self.prev=None;self.prev_cmd=None
        self.transition=transition
        self.movement_noise=movement_noise
        self.epsilon=epsilon
    def act(self,obs,rng):
        from world2d import ACT
        if self.prev is not None and self.prev_cmd is not None and self.prev[-1] and obs[-1] and not obs[-3]:
            step=(self.prev[:2]-obs[:2])*6
            vectors=ACT[np.array([(self.prev_cmd+j)%4 for j in range(4)])].astype(float)
            sq=np.sum((vectors-step)**2,axis=1)
            loglike=-sq/(2*self.movement_noise**2)
            likelihood=np.exp(loglike-loglike.max())
            prior=(1-self.transition)*self.p+self.transition*.25
            post=prior*likelihood
            self.p=post/post.sum() if post.sum()>0 else np.ones(4)/4
        rotation=int(np.argmax(self.p))
        action=(_desired(obs)-rotation)%4
        if rng.random()<self.epsilon:action=int(rng.integers(4))
        self.prev=obs.copy();self.prev_cmd=action
        return action
