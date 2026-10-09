"""Exploratory event/subjective-report alignment audit for OpenNeuro ds001785.

Fetches text-only PUBLIC BIDS event files at an immutable upstream Git commit.
No human EEG downloaded. No individual behavior records written.
Outcomes and ratings are NEVER interpreted as actual neural measurements.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
from pathlib import Path
from urllib.request import Request, urlopen

UPSTREAM_COMMIT = "53be0167e7068aba693d57923eb4c9c037878159"
ROOT = f"https://raw.githubusercontent.com/OpenNeuroDatasets/ds001785/{UPSTREAM_COMMIT}"
REQUIRED = {"onset","duration","trial_type","event_value","event_sample",
            "response_time","response_time2","stimamp","stimon","sdt","confidence"}
OUTCOMES = {"hit","miss","cr","fa"}
SOURCE_DOI = "10.18112/openneuro.ds001785.v1.1.1"
# Only a *prospective candidate* 0.5 s window after nominal stimulus time;
# confirm physical synchronization to EEG and timing of catch events first.
WINDOW_S = 0.5


def fetch_text(path: str) -> str:
    if path.startswith("/") or ".." in Path(path).parts:
        raise ValueError("Unsafe file path")
    req = Request(f"{ROOT}/{path}", headers={"User-Agent":"EmergenceLab-Study11b-Audit/0.1"})
    with urlopen(req, timeout=50) as f:
        data = f.read(350_000)
        if f.read(1):
            raise ValueError(f"Unexpectedly large file: {path}")
    return data.decode("utf-8-sig")


def parse_rows(content: str):
    reader = csv.DictReader(io.StringIO(content), delimiter="\t")
    if not reader.fieldnames or not REQUIRED.issubset(set(reader.fieldnames)):
        raise ValueError("Missing required event columns")
    rows = list(reader)
    if not rows or any(None in row for row in rows):
        raise ValueError("Missing event rows or malformed columns")
    times = [float(x["onset"]) for x in rows]
    if any(not math.isfinite(t) for t in times):
        raise ValueError("Nonfinite event onset")
    if any(t < prev for prev,t in zip(times,times[1:])):
        raise ValueError("Nonmonotonic event time")
    return rows


def numeric(value) -> float | None:
    try:
        x = float(value)
        return x if math.isfinite(x) else None
    except (ValueError, TypeError):
        return None


def audit_participant(rows: list[dict]) -> dict:
    """One nonidentifying summary; do not leak trial-level reports."""
    start_ids = [i for i,r in enumerate(rows) if r["trial_type"] == "stim-adapt"]
    stats = {"starts":len(start_ids),"outcome_complete":0,"confidence_present":0,
             "valid_joint_labels":0,"usable_nominal_windows":0,
             "unpaired_or_ambiguous_outcomes":0,"missing_confidence":0,
             "unsafe_nominal_timing":0,"extra_non_task_markers":0}
    if not start_ids:
        raise ValueError("No adaptive task starts")
    other = [r for r in rows if r["trial_type"] not in
             OUTCOMES | {"stim-adapt","conf","conf-resp"}]
    stats["extra_non_task_markers"] = len(other)
    for i,idx in enumerate(start_ids):
        end = start_ids[i+1] if i+1<len(start_ids) else len(rows)
        block = rows[idx:end]
        outcome = [r for r in block if r["trial_type"] in OUTCOMES]
        ratings = [r for r in block if r["trial_type"] == "conf"]
        rating_responses = [r for r in block if r["trial_type"] == "conf-resp"]
        labels_ok = len(outcome)==1
        confidence = numeric(block[0].get("confidence"))
        confidence_ok = (confidence is not None and 0 <= confidence <= 1
                         and len(ratings)==1 and len(rating_responses)==1)
        stats["outcome_complete"] += int(labels_ok)
        stats["confidence_present"] += int(confidence_ok)
        stats["unpaired_or_ambiguous_outcomes"] += int(not labels_ok)
        stats["missing_confidence"] += int(not confidence_ok)
        stats["valid_joint_labels"] += int(labels_ok and confidence_ok)

        # This is an audit of the *candidate* epoch only, not actual EEG alignment:
        # start+stimon is nominal. Do NOT download/analyze EEG based solely on this.
        on = numeric(block[0].get("onset"))
        delay = numeric(block[0].get("stimon"))
        resp = numeric(outcome[0]["onset"]) if labels_ok else None
        valid_epoch = (labels_ok and confidence_ok and on is not None
                       and delay is not None and 0 <= delay <= 2.5
                       and resp is not None and on+delay+WINDOW_S < resp)
        stats["usable_nominal_windows"] += int(valid_epoch)
        stats["unsafe_nominal_timing"] += int(not valid_epoch)
    return stats


def audit_all(fetch=fetch_text):
    participants = list(csv.DictReader(io.StringIO(fetch("participants.tsv")),delimiter="\t"))
    ids = [r["participant_id"] for r in participants]
    if not ids or len(ids)!=len(set(ids)):
        raise ValueError("Invalid participant IDs")
    per = []
    for sub in ids:
        # Avoid path traversal even if metadata were malicious.
        if not sub.startswith("sub-") or not sub[4:].isdigit():
            raise ValueError("Unexpected subject code")
        path = f"{sub}/ses-01/eeg/{sub}_ses-01_task-adapt_run-01_events.tsv"
        data = parse_rows(fetch(path))
        per.append(audit_participant(data))
    agg = {k:sum(s[k] for s in per) for k in per[0]}
    agg.update({
        "participants_in_public_tsv":len(ids),
        "participants_with_500_starts":sum(s["starts"]==500 for s in per),
        "participants_with_fewer_starts":sum(s["starts"]<500 for s in per),
        "range_starts_per_participant":[min(s["starts"] for s in per),
                                        max(s["starts"] for s in per)],
        "source_doi":SOURCE_DOI,
        "upstream_commit":UPSTREAM_COMMIT,
        "data_examined":"public BIDS event metadata only; no EEG data or human-level predictors",
        "trial_matching":"detection outcome and confidence are recorded within each event block",
        "nominal_window_not_eeg_verified":True,
        "study_status":"EXPLORATORY PRE-FLIGHT; NO EEG RESULT OR CONSCIOUSNESS MEASUREMENT"
    })
    return agg


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",default="event_audit_aggregate.json")
    args=parser.parse_args()
    result=audit_all()
    p=Path(args.output);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps(result,sort_keys=True,indent=2))


if __name__=="__main__":
    main()
