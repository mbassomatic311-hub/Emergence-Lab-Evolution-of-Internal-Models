import unittest
from unittest.mock import patch
import numpy as np
import inspect_signal as s

class Tests(unittest.TestCase):
    def test_correct_sample_major_fdt_interleave(self):
        x=np.array([[1.,2.,3.],[4.,5.,6.]],dtype="<f4")
        with patch.object(s,"get_range",return_value=x.tobytes()) as reader:
            y=s.get_window(1.,2.,1,3)
        np.testing.assert_array_equal(y,x.T)
        self.assertEqual(reader.call_args.args[1:],(12,35))
    def test_range_limit(self):
        with self.assertRaises(ValueError):s.get_range("unused",0,1000000)
    def test_invalid_negative_epoch(self):
        with self.assertRaises(ValueError):s.get_window(-1,.25,512,64)
    def test_230_hz_power(self):
        t=np.arange(200)/1000
        self.assertGreater(float(s.power_ratio(np.sin(2*np.pi*230*t),1000)),
                           float(s.power_ratio(np.sin(2*np.pi*100*t),1000)))
    def test_download_limit_not_bypassed(self):
        with self.assertRaises(ValueError):s.get_range("unused",30,1)
if __name__=="__main__":unittest.main()
