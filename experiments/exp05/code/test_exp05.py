from playwright.sync_api import sync_playwright
from pathlib import Path
p=Path('/mnt/data/consciousness_lab/experiment_05_beyond_the_interface.html')
with sync_playwright() as run:
 b=run.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 errs=[]
 tab=b.new_page(viewport={'width':1320,'height':950},accept_downloads=True)
 tab.on('pageerror',lambda e:errs.append(str(e)))
 tab.set_content(p.read_text(),wait_until="load")
 print('INITIAL',tab.evaluate('exp05Stats()'))
 tab.locator('#step20').click()
 print('STEP20',tab.evaluate('exp05Stats()'))
 tab.locator('#runall').click()
 print('FINAL',tab.evaluate('exp05Stats()'))
 assert tab.evaluate('exp05Stats().generation')==240
 tab.screenshot(path='/mnt/data/consciousness_lab/experiment_05_preview.png',full_page=True)
 with tab.expect_download() as download:
  tab.locator('#export').click()
 print('EXPORT',download.value.suggested_filename)
 tab.locator('#revealA').click()
 assert tab.locator('#worldA').evaluate('(el)=>el.classList.contains("revealed")')
 tab.locator('#probeB').click()
 print('PROBE_TEXT',tab.locator('#readB').inner_text())
 tab.locator('#reset').click();tab.locator('#runall').click();a=tab.evaluate('exp05Stats()')
 tab.locator('#reset').click();tab.locator('#runall').click();bb=tab.evaluate('exp05Stats()')
 assert a==bb
 print('DETERMINISTIC',True)
 tab.locator('#condition').select_option('shuffled');tab.locator('#runall').click()
 print('SHUFFLED',tab.evaluate('exp05Stats()'))
 tab.locator('#cost').evaluate("e=>{e.value='1.30';e.dispatchEvent(new Event('change',{bubbles:true}))}");assert tab.evaluate('exp05Stats().generation')==0
 print('COST_CHANGED',tab.evaluate('exp05Stats().cost'))
 mobile=b.new_page(viewport={'width':390,'height':844},device_scale_factor=1)
 mobile.on('pageerror',lambda e:errs.append('mobile: '+str(e)))
 mobile.set_content(p.read_text(),wait_until="load");mobile.locator('#runall').click()
 overflow=mobile.evaluate('document.documentElement.scrollWidth-innerWidth')
 print('MOBILE_OVERFLOW',overflow)
 mobile.screenshot(path='/mnt/data/consciousness_lab/experiment_05_mobile.png',full_page=True)
 assert overflow<=0
 print('JS_ERRORS',errs)
 assert not errs
 b.close()
