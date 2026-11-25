(function(){
  var top=document.getElementById('top');
  var legal=!document.querySelector('.hero');
  function onScroll(){ if(legal||window.scrollY>window.innerHeight*0.55){top.classList.add('solid')}else{top.classList.remove('solid')} }
  onScroll(); window.addEventListener('scroll',onScroll,{passive:true});

  var b=document.querySelector('.burger'), nav=document.getElementById('nav');
  if(b){
    b.addEventListener('click',function(){var o=nav.classList.toggle('open');b.setAttribute('aria-expanded',o)});
    nav.addEventListener('click',function(e){if(e.target.tagName==='A'){nav.classList.remove('open');b.setAttribute('aria-expanded','false')}});
  }

  var els=document.querySelectorAll('.reveal');
  if('IntersectionObserver' in window){
    var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}})},{rootMargin:'0px 0px -10% 0px'});
    els.forEach(function(el){io.observe(el)});
  }else{els.forEach(function(el){el.classList.add('in')})}

  // parallax for background layers
  var layers=[].slice.call(document.querySelectorAll('.bgimg[data-speed]'));
  var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(layers.length&&!reduce){
    var ticking=false;
    function px(){
      var vh=window.innerHeight;
      layers.forEach(function(el){
        var host=el.parentNode.classList.contains('bgwrap')?el.parentNode:(el.closest('section')||el.parentNode);var r=host.getBoundingClientRect();
        if(r.bottom<0||r.top>vh)return;
        var c=(r.top+r.height/2-vh/2)*parseFloat(el.getAttribute('data-speed'));
        el.style.transform='translate3d(0,'+(-c).toFixed(1)+'px,0)';
      });ticking=false;
    }
    window.addEventListener('scroll',function(){if(!ticking){ticking=true;requestAnimationFrame(px)}},{passive:true});
    window.addEventListener('resize',px);px();
  }
})();
// v18: pull author/contact background images up so they join the image above (no black gaps)
(function(){
  var OV=-70;
  function chain(prevWrap,sec){
    if(!prevWrap||!sec)return;var w=sec.querySelector(':scope>.bgwrap');if(!w)return;
    var pb=prevWrap.getBoundingClientRect().bottom, st=sec.getBoundingClientRect().top;
    var off=Math.min(0,Math.round(pb-st-OV));w.style.top=off+'px';w.style.bottom='0';w.style.height='auto';
  }
  function run(){
    var b=document.querySelector('#beings .bgwrap2'),a=document.getElementById('author'),c=document.getElementById('contact');
    chain(b,a); chain(a&&a.querySelector(':scope>.bgwrap'),c);
  }
  run();window.addEventListener('load',run);window.addEventListener('resize',run);
})();
// v36: load background images only when they come near the screen (same image quality, faster start)
(function(){
  var els=[].slice.call(document.querySelectorAll('.bgimg'));
  function on(e){e.classList.add('on')}
  if(!('IntersectionObserver' in window)){els.forEach(on);return}
  var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){on(e.target);io.unobserve(e.target)}})},{rootMargin:'900px 0px 900px 0px'});
  els.forEach(function(e){io.observe(e)});
})();
// v39: original score player
(function(){
  var S=document.getElementById('score');if(!S)return;
  var P=S.querySelector('.sc-player'),A=S.querySelector('.sc-audio'),btn=S.querySelector('.sc-play'),
      W=S.querySelector('.sc-wave'),C=W.querySelector('canvas'),X=C.getContext('2d'),
      cur=S.querySelector('.cur'),tot=S.querySelector('.tot'),ti=S.querySelector('.sc-title'),pt=S.querySelector('.sc-part'),
      vol=S.querySelector('.sc-vol input'),list=S.querySelector('.sc-list'),
      T=[].slice.call(S.querySelectorAll('.sc-tr')),parts=JSON.parse(S.dataset.parts),idx=0,peaks=[],hover=-1;
  function fmt(s){s=Math.max(0,Math.floor(s||0));return Math.floor(s/60)+':'+('0'+s%60).slice(-2)}
  function dec(w){var a=[];for(var i=0;i<w.length;i++)a.push((w.charCodeAt(i)-48)/74);return a}
  function draw(){
    var r=window.devicePixelRatio||1,w=W.clientWidth,h=W.clientHeight;if(!w)return;
    if(C.width!==Math.round(w*r)||C.height!==Math.round(h*r)){C.width=Math.round(w*r);C.height=Math.round(h*r)}
    X.setTransform(r,0,0,r,0,0);X.clearRect(0,0,w,h);
    var n=peaks.length,bw=w/n,gap=Math.max(1,bw*.35),prog=A.duration?A.currentTime/A.duration:0,mid=h*.62;
    for(var i=0;i<n;i++){
      var v=Math.max(.04,peaks[i]),x=i*bw,f=(i+.5)/n,up=v*mid*.96,dn=v*(h-mid)*.8;
      var played=f<=prog,hov=hover>=0&&f<=hover;
      X.fillStyle=played?'#5fd0ff':(hov?'rgba(223,231,238,.55)':'rgba(154,166,178,.32)');
      X.fillRect(x,mid-up,bw-gap,up);
      X.fillStyle=played?'rgba(95,208,255,.32)':'rgba(154,166,178,.12)';
      X.fillRect(x,mid+1,bw-gap,dn);
    }
  }
  function load(i,play){
    idx=(i+T.length)%T.length;var t=T[idx];
    T.forEach(function(b){b.classList.toggle('on',b===t);b.removeAttribute('aria-current')});t.setAttribute('aria-current','true');
    A.src=t.dataset.src;peaks=dec(t.dataset.w);pend=-1;full(t.dataset.src,idx);
    ti.textContent=t.querySelector('.ti').textContent;pt.textContent=parts[t.dataset.p-1];
    tot.textContent=fmt(+t.dataset.d);cur.textContent='0:00';W.setAttribute('aria-valuemax',t.dataset.d);
    draw();
    if('mediaSession' in navigator){try{navigator.mediaSession.metadata=new MediaMetadata({title:ti.textContent,artist:'Nedy John Cross',album:'UNDER THE DARK – Original Score'})}catch(e){}}
    if(play)A.play();
  }
  function toggle(){if(!A.getAttribute('src'))load(idx,true);else if(A.paused)A.play();else A.pause()}
  btn.addEventListener('click',toggle);
  S.querySelector('.sc-prev').addEventListener('click',function(){if(A.currentTime>3)A.currentTime=0;else load(idx-1,!A.paused||true)});
  S.querySelector('.sc-next').addEventListener('click',function(){load(idx+1,true)});
  T.forEach(function(b,i){b.addEventListener('click',function(){if(i===idx&&A.getAttribute('src'))toggle();else load(i,true)})});
  A.addEventListener('play',function(){P.classList.add('playing');btn.setAttribute('aria-label',S.dataset.lblPause)});
  A.addEventListener('pause',function(){P.classList.remove('playing');btn.setAttribute('aria-label',S.dataset.lblPlay)});
  A.addEventListener('ended',function(){if(idx<T.length-1)load(idx+1,true)});
  A.addEventListener('timeupdate',function(){cur.textContent=fmt(A.currentTime);W.setAttribute('aria-valuenow',Math.floor(A.currentTime));draw()});
  A.addEventListener('loadedmetadata',function(){tot.textContent=fmt(A.duration)});
  A.volume=+vol.value;vol.addEventListener('input',function(){A.volume=+vol.value});
  function pos(e){var r=W.getBoundingClientRect();return Math.min(1,Math.max(0,(e.clientX-r.left)/r.width))}
  // server streams without byte ranges -> load the whole file once as blob so seeking works
  var blobs={},pend=-1;
  function full(src,i){
    if(blobs[src]){swap(blobs[src]);return}
    fetch(src).then(function(r){return r.blob()}).then(function(b){blobs[src]=URL.createObjectURL(b);if(idx===i&&T[idx].dataset.src===src)swap(blobs[src])}).catch(function(){});
  }
  function swap(u){
    if(A.src===u)return;var t=pend>=0?pend:A.currentTime,pl=!A.paused||pend>=0&&P.classList.contains('wantplay');
    A.src=u;A.addEventListener('loadedmetadata',function(){try{A.currentTime=t}catch(e){}if(pl)A.play();pend=-1;P.classList.remove('wantplay')},{once:true});A.load();
  }
  function seek(f){
    if(!A.getAttribute('src'))load(idx,false);
    var src=T[idx].dataset.src,d=A.duration||+T[idx].dataset.d;
    if(blobs[src]&&A.src===blobs[src]){A.currentTime=f*d;if(A.paused)A.play();return}
    pend=f*d;P.classList.add('wantplay');cur.textContent=fmt(pend);
  }
  W.addEventListener('click',function(e){seek(pos(e))});
  W.addEventListener('mousemove',function(e){hover=pos(e);draw()});
  W.addEventListener('mouseleave',function(){hover=-1;draw()});
  W.addEventListener('keydown',function(e){if(!A.duration)return;if(e.key==='ArrowRight'){A.currentTime=Math.min(A.duration,A.currentTime+5);e.preventDefault()}if(e.key==='ArrowLeft'){A.currentTime=Math.max(0,A.currentTime-5);e.preventDefault()}if(e.key===' '){toggle();e.preventDefault()}});
  S.querySelectorAll('.sc-tab').forEach(function(tb){tb.addEventListener('click',function(){
    var p=tb.dataset.p;S.querySelectorAll('.sc-tab').forEach(function(x){x.setAttribute('aria-pressed',x===tb?'true':'false')});
    S.querySelectorAll('.sc-grp').forEach(function(g){g.hidden=p!=='0'&&g.dataset.p!==p});list.classList.toggle('one',p!=='0');
  })});
  if('mediaSession' in navigator){try{
    navigator.mediaSession.setActionHandler('play',function(){A.play()});navigator.mediaSession.setActionHandler('pause',function(){A.pause()});
    navigator.mediaSession.setActionHandler('previoustrack',function(){load(idx-1,true)});navigator.mediaSession.setActionHandler('nexttrack',function(){load(idx+1,true)});
  }catch(e){}}
  A.addEventListener('contextmenu',function(e){e.preventDefault()});
  peaks=dec(T[0].dataset.w);T[0].classList.add('on');
  window.addEventListener('resize',draw);if('ResizeObserver' in window)new ResizeObserver(draw).observe(W);draw();
})();
