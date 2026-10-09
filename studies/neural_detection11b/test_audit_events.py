"""Synthetic fixture tests only; no human EEG or ratings tested here."""
import csv
import io
import unittest
from audit_events import audit_participant, parse_rows, numeric, audit_all, REQUIRED

COLUMNS = ["onset","duration","trial_type","event_value","event_sample",
           "response_time","response_time2","stimamp","stimon","sdt","confidence"]

def row(t, kind, confidence="0.75", stimon="0.9"):
    return {"onset":str(t),"duration":"0","trial_type":kind,"event_value":"100",
            "event_sample":str(int(t*1024)),"response_time":"0.9",
            "response_time2":"1.2","stimamp":"1.1","stimon":stimon,
            "sdt":"h","confidence":confidence}

def fixture(conf="0.75", include_outcome=True, lead=False):
    rows=[row(-1,"stim-thr")] if lead else []
    rows += [row(0,"stim-adapt",conf)]
    if include_outcome: rows.append(row(4,"hit",conf))
    rows += [row(4.5,"conf",conf),row(5,"conf-resp",conf)]
    return rows

class EventAuditTests(unittest.TestCase):
    def test_one_clean_trial(self):
        a=audit_participant(fixture())
        self.assertEqual(a["starts"],1)
        self.assertEqual(a["outcome_complete"],1)
        self.assertEqual(a["valid_joint_labels"],1)
        self.assertEqual(a["usable_nominal_windows"],1)
    def test_missing_detection_cannot_be_imputed(self):
        a=audit_participant(fixture(include_outcome=False))
        self.assertEqual(a["unpaired_or_ambiguous_outcomes"],1)
        self.assertEqual(a["valid_joint_labels"],0)
    def test_missing_confidence_cannot_be_imputed(self):
        a=audit_participant(fixture(conf="n/a"))
        self.assertEqual(a["missing_confidence"],1)
        self.assertEqual(a["valid_joint_labels"],0)
    def test_premature_response_blocks_window(self):
        a=audit_participant([row(0,"stim-adapt"),row(1.0,"hit"),
                             row(1.1,"conf"),row(1.5,"conf-resp")])
        self.assertEqual(a["usable_nominal_windows"],0)
    def test_extra_events_are_not_confused_with_trials(self):
        a=audit_participant(fixture(lead=True))
        self.assertEqual(a["starts"],1)
        self.assertEqual(a["extra_non_task_markers"],1) # preserved as extra metadata
    def test_parse_tsv_and_reject_missing_columns(self):
        f=io.StringIO();w=csv.DictWriter(f,delimiter="\t",fieldnames=COLUMNS);w.writeheader();w.writerows(fixture())
        self.assertEqual(len(parse_rows(f.getvalue())),4)
        with self.assertRaises(ValueError): parse_rows("onset\ttrial_type\n0\tstim-adapt\n")
    def test_time_order_must_be_monotonic(self):
        f=io.StringIO();w=csv.DictWriter(f,delimiter="\t",fieldnames=COLUMNS);w.writeheader()
        w.writerows([row(5,"stim-adapt"),row(2,"hit")])
        with self.assertRaises(ValueError):parse_rows(f.getvalue())
    def test_nan_invalid(self):
        self.assertIsNone(numeric("n/a"))
        self.assertIsNone(numeric("NaN"))
    def test_invalid_duplicate_outcomes(self):
        a=audit_participant([row(0,"stim-adapt"),row(4,"hit"),row(4.2,"miss"),row(4.4,"conf"),row(5,"conf-resp")])
        self.assertEqual(a["unpaired_or_ambiguous_outcomes"],1)
    def test_aggregate_uses_no_trial_level_values(self):
        def fetch(path):
            if path=="participants.tsv":return "participant_id\nsub-01\nsub-02\n"
            f=io.StringIO();w=csv.DictWriter(f,delimiter="\t",fieldnames=COLUMNS);w.writeheader();w.writerows(fixture());return f.getvalue()
        a=audit_all(fetch=fetch)
        self.assertEqual(a["participants_in_public_tsv"],2)
        self.assertEqual(a["valid_joint_labels"],2)
        self.assertNotIn("per_subject",a)
        self.assertTrue(a["nominal_window_not_eeg_verified"])

if __name__=="__main__":unittest.main()
