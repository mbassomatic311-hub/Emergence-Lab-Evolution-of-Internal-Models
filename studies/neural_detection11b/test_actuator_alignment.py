"""Fully synthetic only; no EEG bytes or human reports stored."""
import unittest
import numpy as np
import actuator_alignment as x

class Tests(unittest.TestCase):
    def test_event_alignment_and_classes(self):
        hdr="onset\tstimon\ttrial_type\tevent_sample\n"
        txt=(hdr+"20\t0.5\tstim-adapt\t20480\n23\t0.5\thit\t23552\n"
                  +"25\t0.3\tstim-adapt\t25600\n28\t0.3\tcr\t28672\n")
        self.assertEqual([r["delivered"] for r in x.trials_from_events(txt)],[True,False])
    def test_bad_sample_rejected(self):
        txt="onset\tstimon\ttrial_type\tevent_sample\n20\t0.5\tstim-adapt\t20400\n23\t0.5\thit\t23552\n"
        self.assertEqual(x.trials_from_events(txt),[])
    def test_bandpass_recovers_tactile_frequency(self):
        rng=np.random.default_rng(4)
        t=np.arange(round(3.6*x.FS))/x.FS
        signal=.001*rng.normal(size=len(t))
        mask=(t>1.45)&(t<1.55)
        signal[mask]+=np.sin(2*np.pi*230*t[mask])
        curve=x.bandpower_curve(signal)
        off=np.arange(0,2,.025)
        score=x.measure_offsets(curve,off)
        self.assertGreater(score[np.argmin(abs(off-1.21))],5)
    def test_early_late_split_disjoint(self):
        items=[dict(onset=i,delivered=i%2==0) for i in range(80)]
        cal,val=x.fixed_calibration_validation(items,6)
        self.assertFalse({r["onset"] for r in cal}&{r["onset"] for r in val})
    def test_no_pulse_never_claims_alignment(self):
        o=np.arange(0,.5,.1)
        cal=[dict(delivered=d,score=np.ones(len(o))) for d in [True]*6+[False]*6]
        val=[dict(delivered=d,score=np.ones(len(o)),nominal=1.,response=3.)
             for d in [True]*6+[False]*6]
        self.assertFalse(x.summarize(cal,val,o)["physical_onset_verified"])

if __name__=="__main__":unittest.main()
