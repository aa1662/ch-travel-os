const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const source = fs.readFileSync('core/js/app.js', 'utf8').split('function initReaderFeedback()')[1];
function harness(fetch, timers = {}, hostname = '127.0.0.1') {
  const nodes = {};
  for (const id of ['btnFeedbackLike','feedbackLikeStatus','btnToggleComment','btnSubmitFeedback','btnRetryFeedback','feedbackContent','feedbackNickname','readerFeedbackForm']) {
    nodes[id] = {disabled:false,hidden:false,value:'preserved draft',dataset:{},handlers:{},
      reset(){this.resetCount=(this.resetCount||0)+1;},querySelector:()=>null, setAttribute(){},classList:{toggle(){},add(){},remove(){}},
      addEventListener(event,fn){this.handlers[event]=fn;}};
  }
  const section = {dataset:{articleId:'alpha:story'}};
  vm.runInNewContext('function initReaderFeedback()'+source+';initReaderFeedback();', {
    document:{querySelector:()=>section,getElementById:id=>nodes[id]||null},
    window:{location:{hostname}},
    fetch,localStorage:{getItem:()=> 'test-client-123456789'},crypto:{randomUUID:()=> 'test-uuid'},
    AbortController, setTimeout:timers.setTimeout||setTimeout,clearTimeout:timers.clearTimeout||clearTimeout,
  });
  nodes.section=section;
  return nodes;
}
const settle=()=>new Promise(resolve=>setImmediate(resolve));
test('status failure disables interaction, retries, validates response, preserves input', async()=>{
 let calls=0;
 const nodes=harness(async()=>{calls++;if(calls===1)throw Error('offline');return {ok:true,json:async()=>({success:true,article_id:'alpha:story',liked:true})};});
 for(const id of ['btnFeedbackLike','btnToggleComment','btnSubmitFeedback'])assert.equal(nodes[id].disabled,true,id);
 await settle();
 assert.match(nodes.feedbackLikeStatus.textContent,/重試/);
 assert.equal(nodes.btnRetryFeedback.hidden,false);
 await nodes.readerFeedbackForm.handlers.submit({preventDefault(){}});
 assert.equal(calls,1);
 await nodes.btnRetryFeedback.handlers.click();
 for(const id of ['btnFeedbackLike','btnToggleComment','btnSubmitFeedback'])assert.equal(nodes[id].disabled,false,id);
 assert.equal(nodes.feedbackContent.value,'preserved draft');
});
test('HTTP and malformed status failures never enable controls',async()=>{
 for(const response of [{ok:false,json:async()=>({success:true,article_id:'alpha:story',liked:true})},{ok:true,json:async()=>({success:true})}]){
 const nodes=harness(async()=>response);await settle();assert.equal(nodes.btnFeedbackLike.disabled,true);assert.equal(nodes.btnSubmitFeedback.disabled,true);
 }
});

const statusOK=()=>({ok:true,status:200,json:async()=>({success:true,article_id:'alpha:story',liked:false})});
test('wrong article status stays disabled',async()=>{
 const n=harness(async()=>({ok:true,json:async()=>({success:true,article_id:'other:story',liked:false})}));await settle();assert.equal(n.btnFeedbackLike.disabled,true);
});
test('bounded status timeout can retry successfully',async()=>{
 let timeout;let calls=0;
 const n=harness((url,opts)=>{if(++calls>1)return Promise.resolve(statusOK());return new Promise((_,reject)=>opts.signal.addEventListener('abort',()=>reject(Error('timeout'))));}, {setTimeout:fn=>{timeout=fn;return 1;},clearTimeout(){}});
 timeout();await settle();assert.equal(n.btnSubmitFeedback.disabled,true);assert.equal(n.btnRetryFeedback.hidden,false);
 await n.btnRetryFeedback.handlers.click();assert.equal(n.btnSubmitFeedback.disabled,false);
});
test('message failure and timeout keep draft and submission ID, retry enables sending; duplicate submit blocked',async()=>{
 for(const failure of ['network','timeout','500']) {
  let timeout;let writes=[];let recover=false;
  const n=harness((url,opts)=>{
   if(url.includes('/status?'))return Promise.resolve(statusOK());
   writes.push(JSON.parse(opts.body));
   if(recover)return Promise.resolve({ok:true,status:200,json:async()=>({success:true})});
   if(failure==='network')return Promise.reject(Error('offline'));
   if(failure==='500')return Promise.resolve({ok:false,status:503,json:async()=>({})});
   return new Promise((_,reject)=>opts.signal.addEventListener('abort',()=>reject(Error('timeout'))));
  },{setTimeout:fn=>{timeout=fn;return 1;},clearTimeout(){}});
  await settle();
  const first=n.readerFeedbackForm.handlers.submit({preventDefault(){}});
  await n.readerFeedbackForm.handlers.submit({preventDefault(){}});
  assert.equal(writes.length,1);
  if(failure==='timeout')timeout();await first;
  assert.equal(n.feedbackContent.value,'preserved draft');assert.equal(n.btnSubmitFeedback.disabled,true);assert.equal(n.btnRetryFeedback.hidden,false);
  recover=true;await n.btnRetryFeedback.handlers.click();await n.readerFeedbackForm.handlers.submit({preventDefault(){}});
  assert.equal(writes.length,2);assert.equal(writes[0].client_submission_id,writes[1].client_submission_id);assert.equal(n.readerFeedbackForm.resetCount,1);
 }
});
test('like timeout disables controls, status retry recovers; 400 and 429 are not outages',async()=>{
 let timeout;
 const n=harness((url,opts)=>url.includes('/status?')?Promise.resolve(statusOK()):new Promise((_,reject)=>opts.signal.addEventListener('abort',()=>reject(Error('timeout')))),{setTimeout:fn=>{timeout=fn;return 1;},clearTimeout(){}});
 await settle();const click=n.btnFeedbackLike.handlers.click();timeout();await click;assert.equal(n.btnFeedbackLike.disabled,true);await n.btnRetryFeedback.handlers.click();assert.equal(n.btnFeedbackLike.disabled,false);
 for(const code of [400,429]){
  const nodes=harness(async url=>url.includes('/status?')?statusOK():{ok:false,status:code,json:async()=>({success:false,error:'validation'})});
  await settle();await nodes.readerFeedbackForm.handlers.submit({preventDefault(){}});assert.equal(nodes.btnSubmitFeedback.disabled,false);assert.equal(nodes.feedbackContent.value,'preserved draft');assert.equal(nodes.btnRetryFeedback.hidden,true);
 }
});


test('production hides unavailable service, opens after successful check, and preserves visible drafts on later outage',async()=>{
 const offline=harness(async()=>{throw Error('offline')},{},'chxtravel.com');
 assert.equal(offline.section.hidden,true);await settle();assert.equal(offline.section.hidden,true);
 const connected=harness(async url=>url.includes('/status?')?statusOK():Promise.reject(Error('offline')),{},'chxtravel.com');
 assert.equal(connected.section.hidden,true);await settle();assert.equal(connected.section.hidden,false);
 await connected.readerFeedbackForm.handlers.submit({preventDefault(){}});
 assert.equal(connected.section.hidden,false);assert.equal(connected.feedbackContent.value,'preserved draft');
});
