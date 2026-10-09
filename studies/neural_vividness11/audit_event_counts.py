"""Read-only public EEG event audit for Study 11; NO EEG samples or ratings.

The marker streams contain no poem identity. This code intentionally cannot join
individual sensory recordings to participant ratings.
"""
import argparse
import csv
import io
import json
from collections import Counter
from pathlib import Path
from urllib.request import Request, urlopen

SOURCE_COMMIT="b7e80bf9d225e8a5be06ee8358b7484972464edd"
BASE=f"https://raw.githubusercontent.com/OpenNeuroDatasets/ds006648/{SOURCE_COMMIT}"
TASK=("65281","65282","65283","65284")
REST=("65285","65286","65287","65288")

def fetch(path):
    request=Request(f"{BASE}/{path}",headers={"User-Agent":"EmergenceLab-PublicEventsAudit/1.0"})
    with urlopen(request,timeout=40) as stream:
        data=stream.read(500_000+1)
    if len(data)>500_000:raise ValueError("Unexpected large public metadata file")
    return data.decode("utf-8-sig")

def parse_events(tsv):
    reader=csv.DictReader(io.StringIO(tsv),delimiter="\t")
    if not {"onset","sample","value"}.issubset(set(reader.fieldnames or [])):
        raise ValueError("Bad events TSV column schema")
    events=[]
    for item in reader:
        events.append({"t":float(item["onset"]),"sample":int(item["sample"]),"value":str(int(item["value"]))})
    if any(b["t"]<a["t"] for a,b in zip(events,events[1:])):
        raise ValueError("Events are not time-ordered")
    return events

def analyze(subject,tsv):
    events=parse_events(tsv)
    counts=Counter(x["value"] for x in events)
    core=[x for x in events if x["value"] in TASK]
    prefix=[]
    while core and core[0]["value"]!=TASK[0]:
        prefix.append(core.pop(0)["value"])
    order_errors=timing_errors=0
    for i in range(0,len(core),4):
        quartet=core[i:i+4]
        if tuple(x["value"] for x in quartet)!=TASK:
            order_errors+=1
        else:
            if abs(quartet[2]["t"]-quartet[1]["t"]-5)>0.2 or abs(quartet[3]["t"]-quartet[2]["t"]-5)>0.2:
                timing_errors+=1
    return {"subject_id":subject,
            "n_events":len(events),
            "text_onsets":counts["65282"],
            "fixations":counts["65281"],
            "contemplations":counts["65283"],
            "rating_markers":counts["65284"],
            "complete_quartet_candidates":len(core)//4,
            "leading_task_markers":",".join(prefix),
            "unrecognized_codes":",".join(sorted(set(counts)-set(TASK)-set(REST))),
            "ordering_errors":order_errors,
            "duration_errors":timing_errors,
            "text_markers_minus_210_ratings":counts["65282"]-210,
            "rest_markers":sum(counts[c] for c in REST),
            "ratings_to_events_join_verified":False}

def audit(out, fetcher=fetch):
    reader=csv.DictReader(io.StringIO(fetcher("participants.tsv")),delimiter="\t")
    subjects=[x["participant_id"] for x in reader]
    if len(subjects)!=47 or len(set(subjects))!=47:
        raise ValueError("Unexpected roster count")
    rows=[analyze(s,fetcher(f"{s}/eeg/{s}_task-readpoetry_events.tsv")) for s in subjects]
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    with (out/"per_subject_event_counts.csv").open("w",newline="") as fd:
        w=csv.DictWriter(fd,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    freq=lambda field:dict(sorted(Counter(str(row[field]) for row in rows).items()))
    result={
      "status":"PUBLIC EVENT METADATA ONLY; no EEG signals or human ratings analyzed",
      "source_commit":SOURCE_COMMIT,
      "source_dataset_doi":"10.18112/openneuro.ds006648.v1.0.0",
      "participants_audited":len(rows),
      "published_ratings_per_participant":210,
      "text_onset_distribution":freq("text_onsets"),
      "difference_vs_210_distribution":freq("text_markers_minus_210_ratings"),
      "leading_task_markers_distribution":freq("leading_task_markers"),
      "ordering_errors_total":sum(x["ordering_errors"] for x in rows),
      "duration_errors_total":sum(x["duration_errors"] for x in rows),
      "ratings_to_events_join_verified":False,
      "candidate_pre_rating_window":"65282 text onset through before 65284 rating onset",
      "stop_reason":"Event codes lack poem identity; behavioral rows lack time/trial index; extra trials are unidentified."
    }
    (out/"summary.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--out",required=True)
    audit(p.parse_args().out)
