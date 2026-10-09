import unittest
from audit_block_gaps import inspect, CUTS

def tsv(trials=212,breaks=True):
    lines=["onset\tsample\tvalue"]
    t=0
    for i in range(trials):
        if i:
            t+=54 if breaks and i in CUTS else 23
        lines.append(f"{t}\t{int(t*512)}\t65282")
    return "\n".join(lines)+"\n"
class Tests(unittest.TestCase):
    def test_expected_boundaries(self):
        x=inspect(tsv())
        self.assertEqual(x["boundaries_exceed_internal_median_by_10s"],7)
        self.assertTrue(x["matches_expected_212"])
    def test_no_breaks_no_false_claim(self):
        self.assertEqual(inspect(tsv(breaks=False))["boundaries_exceed_internal_median_by_10s"],0)
    def test_unexpected_trial_count_never_reinterpreted(self):
        self.assertFalse(inspect(tsv(trials=210))["matches_expected_212"])
if __name__=="__main__":unittest.main()
