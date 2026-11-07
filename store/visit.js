/* Local, touch-first inspections. Destinations remain normal anchors. */
(()=>{
 const room=document.querySelector('.room');if(!room)return;
 const html=document.documentElement,note=room.querySelector('#room-note');
 const controls=[...room.querySelectorAll('.room-control')],reduce=matchMedia('(prefers-reduced-motion: reduce)');
 let selected=null,noticeTimer=0,navigationTimer=0,positionFrame=0,usedParts=[];
 const motionKey='57-night-room.motion';
 const getChoice=()=>{try{return localStorage.getItem(motionKey)==='on'}catch{return false}};
 let opted=getChoice();const query=new URL(location.href).searchParams.get('motion');
 if(query==='on'||query==='off'){
  opted=query==='on';try{opted?localStorage.setItem(motionKey,'on'):localStorage.removeItem(motionKey)}catch{}
 }
 const syncMotion=()=>html.classList.toggle('room-motion',opted);
 const hasMotion=()=>opted||!reduce.matches;syncMotion();
 addEventListener('storage',event=>{if(event.key===motionKey){opted=getChoice();syncMotion()}});
 const owners=new Map();
 for(const part of room.querySelectorAll('[data-owner]')){
  const parts=owners.get(part.dataset.owner)||[];parts.push(part);owners.set(part.dataset.owner,parts);
 }
 const artFor=control=>owners.get(control.dataset.object)||[];
 const close=()=>{clearTimeout(navigationTimer);navigationTimer=0;if(selected)selected.setAttribute('aria-expanded','false');selected=null;note.hidden=true};
 const position=()=>{
  if(!selected)return;const bounds=room.getBoundingClientRect(),target=selected.getBoundingClientRect();
  const view=window.visualViewport,left=view?view.offsetLeft:0,top=view?view.offsetTop:0;
  const right=left+(view?view.width:innerWidth),bottom=top+(view?view.height:innerHeight);
  if(target.bottom<=top||target.top>=bottom||target.right<=left||target.left>=right){close();return}
  note.hidden=false;const width=note.offsetWidth,height=note.offsetHeight;
  const minX=Math.max(5,left-bounds.left+5),maxX=Math.min(bounds.width-width-5,right-bounds.left-width-5);
  const minY=Math.max(4,top-bounds.top+5),maxY=Math.min(bounds.height-height-4,bottom-bounds.top-height-5);
  let x=target.left-bounds.left+(target.width-width)/2,y=target.top-bounds.top-height-7;
  if(y<minY)y=target.bottom-bounds.top+7;
  x=Math.max(minX,Math.min(maxX,x));y=Math.max(minY,Math.min(maxY,y));
  note.style.left=x+'px';note.style.top=y+'px';
 };
 const feedback=control=>{
  clearTimeout(noticeTimer);usedParts.forEach(p=>p.classList.remove('used'));const parts=artFor(control),screens=parts.filter(p=>p.matches('.sys-type,.display-scroll'));usedParts=screens.length?screens:parts;
  if(!usedParts.length)return;void usedParts[0].getBoundingClientRect();usedParts.forEach(p=>p.classList.add('used'));
  noticeTimer=setTimeout(()=>{usedParts.forEach(p=>p.classList.remove('used'));usedParts=[]},320);
 };
 for(const control of controls){
  if(control.tagName==='BUTTON')control.hidden=false;
  control.addEventListener('focus',()=>artFor(control).forEach(p=>p.classList.add('focused')));
  control.addEventListener('blur',()=>artFor(control).forEach(p=>p.classList.remove('focused')));
  control.addEventListener('click',event=>{
   if(control.tagName==='A'){
    if(event.button||event.metaKey||event.ctrlKey||event.altKey||event.shiftKey)return;
    close();feedback(control);if(hasMotion()){event.preventDefault();navigationTimer=setTimeout(()=>location.assign(control.href),240)}return;
   }
   event.stopPropagation();if(selected===control){close();return}close();selected=control;
   control.setAttribute('aria-expanded','true');note.querySelector('strong').textContent=control.dataset.noteTitle;
   note.querySelector('span').textContent=control.dataset.note;feedback(control);position();
  });
 }
 document.addEventListener('click',event=>{if(!event.target.closest('.room-control'))close()});
 document.addEventListener('keydown',event=>{if(event.key==='Escape')close()});
 const schedulePosition=()=>{cancelAnimationFrame(positionFrame);positionFrame=requestAnimationFrame(position)};
 addEventListener('scroll',schedulePosition,{passive:true});addEventListener('resize',schedulePosition);
 if(window.visualViewport){visualViewport.addEventListener('scroll',schedulePosition,{passive:true});visualViewport.addEventListener('resize',schedulePosition)}
 const refresh=()=>{
  html.classList.toggle('room-paused',document.hidden);
  for(const control of controls){const b=control.getBoundingClientRect();artFor(control).forEach(p=>p.classList.toggle('sleep',b.bottom < -100||b.top>innerHeight+100))}
 };
 if('IntersectionObserver'in window){const observer=new IntersectionObserver(entries=>{for(const entry of entries)artFor(entry.target).forEach(p=>p.classList.toggle('sleep',!entry.isIntersecting))},{rootMargin:'100px'});controls.forEach(c=>observer.observe(c))}
 document.addEventListener('visibilitychange',refresh);
 for(const name of ['pageshow','focus'])addEventListener(name,refresh);refresh();
})();
