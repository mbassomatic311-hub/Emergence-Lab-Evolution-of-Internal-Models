"""Development-only check for likely two pre-task trials and 7x30 blocks.

This program cannot discover which poem occurred in which EEG event and must
never be used to produce a verified EEG-rating join. Only public timing metadata.
"""
import argparse
import json
from pathlib import Path
from statistics import median
from audit_event_counts import fetch, parse_events

CUTS=(2,32,62,92,122,152,182)

def inspect(events_tsv):
    events=parse_events(events_tsv)
    starts=[e["t"] for e in events if e["value"]=="65282"]
    if len(starts)!=212:
        return {"text_onsets":len(starts),"matches_expected_212":False,
                "boundary_gaps_seconds":[],"internal_median_gap":None}
    gaps={i:starts[i]-starts[i-1] for i in range(1,len(starts))}
    internal=[v for i,v in gaps.items() if i not in CUTS]
    boundary=[gaps[i] for i in CUTS]
    med=median(internal)
    return {
      "text_onsets":len(starts),
      "matches_expected_212":True,
      "boundary_gaps_seconds":[round(v,4) for v in boundary],
      "boundary_median_gap":round(median(boundary),4),
      "internal_median_gap":round(med,4),
      "boundaries_exceed_internal_median_by_10s":sum(x>med+10 for x in boundary),
      "min_boundary_gap":round(min(boundary),4),
      "minimum_margin_vs_internal_median":round(min(boundary)-med,4)}

def main(out):
    import csv,io
    roster=list(csv.DictReader(io.StringIO(fetch("participants.tsv")),delimiter="\t"))
    assert len(roster)==47
    results=[]
    for x in roster:
        subject=x["participant_id"]
        data=inspect(fetch(f"{subject}/eeg/{subject}_task-readpoetry_events.tsv"))
        results.append((subject,data))
    good=[x for _,x in results if x["matches_expected_212"]]
    summary={
      "status":"POST-HOC timing pattern exploration; NOT verified practice-trial or poem identity",
      "participants":len(roster),
      "consistent_212_onsets":len(good),
      "candidate_boundaries_after_presentations":[2,32,62,92,122,152,182],
      "cutoff_inference":"Two candidate introduction sequences followed by seven blocks of thirty",
      "participants_all_7_boundary_gaps_gt_internal_median_plus_10s":
          sum(x["boundaries_exceed_internal_median_by_10s"]==7 for x in good),
      "participants_min_boundary_gap_gt_within_block_median":
          sum(x["minimum_margin_vs_internal_median"]>0 for x in good),
      "median_candidate_gap_seconds":round(median([x["boundary_median_gap"] for x in good]),3),
      "median_internal_gap_seconds":round(median([x["internal_median_gap"] for x in good]),3),
      "join_verified":False,
      "required_fix":"Experiment owner must verify practice trials and supply participant-specific actual stimulus presentation sequence or equivalent event-to-poem keyed log"}
    path=Path(out);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
    return summary
if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("--out",required=True)
    main(a.parse_args().out)
