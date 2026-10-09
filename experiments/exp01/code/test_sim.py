from playwright.sync_api import sync_playwright
import json,statistics,os,time
fileurl='file:///mnt/data/consciousness_lab/evolution_lab.html'
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1400,'height':900}, device_scale_factor=1)
 page.on('pageerror', lambda err: print('BROWSER JS ERROR:',str(err)))
 page.set_content(open('/mnt/data/consciousness_lab/evolution_lab.html').read(), wait_until='load')
 page.wait_for_function('window.runBatch !== undefined')
 print('INITIAL',page.evaluate('window.getWorldStats()').get('population'))
 start=time.time()
 results=[]
 for mode in ['evolve','random','blind']:
  for seed in [17,42,77,101,202,323,404,567,777,901]:
   rec=page.evaluate('({seed,mode})=>{const x=window.runBatch(seed,mode,1000);return {seed,mode,steps:x.steps,population:x.population,births:x.births,foodCollected:x.foodCollected,hazardHits:x.hazardHits,deaths:x.deaths,meanGenes:x.meanGenes,history:x.history.filter((h,i)=>i%10===0 || i===x.history.length-1)};}',{'seed':seed,'mode':mode})
   results.append(rec)
  subset=[x for x in results if x['mode']==mode]
  print('MODE',mode,'pop_avg',round(statistics.mean(x['population'] for x in subset),2),'pop_med',statistics.median(x['population'] for x in subset),'births_avg',round(statistics.mean(x['births'] for x in subset),2),'food_avg',round(statistics.mean(x['foodCollected'] for x in subset),2),'danger_avg',round(statistics.mean(x['hazardHits'] for x in subset),2))
  for g in range(4):
   vals=[x['meanGenes'][g] for x in subset if x['meanGenes'][g] is not None]
   print('  gene',g,'mean',round(statistics.mean(vals),3) if vals else None)
 print('RUNTIME_SEC',round(time.time()-start,2))
 os.makedirs('/mnt/data/consciousness_lab',exist_ok=True)
 with open('/mnt/data/consciousness_lab/test_results.json','w') as f:json.dump(results,f,indent=2)
 page.screenshot(path='/mnt/data/consciousness_lab/preview.png',full_page=True)
 print('SCREENSHOT_SAVED',os.path.getsize('/mnt/data/consciousness_lab/preview.png'))
 b.close()
