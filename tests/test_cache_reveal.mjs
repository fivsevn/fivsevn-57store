import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';

const source = readFileSync(new URL('../site-assets/cache.js', import.meta.url), 'utf8');
for (const initialState of ['loading','complete']) {
  for (const value of ['', 'arbitrary words', '123456', '中文']) {
    let submit, ready, prevented = 0, network = 0;
    const reply = {hidden:true};
    const form = {hidden:false,dataset:{cacheReveal:'reply'},value,addEventListener(name,listener) { assert.equal(name,'submit');submit=listener; }};
    const document = {readyState:initialState,querySelectorAll:()=>[form],getElementById:id => { assert.equal(id,'reply');return reply; },addEventListener:(name,listener)=>{ assert.equal(name,'DOMContentLoaded');ready=listener; }};
    vm.runInNewContext(source,{document,fetch:()=>{network++;throw Error('Unexpected network request');},XMLHttpRequest:()=>{network++;throw Error('Unexpected network request');}});
    if (ready) ready();
    assert.equal(typeof submit,'function');
    submit({preventDefault(){prevented++;}});
    assert.equal(prevented,1);
    assert.equal(network,0);
    assert.equal(reply.hidden,false);
    assert.equal(form.hidden,true);
  }
}
console.log('Passed 8 Cache reveal scenarios, including empty input and both document readiness states.');
