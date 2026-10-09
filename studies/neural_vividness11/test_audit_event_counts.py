"""Synthetic unit tests only; no real EEG or ratings."""
import tempfile
import unittest
from pathlib import Path
from audit_event_counts import analyze, audit, parse_events

def fixture(n=212):
    lines=["onset\tduration\tsample\tvalue","0.5\tn/a\t256\t65284","18\tn/a\t9216\t65285","318\tn/a\t162816\t65286"]
    for i in range(n):
        t=400+20*i
        for offset,code in [(0,65281),(4,65282),(9,65283),(14,65284)]:
            lines.append(f"{t+offset}\tn/a\t{(t+offset)*512}\t{code}")
    return "\n".join(lines)+"\n"

class EventTests(unittest.TestCase):
    def test_extra_trial_counts_are_not_silently_dropped(self):
        r=analyze("sub-001",fixture())
        self.assertEqual(r["text_onsets"],212)
        self.assertEqual(r["text_markers_minus_210_ratings"],2)
        self.assertEqual(r["leading_task_markers"],"65284")
        self.assertFalse(r["ratings_to_events_join_verified"])
    def test_order_errors_visible(self):
        r=analyze("sub-001",fixture().replace("\t65283","\t65281",1))
        self.assertGreater(r["ordering_errors"],0)
    def test_ordering_timestamps_are_validated(self):
        x=fixture().replace("409\tn/a","10\tn/a",1)
        with self.assertRaises(ValueError):parse_events(x)
    def test_partial_data_rejected(self):
        with self.assertRaises(ValueError):parse_events("onset\tx\n")
    def test_full_fake_roster_no_data_fetch(self):
        roster="participant_id\tparticipant_original_id\n"+"".join(f"sub-{i:03d}\tP{i+100}\n" for i in range(1,48))
        def fake(path):return roster if path=="participants.tsv" else fixture()
        with tempfile.TemporaryDirectory() as d:
            r=audit(d,fetcher=fake)
            self.assertEqual(r["difference_vs_210_distribution"],{"2":47})
            self.assertFalse(r["ratings_to_events_join_verified"])
            self.assertTrue((Path(d)/"summary.json").exists())

if __name__=="__main__":unittest.main()
