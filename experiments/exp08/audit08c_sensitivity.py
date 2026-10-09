"""Development-only training initialization sensitivity. No confirmatory seeds or tuning."""
import argparse,csv,json
from pathlib import Path
import numpy as np
from audit08c_learning import generate_data,fit,accuracy,rollout_scores

TRAINING_SEEDS=(80808, 80908, 81008)
MODELS=('memoryless','history','recurrent')

def main():
    a=argparse.ArgumentParser()
    a.add_argument('--out',default='development_identifiability_08c')
    a.add_argument('--epochs',type=int,default=36)
    args=a.parse_args()
    X,Y,W=generate_data(192,'train')
    V,VY,VW=generate_data(48,'validation')
    B,BY,BW=generate_data(72,'shift')
    rows=[]
    for model_idx,name in enumerate(MODELS):
        for start in TRAINING_SEEDS:
            p,loss=fit(name,X,Y,W,start+model_idx*100,epochs=args.epochs)
            val=accuracy(name,p,V,VY,VW)['accuracy']
            transfer=accuracy(name,p,B,BY,BW)['accuracy']
            policy=rollout_scores(name,p,n=24)['shift+dropout']
            rows.append({'model':name,'training_seed':start,'epochs':args.epochs,
                         'validation_accuracy':val,'shift_accuracy':transfer,
                         'shift_policy_food':policy,'final_loss':loss[-1]})
            print(name,start,'validation',round(val,3),'shift',round(transfer,3),'food',round(policy,3),flush=True)
    dest=Path(args.out);dest.mkdir(exist_ok=True,parents=True)
    with (dest/'initialization_sensitivity.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    summary={name:{k:{'mean':float(np.mean([r[k] for r in rows if r['model']==name])),
                        'range':[float(min(r[k] for r in rows if r['model']==name)),float(max(r[k] for r in rows if r['model']==name))]}
            for k in ('validation_accuracy','shift_accuracy','shift_policy_food')} for name in MODELS}
    (dest/'initialization_sensitivity.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
