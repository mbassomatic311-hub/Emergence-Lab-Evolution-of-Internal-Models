"""Independent scientific invariants for development-only 08D. Not confirmatory."""
import unittest
import numpy as np
from world2d import ACT, OBS_DIM, World, WorldConfig
from audit08d_learning import (create_traces,transitions,fit_prototypes,
        infer_posterior,score,LearnedForwardController,SEED_OFFSETS,T)

class Audit08DTests(unittest.TestCase):
    def test_development_seed_namespaces_are_distinct(self):
        self.assertEqual(len(set(SEED_OFFSETS.values())),len(SEED_OFFSETS))
        self.assertTrue(all(a>10_000_000 for a in SEED_OFFSETS.values()))
        samples=[create_traces(4,k)[3] for k in SEED_OFFSETS]
        self.assertEqual(sum(len(s) for s in samples),len(set(sum(samples,[]))))

    def test_data_deterministic_and_never_stitches_dead_agents(self):
        a=create_traces(5,'train_shift');b=create_traces(5,'train_shift')
        for x,y in zip(a[:3],b[:3]):self.assertTrue(np.array_equal(x,y))
        for x,y,w in zip(*a[:3]):
            n=int(w.sum())
            self.assertTrue(np.all(w[:n]))
            self.assertFalse(w[n:].any())
            self.assertFalse(x[n:].any())
            self.assertTrue(np.all((y[w]>=0)&(y[w]<4)))

    def test_reversal_labels_do_not_peek_at_future_motor_change(self):
        x,y,w,seeds=create_traces(8,'train_shift')
        for i,seed in enumerate(seeds):
            world=World(seed,WorldConfig(reversal=True,dropout_probability=.12))
            original=world.rotation
            self.assertEqual(int(y[i,0]),original)
            if w[i,24]:
                self.assertEqual(int(y[i,24]),original)
            if w[i,25]:
                self.assertEqual(int(y[i,25]),(original+2)%4)

    def test_no_future_sensor_in_classifier(self):
        x,y,w,_=create_traces(18,'train_stable')
        model=fit_prototypes(x,y,w)
        z,_=infer_posterior(x,w,model)
        changed=x.copy()
        changed[:,18:,:]=0
        w2=w.copy();w2[:,18:]=False
        z2,_=infer_posterior(changed,w2,model)
        self.assertTrue(np.array_equal(z[:,:18],z2[:,:18]))

    def test_structured_model_has_real_training_support(self):
        x,y,w,_=create_traces(24,'train_stable')
        m=fit_prototypes(x,y,w,regularize=0)
        self.assertGreater(m['counts'].min(),4)
        self.assertTrue(np.all(np.isfinite(m['means'])))
        self.assertGreater(m['scale'],0)
        self.assertEqual(m['means'].shape,(4,4,2))

    def test_conditional_emissions_correspond_to_learned_motion(self):
        x,y,w,_=create_traces(64,'train_stable')
        m=fit_prototypes(x,y,w,regularize=0)
        mse=np.mean((m['means']-ACT[np.add.outer(np.arange(4),np.arange(4))%4])**2)
        self.assertLess(float(mse),.08)

    def test_action_ablation_degrades_development_accuracy(self):
        x,y,w,_=create_traces(48,'train_stable')
        test,targets,mask,_=create_traces(24,'development_test_shift')
        model=fit_prototypes(x,y,w)
        full=score(infer_posterior(test,mask,model)[0],targets,mask)['overall']['accuracy']
        no_action=score(infer_posterior(test,mask,model,scramble=True,seed=82008)[0],targets,mask)['overall']['accuracy']
        self.assertGreater(full-no_action,.35)

    def test_memory_ablation_degrades_development_accuracy(self):
        x,y,w,_=create_traces(48,'train_stable')
        test,targets,mask,_=create_traces(24,'development_test_shift')
        model=fit_prototypes(x,y,w)
        full=score(infer_posterior(test,mask,model)[0],targets,mask)['overall']['accuracy']
        no_mem=score(infer_posterior(test,mask,model,memory=False)[0],targets,mask)['overall']['accuracy']
        self.assertGreater(full-no_mem,.10)

    def test_deployment_controller_receives_only_observations(self):
        x,y,w,_=create_traces(24,'train_stable')
        model=fit_prototypes(x,y,w)
        obs=np.zeros(OBS_DIM);obs[-1]=1;obs[1]=.5
        agent=LearnedForwardController(model)
        a=agent.act(obs,np.random.default_rng(45))
        self.assertIn(a,[0,1,2,3])

    def test_bad_data_group_rejected(self):
        with self.assertRaises(ValueError):create_traces(1,'confirmatory_holdout')

if __name__=='__main__':unittest.main()
