"""Exploratory sub-01 actuator timing preflight; NOT neural or consciousness analysis.
Bounded read-only public EEG AUDIO data; outputs aggregate QC only.
"""
from __future__ import annotations
import csv,io,json,math
import numpy as np
from scipy.signal import butter,sosfiltfilt
from inspect_signal import CHANNELS, EVENTS, get_small, get_window

FS=1024
N_PER_GROUP=6

def trials_from_events(text):
    rows=list(csv.DictReader(io.StringIO(text),delimiter="\t"))
    starts=[i for i,r in enumerate(rows) if r.get("trial_type")=="stim-adapt"]
    trials=[]
    for k,i in enumerate(starts):
        end=starts[k+1] if k+1<len(starts) else len(rows)
        block=rows[i:end]
        outcomes=[r for r in block if r.get("trial_type") in ("hit","miss","cr","fa")]
        if len(outcomes)!=1:continue
        st=block[0]
        try:
            on,d,sample,response=(float(st["onset"]),float(st["stimon"]),
                                  int(st["event_sample"]),float(outcomes[0]["onset"]))
        except (ValueError,KeyError,TypeError):continue
        if (not all(map(math.isfinite,(on,d,response))) or on<=15
            or not 0<=d<=2.5 or abs(on*FS-sample)>1.05):continue
        trials.append(dict(nominal=on+d,response=response,
                           delivered=outcomes[0]["trial_type"] in ("hit","miss"),onset=on))
    return trials

def fixed_calibration_validation(trials,per_group=N_PER_GROUP):
    cal,val=[],[]
    for delivered in (True,False):
        x=[r for r in trials if r["delivered"]==delivered]
        if len(x)<4*per_group:raise ValueError("Too few trials for disjoint early/late groups")
        cal.extend(x[:per_group]);val.extend(x[-per_group:])
    return sorted(cal,key=lambda r:r["onset"]), sorted(val,key=lambda r:r["onset"])

def bandpower_curve(audio,rate=FS,start=-.25):
    audio=np.asarray(audio,dtype=np.float64)
    if not np.all(np.isfinite(audio)) or len(audio)<rate:
        raise ValueError("Nonfinite or short recorded AUDIO segment")
    filt=sosfiltfilt(butter(4,(210,250),btype="bandpass",fs=rate,output="sos"),audio)
    w=round(.08*rate)
    e=np.convolve(filt*filt,np.ones(w)/w,mode="valid")
    t=start+(np.arange(len(e))+(w-1)/2)/rate
    return t,np.sqrt(np.maximum(e,0))

def measure_offsets(curve,offsets):
    t,p=curve
    return np.interp(offsets+.04,t,p)/(np.median(p)+1e-12)

def choose_offset(calibration,offsets):
    a=np.stack([r["score"] for r in calibration if r["delivered"]])
    b=np.stack([r["score"] for r in calibration if not r["delivered"]])
    diff=np.median(a,axis=0)-np.median(b,axis=0)
    return int(np.argmax(diff)),float(np.max(diff))

def summarize(calibration,validation,offsets):
    idx,contrast=choose_offset(calibration,offsets)
    chosen=float(offsets[idx])
    a=np.array([r["score"][idx] for r in validation if r["delivered"]])
    b=np.array([r["score"][idx] for r in validation if not r["delivered"]])
    delivered=[r for r in validation if r["delivered"]]
    sep=float(np.median(a)/(np.median(b)+1e-12))
    passed=int(sum(a>max(3.,float(np.quantile(b,.90)))))
    safely_before=sum(r["nominal"]+chosen+.1<r["response"] for r in delivered)
    return {
        "status":"EXPLORATORY holdout pulse timing preflight; no EEG perception analysis",
        "anchor":"stim-adapt onset + stimon, searched from -0.1 to +3.05 sec",
        "calibration_delivered":sum(r["delivered"] for r in calibration),
        "calibration_catch":sum(not r["delivered"] for r in calibration),
        "validation_delivered":len(a),"validation_catch":len(b),
        "selected_offset_seconds_after_nominal":round(chosen,3),
        "calibration_median_energy_contrast":round(contrast,3),
        "validation_median_normalized_energy_delivered":round(float(np.median(a)),3),
        "validation_median_normalized_energy_catch":round(float(np.median(b)),3),
        "validation_delivered_to_catch_ratio":round(sep,3),
        "validation_delivered_above_catch_p90_and_3x_floor":f"{passed}/{len(a)}",
        "validation_pulse_precedes_report":f"{safely_before}/{len(a)}",
        "physical_onset_verified":bool(sep>=4 and passed>=5 and safely_before>=5),
        "limit":"Passing establishes only a sub-01 trigger candidate, not general EEG alignment, cognition or consciousness"
    }

def read_audio(nominal,channel,nchan):
    # Each 1.8 s range is 523kB at 1024 Hz x 71 channels x float32, below the 600kB limit.
    z1=get_window(nominal-.25,1.8,FS,nchan)[channel]
    z2=get_window(nominal+1.55,1.8,FS,nchan)[channel]
    return np.concatenate((z1,z2))

def main():
    channels=list(csv.DictReader(io.StringIO(get_small(CHANNELS,16000).decode()),delimiter="\t"))
    idx=[i for i,r in enumerate(channels) if r.get("type")=="AUDIO" and r.get("name")=="BIP3"]
    if len(idx)!=1 or not 60<=len(channels)<=85:
        raise RuntimeError("Audio channel not consistent with published BIDS metadata")
    trials=trials_from_events(get_small(EVENTS,200000).decode())
    cal,val=fixed_calibration_validation(trials)
    offsets=np.round(np.arange(-.1,3.0501,.025),4)
    processed=[]
    for group in (cal,val):
        out=[]
        for r in group:
            audio=read_audio(r["nominal"],idx[0],len(channels))
            out.append({**r,"score":measure_offsets(bandpower_curve(audio),offsets)})
        processed.append(out)
    result=summarize(*processed,offsets)
    result.update(source="OpenNeuro ds001785 v1.1.1; upstream commit 53be0167",
                  participant="sub-01",
                  number_of_bounded_range_reads=2*(len(cal)+len(val)),
                  raw_signal_or_trial_results_saved=False)
    print(json.dumps(result,indent=2))
    if not result["physical_onset_verified"]:
        print("STOP GATE BLOCKED: no justified stimulus-locked EEG model.")

if __name__=="__main__":main()
