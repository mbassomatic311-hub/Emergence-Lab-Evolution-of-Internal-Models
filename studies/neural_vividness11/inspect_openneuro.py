"""Study 11 public data SCHEMA ONLY check, no EEG or ratings archived.

Optional network action. Fetches at most one small publicly released ratings CSV;
never outputs its individual ratings. Does not verify EEG-event alignment.
"""
from __future__ import annotations
import io,json,urllib.request
from pathlib import Path
import pandas as pd

MANIFEST='https://data.nemar.org/on006648/v1.0.0/manifest.json'
TARGET='derivatives/Behavioural_Ratings/P101.csv'

def request_limited(url:str,limit:int=500_000):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EmergenceLab-Study11-metadata-preflight/1.0'}),timeout=35) as stream:
        result=stream.read(limit+1)
    if len(result)>limit:raise ValueError('Refusing unexpectedly large payload')
    return result

def locate(rows):
    if isinstance(rows,dict):
        rows=rows.get('files',rows.get('entries',rows.get('manifest',[])))
    if not isinstance(rows,list):raise ValueError('Unsupported manifest structure')
    matched=[]
    for row in rows:
        if not isinstance(row,dict):continue
        path=str(row.get('path',row.get('name',row.get('relative_path','')))).lstrip('/')
        if path.endswith(TARGET):matched.append(row)
    if len(matched)!=1:raise ValueError(f'Expected exactly one matching public ratings file; found {len(matched)}')
    row=matched[0]
    url=row.get('bytes_url',row.get('url',row.get('download_url')))
    if not isinstance(url,str) or not url.startswith('https://'):
        raise ValueError('No HTTPS bytes URL for real ratings file in manifest')
    return url

def inspect(out='schema_check.json'):
    manifest=json.loads(request_limited(MANIFEST,5_000_000))
    url=locate(manifest)
    blob=request_limited(url)
    if blob.startswith(b'../../.git/annex/'):
        raise ValueError('Received git-annex pointer, not real behavioral bytes')
    table=pd.read_csv(io.BytesIO(blob))
    if table.empty or len(table.columns)<2:raise ValueError('Unexpected empty or invalid behavioral table')
    report={
      'dataset':'OpenNeuro ds006648 v1.0.0; NEMAR on006648 v1.0.0',
      'status':'REAL PUBLIC BEHAVIORAL SCHEMA INSPECTED; no EEG data, no event/ratings join',
      'source_file':TARGET,
      'source_bytes':len(blob),
      'rows':len(table),
      'columns':[str(c) for c in table.columns],
      'dtypes':{str(c):str(t) for c,t in table.dtypes.items()},
      'ratings_stored':False,
      'eeg_fetched':False,
      'events_matched':False,
      'preflight_only':True,
    }
    Path(out).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return report

if __name__=='__main__':inspect()