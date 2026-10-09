from playwright.sync_api import sync_playwright
import json,statistics,time
P='/mnt/data/consciousness_lab/experiment_02_prediction.html'
seeds=[11,17,42,73,101,177,202,323,404,567,777,901,1009,2027,3049,4101,5321,6607,7759,8009]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 pg=b.new_page(viewport={'width':1400,'height':1000})
 errors=[]
 pg.on('pageerror',lambda e: errors.append(str(e)))
 pg.set_content(open(P).read(), wait_until='load')
 pg.wait_for_function('window.runBatch !== undefined')
 print('INITIAL',pg.evaluate('getStats().generations'))
 start=time.time();records=[]
 for mode in ['predict','blocked','random','nonheritable']:
  for seed in seeds:
   s=pg.evaluate('({seed,mode})=>{let s=runBatch(seed,mode,300);return {seed,mode,accuracy:s.accuracy,avgLast30:s.avgLast30,meanRetention:s.meanRetention,meanDecoder:s.meanDecoder,earlyMean:s.records.slice(1,31).reduce((a,v)=>a+v.accuracy,0)/30,lateMean:s.records.slice(-30).reduce((a,v)=>a+v.accuracy,0)/30,series:s.records.filter((x,i)=>i%15===0)};}',{'seed':seed,'mode':mode})
   records.append(s)
  rr=[v for v in records if v['mode']==mode]
  print('MODE',mode,'late accuracy mean',round(statistics.mean(v['lateMean'] for v in rr),4),'SD',round(statistics.stdev(v['lateMean'] for v in rr),4),'early',round(statistics.mean(v['earlyMean'] for v in rr),4),'mem',round(statistics.mean(v['meanRetention'] for v in rr),3),'decoder',round(statistics.mean(v['meanDecoder'] for v in rr),3))
 print('RUNTIME',round(time.time()-start,2),'s')
 print('BROWSER_ERRORS', errors)
 pg.locator('#plus100').click();print('BUTTON',pg.evaluate('getStats().generations'))
 pg.locator('#mode').select_option('blocked');print('SWITCH',pg.evaluate('getStats().mode'), pg.evaluate('getStats().generations'))
 pg.locator('#plus10').click();print('ADVANCED',pg.evaluate('getStats().generations'))
 pg.locator('#reset').click();print('RESET',pg.evaluate('getStats().generations'))
 pg.locator('#mode').select_option('predict');pg.locator('#plus100').click();pg.screenshot(path='/mnt/data/consciousness_lab/experiment_02_preview.png',full_page=True)
 with open('/mnt/data/consciousness_lab/experiment_02_results.json','w') as f:json.dump(records,f,indent=2)
 b.close()
