/** Real-browser regression checks. Build _site first; this owns its test server. */
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {createServer} from 'node:http';
import {readFile, stat, mkdir} from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const require = createRequire(import.meta.url);
const {chromium} = require('playwright');
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const site = path.resolve(process.env.STORE_SITE_DIR || path.join(root, '_site'));
const output = process.env.STORE_SCREENSHOTS || path.join(root, 'test-results');
const server = createServer(async (request, response) => {
  try {
    const pathname = decodeURIComponent(new URL(request.url, 'http://local').pathname);
    let file = path.resolve(site, '.' + pathname);
    if (!file.startsWith(site + path.sep) && file !== site) throw Error('Invalid path');
    if ((await stat(file)).isDirectory()) file = path.join(file, 'index.html');
    response.setHeader('Content-Type', {'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.svg':'image/svg+xml','.json':'application/json','.woff2':'font/woff2'}[path.extname(file)] || 'application/octet-stream');
    response.end(await readFile(file));
  } catch {response.writeHead(404);response.end('Not found');}
});
await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
const origin = `http://127.0.0.1:${server.address().port}`;
const browser = await chromium.launch();
try {
  await mkdir(output, {recursive:true});
  const errors = [];
  const config = JSON.parse(await readFile(path.join(root, 'store/config.json'), 'utf8'));
  for (const width of [320,390,768,1440]) {
    const context = await browser.newContext({viewport:{width,height:844},hasTouch:width<500,reducedMotion:'no-preference'});
    const page = await context.newPage();
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(origin);
    await page.evaluate(()=>document.fonts.ready);
    assert.equal(await page.locator('header,footer,dialog,.store-masthead,.entry-number').count(),0);
    assert.deepEqual(await page.locator('a').evaluateAll(nodes=>nodes.map(n=>n.getAttribute('href')).sort()),['/cctv/','/receipt/','/sys/']);
    assert.equal(await page.locator('main').count(),1);
    assert.equal(await page.locator('svg.store-art image,svg.store-art foreignObject,svg.store-art script').count(),0,'Scene uses code-drawn SVG only');
    assert.deepEqual(await page.locator('svg.store-art [href],svg.store-art [src],svg.store-art [xlink\\:href]').evaluateAll(nodes=>nodes.flatMap(node=>
      ['href','src','xlink:href'].map(name=>node.getAttribute(name)).filter(value=>value && !value.startsWith('#')))),[],'SVG contains no external assets');
    assert.equal(await page.locator('.object-toilet,.object-toiletdoor,.object-toiletbasin').count(),3,'Toilet is visible as room fixtures');
    assert.equal(await page.locator('a[href*="toilet"],a[href*="cache"],a[href*="fragment"]').count(),0);
    for (const route of ['sys','cctv']) {
      const coldStock=config.fixtures.find(fixture=>fixture.id==='coldstock').bounds;
      assert.ok(config.entries.find(entry=>entry.id===route).bounds[1]>=coldStock[1]+coldStock[3],`${route} must be behind the cold-room stock area`);
    }
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth <= innerWidth),true,`Horizontal overflow at ${width}`);
    const boxes = await page.locator('[data-store-object]').evaluateAll(nodes=>nodes.map(node=>{
      const r=node.getBoundingClientRect(); return {id:node.dataset.storeObject,small:node.dataset.small==='true',x:r.x,y:r.y,width:r.width,height:r.height};
    }));
    assert.ok(boxes.find(b=>b.id==='door').y<boxes.find(b=>b.id==='receipt').y,'Entrance appears before checkout');
    for (const route of ['sys','cctv']) assert.ok(boxes.find(b=>b.id===route).y>boxes.find(b=>b.id==='drinks').y,`${route} is in the rear staff workplace`);
    for (const box of boxes) {
      const min=box.small?24:44;
      assert.ok(box.width>=min-.01 && box.height>=min-.01,`Undersized target: ${JSON.stringify(box)}`);
      assert.ok(box.x>=0 && box.x+box.width<=width+1,`Target leaves viewport: ${box.id}`);
    }
    for (let a=0;a<boxes.length;a++) for(let b=a+1;b<boxes.length;b++) {
      const x=boxes[a],y=boxes[b];
      assert.ok(x.x+x.width<=y.x+.1 || y.x+y.width<=x.x+.1 || x.y+x.height<=y.y+.1 || y.y+y.height<=x.y+.1,`Overlapping hit targets: ${x.id}, ${y.id}`);
    }
    for (const fixture of config.fixtures) {
      const trigger=page.locator(`[data-store-object="${fixture.id}"]`);
      if (width<500) await trigger.tap(); else await trigger.click();
      const label=page.locator(`#label-${fixture.id}`);
      assert.equal(await label.isVisible(),true,fixture.id);
      assert.equal(await page.locator('.shelf-label:visible').count(),1);
      assert.equal(await trigger.getAttribute('aria-expanded'),'true');
      assert.equal(await label.locator('strong').innerText(),fixture.name);
      assert.equal(await label.locator('span').innerText(),fixture.note);
      assert.equal(await label.locator('button,a,img').count(),0,'Inspection label stays a small two-line note');
      const bounds=await label.boundingBox();
      assert.ok(bounds.width<=112.1 && bounds.height<=60,`Label too large: ${fixture.id} at ${width}: ${JSON.stringify(bounds)}`);
      assert.equal(await label.evaluate(el=>getComputedStyle(el).backgroundColor.match(/[\d.]+/g).slice(0,3).every(channel=>Number(channel)<80)),true,'Label uses the dark store palette');
      assert.ok(bounds.x>=0 && bounds.x+bounds.width<=width+1,`Label clipped: ${fixture.id}`);
      assert.ok(bounds.y>=0 && bounds.y+bounds.height<=844,`Label outside view: ${fixture.id}`);
      await trigger.click();
      assert.equal(await label.isVisible(),false,'Second tap puts label back');
      assert.equal(await trigger.evaluate(el=>document.activeElement===el),true);
    }
    await page.locator('.object-snacks').click();
    await page.mouse.click(2,2);
    assert.equal(await page.locator('.shelf-label:visible').count(),0,'Tap floor closes label');
    await page.locator('.object-snacks').focus();
    await page.keyboard.press('Enter');
    assert.equal(await page.locator('#label-snacks').isVisible(),true);
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('.shelf-label:visible').count(),0);
    for (const route of ['receipt','sys','cctv']) {
      await page.locator(`.entry-${route}`).click();
      await page.waitForURL(`${origin}/${route}/`);
      assert.equal((await page.locator('title').textContent()).includes('57store'),true);
      if (route!=='receipt') {
        const terminal=page.locator('.store-terminal-header');
        assert.equal(await terminal.locator('a[href="/receipt/"]').count(),0);
        assert.equal(await terminal.locator('.store-session-exit a').innerText(),'EXIT');
        const exit=terminal.locator('.store-session-exit a');
        assert.equal(await exit.evaluate(el=>getComputedStyle(el).textDecorationLine),'none');
        assert.equal(await exit.evaluate(el=>getComputedStyle(el).color),'rgb(107, 236, 174)');
        await terminal.getByRole('link',{name:'Exit terminal'}).click();
      } else {
        const structure=await page.locator('.receipt-return').evaluate(el=>{
          const comment=el.parentElement;
          const lines=[...comment.children].filter(node=>node.tagName==='P');
          const ticket=document.querySelector('.has-border-color.has-base-background-color');
          return {
            marker:comment.previousElementSibling?.textContent.trim(),
            opening:lines[0].textContent.trim(),closing:lines.at(-1).textContent.trim(),
            returnIndex:lines.indexOf(el),printerIndex:lines.findIndex(node=>node.textContent.startsWith('receipt printer:')),
            ticketHasReturn:!!ticket?.querySelector('.receipt-return,a[href="/"]'),
            ticketHasGoodNight:ticket?.textContent.includes('GOOD NIGHT.')
          };
        });
        assert.equal(await page.locator('.receipt-return').count(),1);
        assert.equal(structure.marker,'// store.rs');
        assert.equal(structure.opening,'/*');assert.equal(structure.closing,'*/');
        assert.ok(structure.returnIndex>0 && structure.returnIndex<structure.printerIndex,'Counter exit belongs to the opening store.rs comment before printer status');
        assert.equal(structure.ticketHasReturn,false,'Receipt paper has no store navigation below GOOD NIGHT');
        assert.equal(structure.ticketHasGoodNight,true);
        await page.locator('.receipt-return a').click();
      }
      await page.waitForURL(origin+'/');
    }
    // Verify real time changes, not only the presence of animation declarations.
    await page.evaluate(()=>scrollTo(0,0));
    const steam=page.locator('.steam');
    const before=await steam.evaluate(el=>getComputedStyle(el).transform);
    await page.waitForTimeout(440);
    assert.notEqual(await steam.evaluate(el=>getComputedStyle(el).transform),before);
    const animated=await page.locator('.ambient,.hand,.feet').evaluateAll(ns=>new Set(ns.map(n=>getComputedStyle(n).animationName).filter(n=>n!=='none')).size);
    assert.ok(animated>=15,`Only ${animated} distinct animation designs`);
    await page.emulateMedia({reducedMotion:'reduce'});
    await page.locator('.object-snacks').click();
    assert.equal(await page.locator('#fixture-snacks .stock-response').evaluate(el=>getComputedStyle(el).animationName),'none');
    assert.equal(await steam.evaluate(el=>getComputedStyle(el).animationName),'none');
    if(width===390) await page.screenshot({path:path.join(output,'store-label-mobile.png'),fullPage:true});
    await page.keyboard.press('Escape');
    await page.mouse.click(2,2);
    await page.screenshot({path:path.join(output,`store-${width}.png`),fullPage:true});
    if(width===390 || width===1440) await page.screenshot({path:path.join(output,width===390?'store-mobile.png':'store-desktop.png'),fullPage:true});
    // The explicit choice reaches already-open tabs and subsequently opened
    // root links, where the desktop preview can use a separate browsing tab.
    const peer = await context.newPage();
    await peer.emulateMedia({reducedMotion:'reduce'});
    await peer.goto(origin);
    assert.equal(await peer.locator('.steam').evaluate(el=>getComputedStyle(el).animationName),'none');
    await page.goto(origin+'/?motion=on');
    await peer.waitForFunction(()=>document.documentElement.classList.contains('motion-enabled'));
    assert.equal(await steam.evaluate(el=>getComputedStyle(el).animationName),'steam-rise');
    const openingDoor = await page.locator('.door-left').evaluate(el=>getComputedStyle(el).transform);
    const wakingSteam = await steam.evaluate(el=>getComputedStyle(el).transform);
    await page.waitForTimeout(650);
    assert.notEqual(await page.locator('.door-left').evaluate(el=>getComputedStyle(el).transform),openingDoor,'Door visibly moves during the first second');
    assert.notEqual(await steam.evaluate(el=>getComputedStyle(el).transform),wakingSteam);
    const freshTab = await context.newPage();
    await freshTab.emulateMedia({reducedMotion:'reduce'});
    await freshTab.goto(origin);
    assert.equal(await freshTab.locator('.steam').evaluate(el=>getComputedStyle(el).animationName),'steam-rise');
    await freshTab.close();
    await page.reload();
    assert.equal(await steam.evaluate(el=>getComputedStyle(el).animationName),'steam-rise');
    // A page restored with stale pause classes must reconcile visible fixtures.
    await page.evaluate(()=>{
      document.documentElement.classList.add('store-paused');
      document.querySelector('#fixture-coffee').classList.add('is-away');
      dispatchEvent(new Event('pageshow'));
    });
    assert.equal(await steam.evaluate(el=>getComputedStyle(el).animationPlayState),'running');
    await page.goto(origin+'/?motion=off');
    await peer.waitForFunction(()=>!document.documentElement.classList.contains('motion-enabled'));
    assert.equal(await steam.evaluate(el=>getComputedStyle(el).animationName),'none');
    assert.equal(await peer.locator('.steam').evaluate(el=>getComputedStyle(el).animationName),'none');
    await peer.close();
    await context.close();
  }
  // Privacy settings can deny both storage APIs. Explicit motion still works.
  const blockedStorage = await browser.newContext({viewport:{width:390,height:844},reducedMotion:'reduce'});
  await blockedStorage.addInitScript(()=>{
    for (const key of ['localStorage','sessionStorage']) Object.defineProperty(window,key,{
      get(){ throw new DOMException('Storage blocked','SecurityError'); }
    });
  });
  const blockedPage = await blockedStorage.newPage();
  blockedPage.on('pageerror', error => errors.push(error.message));
  await blockedPage.goto(origin+'/?motion=on');
  assert.equal(await blockedPage.locator('.steam').evaluate(el=>getComputedStyle(el).animationName),'steam-rise');
  await blockedPage.goto(origin+'/?motion=off');
  assert.equal(await blockedPage.locator('.steam').evaluate(el=>getComputedStyle(el).animationName),'none');
  await blockedStorage.close();
  const context = await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});
  const page = await context.newPage();await page.goto(origin);
  assert.equal(await page.locator('svg.store-art').isVisible(),true);
  assert.equal(await page.locator('.store-object:visible').count(),0);
  await page.locator('.entry-receipt').click();await page.waitForURL(`${origin}/receipt/`);
  await context.close();
  assert.deepEqual(errors,[]);
  console.log(`Passed: 4 viewport sizes, ${config.fixtures.length} tap labels, routes, focus, motion over time, reduced motion, cross-tab explicit opt-in, restored pages, blocked storage, no-JS.`);
} finally {await browser.close();await new Promise(resolve=>server.close(resolve));}
