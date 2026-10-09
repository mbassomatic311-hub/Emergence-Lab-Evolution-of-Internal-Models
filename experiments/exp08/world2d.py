"""Emergence Lab Experiment 08: independently written 2D DEVELOPMENT simulator.

Explicitly exploratory. No subjective consciousness measure.
Agent never sees true actuator rotation or its own map coordinates.
"""
from dataclasses import dataclass
import numpy as np

N = 13
ACT = np.asarray([[-1,0],[0,1],[1,0],[0,-1]], dtype=np.int16) # up,right,down,left
OBS_DIM = 14 # noisy food-relative x/y, 4 obstacle directions, energy, 4 past-action flags, reward, collision, visibility

@dataclass(frozen=True)
class WorldConfig:
    steps:int=48
    blockers:int=13
    hazard_slip:float=.09
    observation_noise:float=.025
    gust_probability:float=.055
    dropout_probability:float=0.
    reversal:bool=False
    energy_start:float=39.


class World:
    def __init__(self, seed:int, config:WorldConfig):
        self.rng=np.random.default_rng(seed)
        self.cfg=config
        self.blocked=np.zeros((N,N),dtype=bool)
        for _ in range(config.blockers):
            r,c=map(int,self.rng.integers(1,N-1,size=2))
            if (r,c)!=(N//2,N//2):self.blocked[r,c]=True
        self.pos=np.array([N//2,N//2], dtype=np.int16)
        self.rotation=int(self.rng.integers(4))
        self.target=self._place_target()
        self.prev_action=-1
        self.prev_food=0.;self.prev_collision=0.
        self.energy=config.energy_start
        self.food=0
        self.goal_progress=0.0  # development-only diagnostic, never directly observed by agent
        self.alive_steps=0
        self.t=0
        self.done=False
        self._last_obs=None

    def _place_target(self):
        candidates=[]
        for r in range(1,N-1):
            for c in range(1,N-1):
                d=abs(r-int(self.pos[0]))+abs(c-int(self.pos[1]))
                if 3<=d<=7 and not self.blocked[r,c]:candidates.append((r,c))
        if not candidates:
            candidates=[(r,c) for r in range(N) for c in range(N) if not self.blocked[r,c] and (r,c)!=tuple(self.pos)]
        return np.array(candidates[int(self.rng.integers(len(candidates)))],dtype=np.int16)

    def _blocked(self, point):
        r,c=map(int,point)
        return r<0 or r>=N or c<0 or c>=N or bool(self.blocked[r,c])

    def observe(self):
        delta=(self.target-self.pos).astype(float)/6.0
        delta+=self.rng.normal(0,self.cfg.observation_noise,size=2)
        visible=self.rng.random()>=self.cfg.dropout_probability
        if not visible:delta[:]=0.
        neighbours=np.array([self._blocked(self.pos+v) for v in ACT],dtype=float)
        action=np.zeros(4)
        if self.prev_action>=0:action[self.prev_action]=1
        obs=np.r_[delta,neighbours,self.energy/39.,action,self.prev_food,self.prev_collision,float(visible)].astype(float)
        assert len(obs)==OBS_DIM
        self._last_obs=obs
        return obs

    def step(self, action:int):
        if self.done:raise RuntimeError('step after death / end')
        if not (0<=action<4):raise ValueError('invalid command')
        self.prev_action=int(action)
        if self.cfg.reversal and self.t==self.cfg.steps//2:
            self.rotation=(self.rotation+2)%4
        distance_before=float(np.abs(self.target-self.pos).sum())
        physical=(action+self.rotation)%4
        if self.rng.random()<self.cfg.hazard_slip:physical=int(self.rng.integers(4))
        vec=ACT[physical]
        moved=self.pos+vec
        collided=self._blocked(moved)
        if not collided:self.pos=moved
        if self.rng.random()<self.cfg.gust_probability:
            wind=self.pos+ACT[int(self.rng.integers(4))]
            if not self._blocked(wind):self.pos=wind
        distance_after=float(np.abs(self.target-self.pos).sum())
        self.goal_progress += distance_before-distance_after
        ate=bool(np.array_equal(self.pos,self.target))
        self.prev_food=float(ate)
        self.prev_collision=float(collided)
        self.food+=int(ate)
        self.energy-=1.0+1.5*int(collided)
        if ate:
            self.energy=min(45.,self.energy+11.)
            self.target=self._place_target()
        self.t+=1
        self.alive_steps=self.t
        self.done=self.energy<=0 or self.t>=self.cfg.steps
        return ate, collided
