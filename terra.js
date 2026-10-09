(function(){
  var lang=document.documentElement.lang||'bg';
  var loc={bg:'bg-BG',de:'de-DE'}[lang]||lang;
  function clocks(){document.querySelectorAll('[data-tz]').forEach(function(b){try{b.textContent=new Intl.DateTimeFormat(loc,{hour:'2-digit',minute:'2-digit',timeZone:b.dataset.tz}).format(new Date())}catch(e){}})}
  clocks();setInterval(clocks,20000);
  /* Datumsleiste: Hauptstadt des Besucherlandes + Ortszeit, Temperatur am Standort (Daten: /api/wx, MET Norway) */
  (function(){var ec=document.getElementById('edclock'),ew=document.getElementById('edwx');if(!ec||!window.fetch)return;
    fetch('/api/wx?l='+lang,{credentials:'omit'}).then(function(r){return r.ok?r.json():null}).then(function(d){if(!d)return;
      if(d.cap&&d.tz){try{new Intl.DateTimeFormat(loc,{timeZone:d.tz});ec.querySelector('.ed-city').textContent=d.cap;ec.querySelector('b').dataset.tz=d.tz;clocks()}catch(e){}}
      if(ew&&typeof d.t==='number'){var s=d.sym||'',n=/_night/.test(s);
        var ic=/thunder/.test(s)?'⛈':/snow/.test(s)?'❄':/sleet/.test(s)?'🌨':/rain/.test(s)?'🌧':/fog/.test(s)?'🌫':/^cloudy/.test(s)?'☁':/partlycloudy/.test(s)?'⛅':/fair/.test(s)?(n?'☾':'🌤'):/clearsky/.test(s)?(n?'☾':'☀'):'';
        ew.innerHTML='<span class="wi" aria-hidden="true">'+ic+'</span>'+(d.t>0?'':d.t<0?'−':'')+Math.abs(d.t)+' °C';}
    }).catch(function(){});})();
  /* Service-Leiste der Startseite: Wetter in BG/DE-Städten + EZB-Euro-Kurse (Daten: /api/svc) */
  (function(){var sv=document.getElementById('svc');if(!sv||!window.fetch)return;var tx;try{tx=JSON.parse(sv.dataset.tx)}catch(e){return}
    function ic(s){var n=/_night/.test(s);return /thunder/.test(s)?'⛈':/snow/.test(s)?'❄':/sleet/.test(s)?'🌨':/rain/.test(s)?'🌧':/fog/.test(s)?'🌫':/^cloudy/.test(s)?'☁':/partlycloudy/.test(s)?'⛅':/fair/.test(s)?(n?'☾':'🌤'):/clearsky/.test(s)?(n?'☾':'☀'):''}
    function nf(v,d){try{return new Intl.NumberFormat(loc,{minimumFractionDigits:d,maximumFractionDigits:d}).format(v)}catch(e){return v.toFixed(d)}}
    fetch('/api/svc',{credentials:'omit'}).then(function(r){return r.ok?r.json():null}).then(function(d){if(!d)return;var ok=false;
      var by={};(d.wx||[]).forEach(function(w){by[w.c]=w});
      var wh=tx.order.filter(function(c){return by[c]&&typeof by[c].t==='number'}).map(function(c){var w=by[c];return '<span>'+tx.cities[c]+' <b><span aria-hidden="true">'+ic(w.sym||'')+'</span> '+(w.t<0?'−':'')+Math.abs(w.t)+'°</b></span>'}).join(' · ');
      if(wh){sv.querySelector('.svc-wx').innerHTML=wh;ok=true}else{sv.querySelector('.svc-wx').parentNode.hidden=true}
      var cr='';
      if(d.fx&&d.fx.rates){var r=d.fx.rates,ks=['USD','GBP','CHF','TRY','RON','PLN','JPY'].filter(function(k){return r[k]});
        sv.querySelector('.svc-fx').innerHTML='1 € = '+ks.map(function(k){return '<span><b>'+nf(r[k],k==='JPY'?1:(r[k]>=10?2:4))+'</b> '+k+'</span>'}).join(' · ');ok=true;
        var p=d.fx.date.split('-');cr=' '+p[2]+'.'+p[1]+'.'+p[0];}
      else{sv.querySelector('.svc-fx').textContent=''}
      sv.querySelector('.svc-cr').textContent=cr?tx.cr+cr:tx.cr.split(' · ')[0];
      if(ok)sv.hidden=false;
    }).catch(function(){});})();
  /* Laufbänder: feste Lesegeschwindigkeit (Pixel pro Sekunde), unabhängig von Gerät und Textlänge.
     Breite erst messen, wenn Schriften und Layout fertig sind; bei Änderung Animation sauber neu starten (iOS). */
  document.querySelectorAll('.ticker .tk-move').forEach(function(tk){var tb=tk.closest('.ticker'),pb=tb.querySelector('.tk-pause'),last=0;
    var setDur=function(){var w=tk.firstElementChild.getBoundingClientRect().width;if(w<200)return;
      var pps=window.innerWidth<700?55:70,d=Math.max(25,w/pps);if(Math.abs(d-last)<1)return;last=d;
      tk.style.setProperty('--dur',d.toFixed(1)+'s');tk.style.animationName='none';void tk.offsetWidth;tk.style.animationName='';};
    setDur();
    if(document.fonts&&document.fonts.ready)document.fonts.ready.then(setDur);
    window.addEventListener('load',setDur);
    if(window.ResizeObserver)new ResizeObserver(setDur).observe(tk.firstElementChild);else window.addEventListener('resize',setDur);
    if(pb)pb.addEventListener('click',function(){var p=tb.classList.toggle('paused');pb.setAttribute('aria-pressed',p?'true':'false')});});
  function seeded(str){var h=2166136261;for(var k=0;k<str.length;k++){h^=str.charCodeAt(k);h=Math.imul(h,16777619)}return function(){h^=h<<13;h^=h>>>17;h^=h<<5;return((h>>>0)%10000)/10000}}
  function paint(){var root=getComputedStyle(document.documentElement);var ink=root.getPropertyValue('--ink').trim()||'#101a1d';var red=root.getPropertyValue('--signal').trim()||'#e0342a';
    document.querySelectorAll('.plate canvas').forEach(function(cv){var r=cv.getBoundingClientRect();if(!r.width)return;var dpr=Math.min(2,window.devicePixelRatio||1);cv.width=r.width*dpr;cv.height=r.height*dpr;var g=cv.getContext('2d');g.scale(dpr,dpr);var rnd=seeded(cv.dataset.seed||'x');var w=r.width,h=r.height;
      var cx=w*(.45+rnd()*.3),cy=h*(.45+rnd()*.2),R=Math.min(w,h)*(.55+rnd()*.25),step=Math.max(5,w/70);g.fillStyle=ink;
      for(var y=step/2;y<h;y+=step)for(var x=step/2;x<w;x+=step){var dx=(x-cx)/R,dy=(y-cy)/R,d=Math.sqrt(dx*dx+dy*dy);var v=d<1?(.35+.5*Math.max(0,1-d)+.15*Math.sin(dx*7+dy*4)):.08+.1*Math.max(0,1.6-d);var lat=Math.abs(Math.sin(dy*Math.PI*3))<.08||Math.abs(Math.sin(dx*Math.PI*2.4))<.06;if(d<1&&lat)v=.95;v=Math.max(0,Math.min(1,v));g.beginPath();g.arc(x,y,step*.48*Math.sqrt(v),0,Math.PI*2);g.fill()}
      g.fillStyle=red;g.beginPath();g.arc(cx+R*.62,cy-R*.55,Math.max(4,R*.07),0,Math.PI*2);g.fill()})}
  paint();var t;window.addEventListener('resize',function(){clearTimeout(t);t=setTimeout(paint,150)});
  try{matchMedia('(prefers-color-scheme: dark)').addEventListener('change',paint)}catch(e){}
})();

/* YouTube-Trailer: erst nach Klick laden (Datenschutz) */
document.querySelectorAll('.yt[data-yt] .yt-play').forEach(function(b){
  b.addEventListener('click',function(){
    var box=b.parentNode, id=box.getAttribute('data-yt');
    var f=document.createElement('iframe');
    f.src='https://www.youtube-nocookie.com/embed/'+encodeURIComponent(id)+'?autoplay=1&rel=0';
    f.title='YouTube';f.allow='autoplay; encrypted-media; picture-in-picture; fullscreen';f.allowFullscreen=true;
    f.referrerPolicy='strict-origin-when-cross-origin';
    box.innerHTML='';box.appendChild(f);box.classList.add('on');
  });
});

/* Sprachwahl merken: wer die Sprache selbst wählt, wird auf der Startseite nicht mehr automatisch umgeleitet */
document.querySelectorAll('.langs a[hreflang]').forEach(function(a){
  a.addEventListener('click',function(){
    document.cookie='twn_lang='+a.getAttribute('hreflang')+';path=/;max-age=31536000;SameSite=Lax;Secure';
  });
});

/* Mobil-Menü auf- und zuklappen */
(function(){var n=document.getElementById('mainnav');if(!n)return;var b=n.querySelector('.nav-tg');if(!b)return;
b.addEventListener('click',function(){var o=n.classList.toggle('open');b.setAttribute('aria-expanded',o?'true':'false');});
document.addEventListener('keydown',function(ev){if(ev.key==='Escape'&&n.classList.contains('open')){n.classList.remove('open');b.setAttribute('aria-expanded','false');b.focus();}});})();

/* Menü v2: kompakte Sticky-Leiste + aktive Rubrik in der Wisch-Leiste sichtbar */
(function(){var n=document.getElementById('mainnav'),s=document.getElementById('nv-sentinel');if(!n)return;
if(s&&'IntersectionObserver' in window){new IntersectionObserver(function(e){n.classList.toggle('stuck',!e[0].isIntersecting);},{threshold:0}).observe(s);}
var w=n.querySelector('.nv-swipe a[aria-current="page"]');if(w&&w.parentNode){var p=w.parentNode;p.scrollLeft=Math.max(0,w.offsetLeft-p.clientWidth/2+w.clientWidth/2);}
document.addEventListener('click',function(ev){if(n.classList.contains('open')&&!n.contains(ev.target)){n.classList.remove('open');var b=n.querySelector('.nav-tg');if(b)b.setAttribute('aria-expanded','false');}});})();

/* Mobil-Menü als eigenes Fenster: unter der Leiste fixiert, innen scrollbar, Seite dahinter gesperrt */
(function(){var n=document.getElementById('mainnav');if(!n)return;var b=n.querySelector('.nav-tg'),it=document.getElementById('navitems'),bar=n.querySelector('.nv-bar');if(!b||!it||!bar)return;
var ly=null,bs=document.body.style;
function lock(){if(ly!==null)return;ly=scrollY;document.documentElement.classList.add('nav-locked');}
function unlock(){if(ly===null)return;document.documentElement.classList.remove('nav-locked');ly=null;}
function place(){if(!n.classList.contains('open')||innerWidth>860){it.style.top=it.style.left=it.style.width=it.style.maxHeight='';unlock();return;}
var r=bar.getBoundingClientRect();if(r.bottom<=0||r.top>=innerHeight){n.classList.remove('open');b.setAttribute('aria-expanded','false');unlock();return;}lock();it.style.top=r.bottom+'px';it.style.left=r.left+'px';it.style.width=r.width+'px';it.style.maxHeight=(innerHeight-r.bottom)+'px';}
document.addEventListener('touchmove',function(ev){if(ly!==null&&!it.contains(ev.target))ev.preventDefault();},{passive:false});
document.addEventListener('wheel',function(ev){if(ly!==null&&!it.contains(ev.target))ev.preventDefault();},{passive:false});
b.addEventListener('click',function(){if(n.classList.contains('open')&&innerWidth<=860){var t=n.getBoundingClientRect().top;if(t>0)scrollTo(0,scrollY+t+2);}setTimeout(place,30);});document.addEventListener('click',function(){setTimeout(place,0);});
addEventListener('resize',place);addEventListener('orientationchange',place);
document.addEventListener('keydown',function(ev){if(ev.key==='Escape')setTimeout(place,0);});})();
(function(){var box=document.querySelector('.live-box');if(!box||!window.fetch)return;
var kind=box.getAttribute('data-live'),tx={},nt={};try{tx=JSON.parse(box.getAttribute('data-tx'))}catch(e){}try{nt=JSON.parse(box.getAttribute('data-nt')||'{}')}catch(e){}
var list=box.querySelector('.live-list'),timer=null,LV={'1H':1,'HT':1,'2H':1,'ET':1,'BT':1,'P':1,'SUSP':1,'INT':1,'LIVE':1},FT={'FT':1,'AET':1,'PEN':1};
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function nm(n){return nt[n]||n}
function hm(ts){var d=new Date(ts*1000);return d.toLocaleTimeString(box.getAttribute('data-l')==='bg'?'bg-BG':box.getAttribute('data-l')==='de'?'de-DE':'en-GB',{hour:'2-digit',minute:'2-digit',timeZone:box.getAttribute('data-l')==='bg'?'Europe/Sofia':'Europe/Berlin'})}
function stat(m){if(LV[m.st])return m.st==='HT'?'<b class="lv-on">'+esc(tx.ht)+'</b>':'<b class="lv-on">'+esc(m.min)+(m.ext?'+'+esc(m.ext):'')+'′</b>';if(FT[m.st])return '<span class="lv-ft">'+esc(tx.ft)+'</span>';return '<span class="lv-ko">'+hm(m.ts)+'</span>'}
function evs(m){var o='';(m.ev||[]).forEach(function(e){if(e.ty==='sub')return;var ic=e.ty==='yc'?'<i class="lv-yc"></i>':e.ty==='rc'?'<i class="lv-rc"></i>':e.ty==='mp'?'✕':'⚽';
o+='<li class="lv-'+e.side+'">'+ic+' '+esc(e.m)+(e.x?'+'+esc(e.x):'')+'′ '+esc(e.p)+(e.ty==='pen'?' ('+esc(tx.pen)+')':e.ty==='og'?' ('+esc(tx.og)+')':'')+'</li>'});return o?'<ul class="lv-ev">'+o+'</ul>':''}
function render(d){var ok=d&&d.ok&&d.m;if(!ok){box.hidden=true;return}var ids=kind==='nat'?d.nat:d.club,ms=d.m.filter(function(m){return ids.indexOf(m.lg)>=0});
if(!ms.length){box.hidden=true;return}var g={},order=[];ms.forEach(function(m){var k=m.ln;if(!g[k]){g[k]=[];order.push(k)}g[k].push(m)});
var h='';order.forEach(function(k){h+='<div class="lv-lg"><h3>'+esc(k)+'</h3>';g[k].forEach(function(m){var on=LV[m.st];
h+='<div class="lv-m'+(on?' is-live':'')+'"><div class="lv-row"><span class="lv-st">'+stat(m)+'</span><span class="lv-t lv-th">'+esc(nm(m.h))+'</span><span class="lv-sc">'+(m.gh==null?'–':esc(m.gh))+' : '+(m.ga==null?'–':esc(m.ga))+'</span><span class="lv-t">'+esc(nm(m.a))+'</span></div>'+evs(m)+'</div>'});h+='</div>'});
list.innerHTML=h;box.hidden=false;return d.live}
function load(){fetch('/api/live',{cache:'no-store'}).then(function(r){return r.json()}).then(function(d){var live=render(d);clearTimeout(timer);timer=setTimeout(load,live?60000:300000)}).catch(function(){clearTimeout(timer);timer=setTimeout(load,300000)})}
load();document.addEventListener('visibilitychange',function(){if(!document.hidden){clearTimeout(timer);load()}})})();
/* Börse: Live-Kursband (TradingView) – lädt erst nach Klick (Datenschutz), Entscheidung wird gemerkt (seit 09.10.2026) */
(function(){var b=document.querySelector('.ticker.boerse');if(!b)return;var go=b.querySelector('.tv-go');
function ok(){try{return localStorage.getItem('twn_tv')==='1'}catch(e){return false}}
function load(){try{localStorage.setItem('twn_tv','1')}catch(e){}
var tr=b.querySelector('.tk-track'),pz=b.querySelector('.tk-pause');if(pz)pz.remove();if(go)go.remove();
var w=document.createElement('div');w.className='tradingview-widget-container tv-band';var i=document.createElement('div');i.className='tradingview-widget-container__widget';w.appendChild(i);
var sc=document.createElement('script');sc.src='https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js';sc.async=true;
sc.textContent=JSON.stringify({symbols:[{proName:'XETR:DAX',title:'DAX'},{proName:'FOREXCOM:SPXUSD',title:'S&P 500'},{proName:'FOREXCOM:NSXUSD',title:'Nasdaq 100'},{proName:'FOREXCOM:DJI',title:'Dow Jones'},{proName:'FX_IDC:EURUSD',title:'EUR/USD'},{proName:'OANDA:XAUUSD',title:'Gold'},{proName:'TVC:UKOIL',title:'Brent'},{proName:'BITSTAMP:BTCUSD',title:'Bitcoin'}],showSymbolLogo:true,isTransparent:true,displayMode:'adaptive',colorTheme:'dark',locale:b.getAttribute('data-tv')||'en'});
w.appendChild(sc);tr.innerHTML='';tr.appendChild(w);b.classList.add('tv-on')}
if(go)go.addEventListener('click',load);if(ok())load()})();
