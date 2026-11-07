/* Actual-browser checks. Run against a freshly built output:
 * STORE_PREVIEW_DIR=/tmp/57store-new-preview node --test tests/test_store.mjs
 * Requires Playwright and its Chromium browser; no network service is used.
 */
import assert from 'node:assert/strict';
import {readFile, stat} from 'node:fs/promises';
import {createServer} from 'node:http';
import {createRequire} from 'node:module';
import path from 'node:path';
import test from 'node:test';

const preview=process.env.STORE_PREVIEW_DIR;

test('Store browser QA',{skip:!preview,timeout:120000},async t=>{
  const {chromium}=createRequire(import.meta.url)('playwright');
  const root=path.resolve(preview);
  const types={'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.json':'application/json','.woff2':'font/woff2','.svg':'image/svg+xml','.png':'image/png','.webp':'image/webp'};
  const server=createServer(async(request,response)=>{
    try {
      const pathname=decodeURIComponent(new URL(request.url,'http://localhost').pathname);
      let file=path.resolve(root,'.'+pathname);
      if(file!==root&&!file.startsWith(root+path.sep))throw Error('Path leaves output');
      if((await stat(file)).isDirectory())file=path.join(file,'index.html');
      response.writeHead(200,{'Content-Type':types[path.extname(file)]||'application/octet-stream'});
      response.end(await readFile(file));
    } catch {response.writeHead(404);response.end('Not found');}
  });
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  t.after(()=>new Promise(resolve=>server.close(resolve)));
  const origin='http://127.0.0.1:'+server.address().port;
  const browser=await chromium.launch({headless:true});
  t.after(()=>browser.close());
  const open=async(options={})=>{
    const context=await browser.newContext(options),page=await context.newPage(),errors=[];
    page.on('pageerror',error=>errors.push(error.message));
    await page.goto(origin+'/',{waitUntil:'networkidle'});
    await page.waitForFunction(()=>[...document.querySelectorAll('button.room-control')].every(button=>!button.hidden));
    return {context,page,errors};
  };

  for(const [width,height] of [[320,568],[375,667],[768,1024],[1440,900]]){
    await t.test(`Notes and keyboard at ${width}px`,async t=>{
      const {context,page,errors}=await open({viewport:{width,height},reducedMotion:'reduce'});
      t.after(()=>context.close());
      assert.equal(await page.locator('h1').innerText(),'57STORE ゴナナストア');
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true,'No horizontal overflow');
      const notes=page.locator('button.room-control');
      assert.ok(await notes.count()>20,'The physical room retains inspectable objects');
      for(const button of await notes.all()){
        const title=await button.getAttribute('data-note-title');
        await button.scrollIntoViewIfNeeded();
        // A foreground object may cover part of a projected target. Require
        // an actual exposed tap point, never a forced/programmatic click.
        const point=await button.evaluate(control=>{
          const box=control.getBoundingClientRect(),points=[];
          for(const y of [.5,.3,.7,.1,.9])for(const x of [.5,.3,.7,.1,.9])points.push({x:x*box.width,y:y*box.height});
          return points.find(point=>document.elementFromPoint(box.left+point.x,box.top+point.y)?.closest('.room-control')===control)||null;
        });
        assert.ok(point,`Object has an exposed pointer target: ${title}`);
        await button.click({position:point,timeout:3000});
        await page.waitForFunction(()=>!document.getElementById('room-note').hidden);
        assert.equal(await page.locator('#room-note strong').innerText(),title);
        assert.equal(await page.locator('button[aria-expanded=true]').count(),1);
        const box=await page.locator('#room-note').boundingBox();
        assert.ok(box.x>=0&&box.y>=0&&box.x+box.width<=width+1&&box.y+box.height<=height+1,`Visible note: ${title}`);
      }
      await page.waitForTimeout(360);
      assert.equal(await page.locator('.world-object.used').count(),0,'Rapid successive inspections clean up prior feedback');
      await page.keyboard.press('Escape');
      assert.equal(await page.locator('#room-note').isVisible(),false);
      assert.equal(await page.locator('button[aria-expanded=true]').count(),0);
      const first=notes.first();
      await first.focus();await page.keyboard.press('Enter');
      assert.equal(await page.locator('#room-note').isVisible(),true,'Keyboard opens the same note');
      assert.ok(await page.locator('.world-object.focused').count()>0,'Keyboard focus highlights the corresponding object');
      await page.mouse.click(1,1);
      assert.equal(await page.locator('#room-note').isVisible(),false,'Outside tap dismisses the note');
      assert.deepEqual(errors,[]);
    });
  }

  await t.test('Glass fronts and upper/lower shelves respond across the full fixture',async t=>{
    const {context,page}=await open({viewport:{width:375,height:667},reducedMotion:'reduce'});
    t.after(()=>context.close());
    // Native artwork points on the visible hot-case glass and cold-case goods.
    // These taps used to miss a target restricted to the fixture's middle.
    for(const [x,y,title] of [[110,195,'热食柜'],[555,470,'乳品冷柜'],[575,630,'乳品冷柜'],[590,1140,'便当冷柜']]){
      let box=await page.locator('.room').boundingBox();const scale=box.width/672;
      await page.evaluate(y=>scrollTo(0,y-200),y*scale);
      box=await page.locator('.room').boundingBox();
      await page.mouse.click(box.x+x*scale,box.y+y*scale);
      assert.equal(await page.locator('#room-note strong').innerText(),title);
      assert.equal(await page.locator('#room-note').isVisible(),true);
      await page.keyboard.press('Escape');
    }
  });

  await t.test('The three physical destinations navigate normally',async t=>{
    const {context,page,errors}=await open({viewport:{width:375,height:667}});
    t.after(()=>context.close());
    assert.deepEqual(await page.locator('a.room-control').evaluateAll(anchors=>anchors.map(a=>a.getAttribute('href')).sort()),['/cctv/','/receipt/','/sys/']);
    for(const destination of ['/receipt/','/sys/','/cctv/']){
      await page.goto(origin+'/',{waitUntil:'networkidle'});
      await Promise.all([page.waitForURL(origin+destination),page.locator(`a.room-control[href="${destination}"]`).click()]);
      assert.ok(await page.locator('body').innerText());
    }
    assert.deepEqual(errors,[]);
  });

  await t.test('Reduced motion respects deliberate opt-in and reset',async t=>{
    const {context,page}=await open({viewport:{width:375,height:667},reducedMotion:'reduce'});
    t.after(()=>context.close());
    const animation=()=>page.locator('.motion').first().evaluate(el=>getComputedStyle(el).animationName);
    assert.equal(await animation(),'none');
    await page.goto(origin+'/?motion=on',{waitUntil:'networkidle'});
    assert.notEqual(await animation(),'none');
    await page.goto(origin+'/',{waitUntil:'networkidle'});
    assert.notEqual(await animation(),'none','The explicit choice persists locally');
    await page.goto(origin+'/?motion=off',{waitUntil:'networkidle'});
    assert.equal(await animation(),'none');
    await page.goto(origin+'/',{waitUntil:'networkidle'});
    assert.equal(await animation(),'none');
  });

  await t.test('At least ten physical places visibly change with motion enabled',async t=>{
    const {context,page}=await open({viewport:{width:375,height:1200},reducedMotion:'reduce'});
    t.after(()=>context.close());
    await page.goto(origin+'/?motion=on',{waitUntil:'networkidle'});
    const sample=()=>page.locator('.motion').evaluateAll(parts=>parts.map(part=>({
      owner:part.dataset.owner,name:part.classList[3],
      value:getComputedStyle(part).transform+'/'+getComputedStyle(part).opacity
    })));
    const initial=await sample(),places=new Set(),kinds=new Set();
    for(let i=0;i<6;i++){
      await page.waitForTimeout(500);
      (await sample()).forEach((part,index)=>{if(part.value!==initial[index].value){places.add(part.owner);kinds.add(part.name)}});
    }
    assert.ok(places.size>=10,`${places.size} distinct physical objects visibly animate`);
    assert.ok(kinds.size>=10,`${kinds.size} distinct physical animation types change`);
  });

  await t.test('Offscreen fragments pause and restart on re-entry',async t=>{
    const {context,page}=await open({viewport:{width:375,height:667}});
    t.after(()=>context.close());
    const upper=page.locator('.motion').first();
    await upper.scrollIntoViewIfNeeded();
    await page.waitForFunction(()=>getComputedStyle(document.querySelector('.motion')).animationPlayState==='running');
    await page.locator('button.room-control').first().click();
    assert.ok(await page.locator('.world-object.used').count()>0);
    await page.evaluate(()=>{
      Object.defineProperty(document,'hidden',{value:true,configurable:true});
      document.dispatchEvent(new Event('visibilitychange'));
    });
    assert.equal(await page.locator('.motion,.world-object.used').evaluateAll(parts=>parts.every(part=>getComputedStyle(part).animationPlayState==='paused')),true,'Hidden pages pause idle and recent tap feedback');
    await page.evaluate(()=>{
      Object.defineProperty(document,'hidden',{value:false,configurable:true});
      document.dispatchEvent(new Event('visibilitychange'));
    });
    await page.evaluate(()=>scrollTo(0,document.documentElement.scrollHeight));
    await page.waitForFunction(()=>getComputedStyle(document.querySelector('.motion')).animationPlayState==='paused');
    await page.evaluate(()=>scrollTo(0,0));
    await page.waitForFunction(()=>getComputedStyle(document.querySelector('.motion')).animationPlayState==='running');
  });

  await t.test('The destination links work without JavaScript',async t=>{
    const context=await browser.newContext({javaScriptEnabled:false,viewport:{width:375,height:667}});
    t.after(()=>context.close());
    const page=await context.newPage();await page.goto(origin+'/');
    assert.equal(await page.locator('button.room-control:visible').count(),0);
    for(const destination of ['/receipt/','/sys/','/cctv/']){
      await page.goto(origin+'/');
      await Promise.all([page.waitForURL(origin+destination),page.locator(`a.room-control[href="${destination}"]`).click()]);
    }
  });
});
