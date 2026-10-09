from playwright.sync_api import sync_playwright
from pathlib import Path
P=Path('/mnt/data/consciousness_lab/experiment_04_perception.html')
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1365,'height':1000},accept_downloads=True)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 page.set_content(P.read_text(), wait_until="load")
 page.wait_for_function('window.exp04Stats !== undefined')
 print('INITIAL',page.evaluate('exp04Stats()'))
 page.locator('#step20').click()
 print('GEN20',page.evaluate('exp04Stats()'))
 page.locator('#stepall').click()
 print('GEN160',page.evaluate('exp04Stats()'))
 assert page.evaluate('exp04Stats().generation') == 160
 page.screenshot(path='/mnt/data/consciousness_lab/experiment_04_preview.png',full_page=True)
 with page.expect_download() as download_info: page.locator('#export').click()
 d=download_info.value
 print('CSV_DOWNLOAD',d.suggested_filename)
 assert d.suggested_filename.endswith('.csv')
 page.locator('#iconbtn').click();print('VIEW',page.evaluate('exp04Stats().view'))
 assert page.evaluate('exp04Stats().view') == 'icons'
 page.locator('#pairbtn').click();print('PAIR_CLICK',page.locator('#pairbtn').inner_text())
 page.locator('#scenario').select_option('variable');print('VARIABLE_RESET',page.evaluate('exp04Stats()'))
 assert page.evaluate('exp04Stats().generation') == 0
 page.locator('#stepall').click();print('VARIABLE_FINISH',page.evaluate('exp04Stats().shares'))
 page.locator('#cost').fill('0.22');page.locator('#cost').dispatch_event('change');print('COST_CHANGE',page.evaluate('exp04Stats().fullCost'))
 assert page.evaluate('exp04Stats().fullCost') == .22
 page.locator('#reset').click();print('RESET',page.evaluate('exp04Stats().generation'))
 page.locator('#scenario').select_option('shock');page.locator('#cost').fill('0.1');page.locator('#cost').dispatch_event('change');page.locator('#stepall').click();first=page.evaluate('exp04Stats().shares')
 page.locator('#reset').click();page.locator('#stepall').click();second=page.evaluate('exp04Stats().shares')
 print('DETERMINISM',first==second)
 assert first==second
 mobile=b.new_page(viewport={'width':390,'height':844},device_scale_factor=1)
 mobile.on('pageerror',lambda e:errors.append('mobile '+str(e)))
 mobile.set_content(P.read_text(), wait_until="load");mobile.wait_for_function('window.exp04Stats !== undefined')
 mobile.locator('#stepall').click()
 print('MOBILE_OVERFLOW',mobile.evaluate('document.documentElement.scrollWidth - window.innerWidth'))
 mobile.screenshot(path='/mnt/data/consciousness_lab/experiment_04_mobile.png',full_page=True)
 assert mobile.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
 print('JS_ERRORS',errors)
 assert not errors
 b.close()
