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
  for (const width of [320,390,768,1440]) {
    const context = await browser.newContext({viewport:{width,height:844},hasTouch:width<500});
    const page = await context.newPage();
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(origin);
    assert.equal(await page.locator('header,footer,.store-masthead,.entry-number').count(),0);
    assert.deepEqual(await page.locator('a').evaluateAll(nodes=>nodes.map(n=>n.getAttribute('href')).sort()),['/cctv/','/receipt/','/sys/']);
    assert.equal(await page.locator('main').count(),1);
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth <= innerWidth),true,`Horizontal overflow at ${width}`);
    const boxes = await page.locator('[data-store-object]').evaluateAll(nodes=>nodes.map(node=>{
      const r=node.getBoundingClientRect(); return {id:node.dataset.storeObject,x:r.x,y:r.y,width:r.width,height:r.height};
    }));
    for (const box of boxes) {
      assert.ok(box.width>=44 && box.height>=44,`Undersized target: ${JSON.stringify(box)}`);
      assert.ok(box.x>=0 && box.x+box.width<=width+1,`Target leaves viewport: ${box.id}`);
    }
    for (let a=0;a<boxes.length;a++) for(let b=a+1;b<boxes.length;b++) {
      const x=boxes[a],y=boxes[b];
      assert.ok(x.x+x.width<=y.x || y.x+y.width<=x.x || x.y+x.height<=y.y || y.y+y.height<=x.y,`Overlapping hit targets: ${x.id}, ${y.id}`);
    }
    for (const fixture of ['snacks','daily','fresh','drinks','coffee','arrival']) {
      const trigger=page.locator(`[data-store-object="${fixture}"]`);
      if (width<500) await trigger.tap(); else await trigger.click();
      const dialog=page.locator(`#label-${fixture}`);
      assert.equal(await dialog.evaluate(el=>el.open),true);
      assert.ok(await dialog.locator('li').count()>=3);
      assert.equal(await page.locator('dialog[open]').count(),1);
      // No hover is necessary. Each label has a large explicit closing control.
      await dialog.getByRole('button').click();
      assert.equal(await dialog.evaluate(el=>el.open),false);
      assert.equal(await trigger.evaluate(el=>document.activeElement===el),true);
    }
    await page.locator('.object-snacks').click();
    await page.mouse.click(4,4);
    assert.equal(await page.locator('dialog[open]').count(),0,'Tap outside puts the label back');
    await page.locator('.object-snacks').focus();
    await page.keyboard.press('Enter');
    assert.equal(await page.locator('#label-snacks').evaluate(el=>el.open),true);
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('dialog[open]').count(),0);
    for (const route of ['receipt','sys','cctv']) {
      await page.locator(`.entry-${route}`).click();
      await page.waitForURL(`${origin}/${route}/`);
      assert.equal((await page.locator('title').textContent()).includes('57store'),true);
      if (route!=='receipt') {
        const terminal=page.locator('.store-terminal-header');
        assert.equal(await terminal.locator('a[href="/receipt/"]').count(),0);
        assert.equal(await terminal.locator('.store-session-exit a').innerText(),'EXIT');
        assert.equal(await terminal.locator('.store-session-exit a').evaluate(el=>getComputedStyle(el).textDecorationLine),'none');
        await terminal.getByRole('link',{name:'Exit terminal'}).click();
      } else await page.locator('.receipt-return a').click();
      await page.waitForURL(origin+'/');
    }
    await page.emulateMedia({reducedMotion:'reduce'});
    await page.locator('.object-snacks').click();
    assert.equal(await page.locator('#fixture-snacks .stock-response').evaluate(el=>getComputedStyle(el).animationName),'none');
    assert.equal(await page.locator('.shopper').evaluate(el=>getComputedStyle(el).animationName),'none');
    if(width===390) await page.screenshot({path:path.join(output,'store-label-mobile.png'),fullPage:true});
    await page.keyboard.press('Escape');
    // Remove keyboard focus only for representative artwork screenshots.
    await page.mouse.click(4,4);
    if(width===390 || width===1440) await page.screenshot({path:path.join(output,width===390?'store-mobile.png':'store-desktop.png'),fullPage:true});
    await context.close();
  }
  // Scene/navigation remain available when JavaScript is unavailable.
  const context = await browser.newContext({javaScriptEnabled:false,viewport:{width:390,height:844}});
  const page = await context.newPage();await page.goto(origin);
  assert.equal(await page.locator('svg.store-art').isVisible(),true);
  assert.equal(await page.locator('.store-object:visible').count(),0);
  await page.locator('.entry-receipt').click();await page.waitForURL(`${origin}/receipt/`);
  await context.close();
  assert.deepEqual(errors,[]);
  console.log('Passed: 4 viewport sizes, 6 touch labels, all routes, dismissal/focus, no-JS and reduced motion.');
} finally {await browser.close();await new Promise(resolve=>server.close(resolve));}
