"""Bounded, read-only public OpenNeuro ds001785 REAL EEG signal verification.

Inspects one EEG .set header (<=45MB) and up to 12 short 206-range .fdt
segments (<=600KB each). No trial results or signal bytes stored.
Physical onset remains UNVERIFIED unless independently aligned to actuator.
"""
from __future__ import annotations
import io,json,math,urllib.request
import numpy as np
from scipy.io import loadmat

ROOT="https://s3.amazonaws.com/openneuro.org/ds001785/sub-01/ses-01/eeg/sub-01_ses-01_task-adapt_run-01_eeg"
EVENTS="https://raw.githubusercontent.com/OpenNeuroDatasets/ds001785/53be0167e7068aba693d57923eb4c9c037878159/sub-01/ses-01/eeg/sub-01_ses-01_task-adapt_run-01_events.tsv"
CHANNELS="https://raw.githubusercontent.com/OpenNeuroDatasets/ds001785/53be0167e7068aba693d57923eb4c9c037878159/sub-01/ses-01/eeg/sub-01_ses-01_channels.tsv"

def get_small(url,limit):
    r=urllib.request.Request(url,headers={"User-Agent":"EmergenceLab-St11B-Research/1"})
    with urllib.request.urlopen(r,timeout=75) as f:
        n=f.headers.get("Content-Length")
        if n and int(n)>limit:raise ValueError("Oversized download refused")
        b=f.read(limit+1)
    if len(b)>limit:raise ValueError("Oversized response refused")
    return b

def get_range(url,start,end):
    if start<0 or end<start or end-start+1>600000:raise ValueError("Range limit violated")
    r=urllib.request.Request(url,headers={"Range":f"bytes={start}-{end}","User-Agent":"EmergenceLab-St11B-Research/1"})
    with urllib.request.urlopen(r,timeout=75) as f:
        data=f.read(600001)
        if f.status!=206 or len(data)!=end-start+1:raise ValueError("Server did not honor exact byte range")
    return data

def get_window(time_seconds,seconds,rate,channels):
    first_sample=round(time_seconds*rate)
    count=round(seconds*rate)
    if first_sample<0 or count<=0:raise ValueError("Invalid time window")
    b=get_range(ROOT+".fdt",first_sample*channels*4,(first_sample+count)*channels*4-1)
    return np.frombuffer(b,dtype="<f4").reshape(count,channels).T.copy()

def power_ratio(x,rate,freq=230):
    z=np.asarray(x,dtype=float)
    n=z.shape[-1]
    if n<80:return np.zeros(z.shape[:-1])
    z=z-np.mean(z,axis=-1,keepdims=True)
    f=np.fft.rfftfreq(n,d=1/rate)
    s=np.abs(np.fft.rfft(z*np.hanning(n),axis=-1))**2
    main=(f>=freq-17)&(f<=freq+17)
    surround=(f>=freq-70)&(f<=freq+70)&~main
    return np.mean(s[...,main],axis=-1)/(np.mean(s[...,surround],axis=-1)+1e-14)

def inspect():
    data=get_small(ROOT+".set",45000000)
    mat=loadmat(io.BytesIO(data),squeeze_me=True,struct_as_record=False)
    if "EEG" not in mat:raise RuntimeError("EEGLAB struct absent")
    eeg=mat["EEG"]
    n,rate,pnts=int(eeg.nbchan),int(eeg.srate),int(eeg.pnts)
    channels=eeg.chanlocs
    if not isinstance(channels,np.ndarray):channels=np.array([channels],dtype=object)
    labels=[str(x.labels).strip() for x in channels.flat]
    print("HEADER:",json.dumps({"n_channels":n,"sampling_hz":rate,"total_samples":pnts,
                                  "set_bytes":len(data),"labels":labels}))
    if n<50 or n>90 or rate not in (512,1024) or len(labels)!=n:raise RuntimeError("Unexpected signal shape")
    if not isinstance(eeg.data,str):raise RuntimeError("Signal stored in .set; fdt assumptions not valid")
    if n*pnts*4>1600000000:raise RuntimeError("Unexpected signal size")
    import csv
    channel_rows=list(csv.DictReader(io.StringIO(get_small(CHANNELS,16000).decode()),delimiter="\t"))
    if [q["name"] for q in channel_rows]!=labels:
        raise RuntimeError("EEGLAB and BIDS EEG channel order mismatch")
    idx=[i for i,q in enumerate(channel_rows) if q["type"]=="AUDIO"]
    print("AUDIO CHANNEL INDEX FROM PUBLISHED BIDS TYPES:",idx)
    if len(idx)!=1:raise RuntimeError("Exactly one independent audio channel must be verified")
    event_rows=list(csv.DictReader(io.StringIO(get_small(EVENTS,200000).decode()),delimiter="\t"))
    trials=[]
    starts=[i for i,r in enumerate(event_rows) if r["trial_type"]=="stim-adapt"]
    for k,i in enumerate(starts):
        end=starts[k+1] if k+1<len(starts) else len(event_rows)
        block=event_rows[i:end]
        outcome=[q["trial_type"] for q in block if q["trial_type"] in ("hit","miss","cr","fa")]
        if len(outcome)!=1:continue
        try: a,d=float(event_rows[i]["onset"]),float(event_rows[i]["stimon"])
        except ValueError: continue
        if math.isfinite(a) and math.isfinite(d) and a>15 and .3<d<1.0:
            trials.append((a+d,"delivered" if outcome[0] in ("hit","miss") else "catch"))
    grouped={}
    for group in ("delivered","catch"):
        sample=[t for t,g in trials if g==group][:12]
        if len(sample)<10:raise RuntimeError(f"Need 10+ trial timing windows of type {group}")
        rms_ratios=[];spectra=[];window_summaries=[]
        for t in sample:
            z=get_window(t-.25,.65,rate,n)
            if not np.isfinite(z).all():continue
            before=z[:,:round(.20*rate)]
            after=z[:,round(.27*rate):round(.44*rate)]
            # Remove substantial DC offsets and evaluate variance of actual signal.
            pre_mean=np.mean(before,axis=1,keepdims=True)
            b=np.sqrt(np.mean((before-pre_mean)**2,axis=1))+1e-12
            a=np.sqrt(np.mean((after-pre_mean)**2,axis=1))+1e-12
            rms_ratios.append(float(np.max((a/b)[idx])))
            spectra.append(float(np.max(power_ratio(after[idx],rate))))
            # Normalize temporal waveform by pre-stimulus fluctuation, NOT raw DC.
            signal=z[idx[0],:]-pre_mean[idx[0],0]
            base=np.sqrt(np.mean(signal[:round(.20*rate)]**2))+1e-12
            chunk=round(.025*rate)
            wins=np.array([np.mean(np.abs(signal[j:j+chunk]))/base
                for j in range(0,len(signal)-chunk,chunk)])
            window_summaries.append(wins)
        grouped[group]={"segments":len(rms_ratios),
                "median_rms_post_pre":float(np.median(rms_ratios)),
                "median_230hz_relative_power":float(np.median(spectra)),
                "coarse_median_normalized_abs_waveform":[round(float(q),3)
                    for q in np.median(np.stack(window_summaries),axis=0)]}
    result={"n_signal_channels":n,"audio_channel_labels":[labels[i] for i in idx],
            "metadata_stimulus_groups":grouped,"physical_onset_verified":False,
            "status":"Independent BIDS AUDIO channel cross-check; pulse timestamp still requires offset calibration"}
    print("NONIDENTIFYING AUDIO-CHANNEL QC:",json.dumps(result,indent=2))

if __name__=="__main__":inspect()
