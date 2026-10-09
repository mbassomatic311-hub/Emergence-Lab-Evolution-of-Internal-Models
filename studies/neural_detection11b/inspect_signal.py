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
    starts=[]
    import csv
    for item in csv.DictReader(io.StringIO(get_small(EVENTS,200000).decode()),delimiter="\t"):
        if item["trial_type"]=="stim-adapt":
            try:a,d=float(item["onset"]),float(item["stimon"])
            except ValueError:continue
            if math.isfinite(a) and math.isfinite(d) and a>15 and .3<d<1.0:
                starts.append(a+d)
            if len(starts)>=12:break
    if len(starts)<8:raise RuntimeError("Not enough candidate events")
    idx=[i for i,x in enumerate(labels) if any(k in x.lower() for k in ("audio","stim","aux","trig"))]
    print("CANDIDATE ACTUATOR CHANNELS:",idx)
    if not idx:
        print("STOP: no identifiable actuator channel: physical onset not verified")
        return
    ratios=[];spectra=[]
    for t in starts:
        z=get_window(t-.25,.65,rate,n)
        if not np.isfinite(z).all():continue
        before=z[:,:round(.20*rate)]
        after=z[:,round(.27*rate):round(.44*rate)]
        b=np.sqrt(np.mean(before**2,axis=1))+1e-12
        a=np.sqrt(np.mean(after**2,axis=1))+1e-12
        ratios.append(float(np.max((a/b)[idx])))
        spectra.append(float(np.max(power_ratio(after[idx],rate))))
    print("NONIDENTIFYING SIGNAL QUALITY METRICS:",
          json.dumps({"segments_read":len(ratios),
                      "aux_median_rms_post_pre":float(np.median(ratios)),
                      "aux_median_230hz_relative_power":float(np.median(spectra)),
                      "physical_onset_verified":False,
                      "status":"Signal access and byte-order audit only; no EEG predictive model"}))

if __name__=="__main__":inspect()
