/* Bulgarischsprachige Besucher, die über Google o. Ä. auf einer EN-/DE-Seite landen, zur bulgarischen Fassung derselben Seite leiten
   (Nedy 24.10.2026). Nicht bei selbst gewählter Sprache (Cookie twn_lang), nicht bei Navigation innerhalb der Seite, nie für Bots. */
(function(){try{
  var l=document.documentElement.lang;if(!l||l==='bg')return;
  if(/(?:^|;\s*)twn_lang=/.test(document.cookie))return;
  if(navigator.webdriver||/bot|crawl|spider|google|bing|yandex|lighthouse|headless|preview/i.test(navigator.userAgent))return;
  if(document.referrer&&document.referrer.indexOf(location.origin)===0)return;
  var nl=((navigator.languages&&navigator.languages[0])||navigator.language||'').toLowerCase();
  if(nl.indexOf('bg')!==0)return;
  var a=document.querySelector('link[rel="alternate"][hreflang="bg"]');if(!a)return;
  var u=new URL(a.getAttribute('href'),location.href);if(u.origin!==location.origin||u.pathname===location.pathname)return;
  document.cookie='twn_lang=bg;path=/;max-age=31536000;SameSite=Lax;Secure'; /* verhindert Schleife mit der Länder-Umleitung der Startseite */
  location.replace(u.pathname+u.search+location.hash);
}catch(e){}})();
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
var list=box.querySelector('.live-list'),timer=null,LV={'1H':1,'HT':1,'2H':1,'ET':1,'BT':1,'P':1,'PT':1,'SUSP':1,'INT':1,'LIVE':1},FT={'FT':1,'AET':1,'PEN':1,'AP':1},URL=kind==='hb'?'/api/live?sport=handball':'/api/live';
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function nm(n){return nt[n]||n}
function hm(ts){var d=new Date(ts*1000);return d.toLocaleTimeString(box.getAttribute('data-l')==='bg'?'bg-BG':box.getAttribute('data-l')==='de'?'de-DE':'en-GB',{hour:'2-digit',minute:'2-digit',timeZone:box.getAttribute('data-l')==='bg'?'Europe/Sofia':'Europe/Berlin'})}
function stat(m){if(LV[m.st])return m.st==='HT'?'<b class="lv-on">'+esc(tx.ht)+'</b>':'<b class="lv-on">'+esc(m.min)+(m.ext?'+'+esc(m.ext):'')+'′</b>';if(FT[m.st])return '<span class="lv-ft">'+esc(tx.ft)+'</span>';return '<span class="lv-ko">'+hm(m.ts)+'</span>'}
function evs(m){var o='';(m.ev||[]).forEach(function(e){if(e.ty==='sub')return;var ic=e.ty==='yc'?'<i class="lv-yc"></i>':e.ty==='rc'?'<i class="lv-rc"></i>':e.ty==='mp'?'✕':'⚽';
o+='<li class="lv-'+e.side+'">'+ic+' '+esc(e.m)+(e.x?'+'+esc(e.x):'')+'′ '+esc(e.p)+(e.ty==='pen'?' ('+esc(tx.pen)+')':e.ty==='og'?' ('+esc(tx.og)+')':'')+'</li>'});return o?'<ul class="lv-ev">'+o+'</ul>':''}
function render(d){try{rows(d)}catch(e){}var ok=d&&d.ok&&d.m;if(!ok){if(box.getAttribute('data-empty')){d={m:[]}}else{box.hidden=true;return}}var ids=kind==='nat'?d.nat:kind==='hb'?null:box.getAttribute('data-lg')?[+box.getAttribute('data-lg')]:d.club,ms=d.m.filter(function(m){return !ids||ids.indexOf(m.lg)>=0});
if(!ms.length){var em=box.getAttribute('data-empty');if(em){list.innerHTML='<p class="lv-empty">'+esc(em)+'</p>';box.hidden=false}else box.hidden=true;return}var g={},order=[];ms.forEach(function(m){var k=m.ln;if(!g[k]){g[k]=[];order.push(k)}g[k].push(m)});
var h='';order.forEach(function(k){h+='<div class="lv-lg"><h3>'+esc(k)+'</h3>';g[k].forEach(function(m){var on=LV[m.st];
h+='<div class="lv-m'+(on?' is-live':'')+'"><div class="lv-row"><span class="lv-st">'+stat(m)+'</span><span class="lv-t lv-th">'+esc(nm(m.h))+'</span><span class="lv-sc">'+(m.gh==null?'–':esc(m.gh))+' : '+(m.ga==null?'–':esc(m.ga))+'</span><span class="lv-t">'+esc(nm(m.a))+'</span></div>'+evs(m)+'</div>'});h+='</div>'});
list.innerHTML=h;box.hidden=false;return d.live}
function nz(x){return String(x||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/\b(fc|sv|sc|vfb|vfl|tsg|tsv|ssv|ac|as|us|cf|ud|cd|rc|ss|afc|1|04|05|07|1899|1846|1909|de|of|the)\b/g,' ').replace(/[^a-z0-9 ]/g,' ').replace(/\s+/g,' ').trim()}
function same(x,y){x=nz(x);y=nz(y);if(!x||!y)return false;if(x===y||x.indexOf(y)>=0||y.indexOf(x)>=0)return true;var a=x.split(' '),b=y.split(' ');return a.some(function(w){return w.length>3&&b.indexOf(w)>=0})}
function rows(d){if(!d||!d.ok||!d.m)return;document.querySelectorAll('tr[data-day="'+d.day+'"]').forEach(function(tr){var m=d.m.filter(function(m){return same(m.h,tr.getAttribute('data-a'))&&same(m.a,tr.getAttribute('data-b'))})[0];if(!m||m.st==='NS'||m.gh==null)return;
var c=tr.querySelector('.fb-scc');if(!c)return;var on=LV[m.st];c.innerHTML='<b class="fb-sc'+(on?' fb-live':'')+'">'+esc(m.gh)+':'+esc(m.ga)+'</b>'+(on?'<span class="fb-min">'+(m.st==='HT'?esc(tx.ht):esc(m.min)+(m.ext?'+'+esc(m.ext):'')+'′')+'</span>':'')})}
function load(){fetch(URL,{cache:'no-store'}).then(function(r){return r.json()}).then(function(d){var live=render(d);clearTimeout(timer);timer=setTimeout(load,live?60000:300000)}).catch(function(){clearTimeout(timer);timer=setTimeout(load,300000)})}
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
/* Sport: zweites Laufband „⚽ LIVE“ mit den heutigen Fußballspielen (seit 09.10.2026) */
(function(){var b=document.querySelector('.ticker.fbt');if(!b||!window.fetch)return;var sets=b.querySelectorAll('.tk-set'),L=b.getAttribute('data-l'),t=null,
LV={'1H':1,'HT':1,'2H':1,'ET':1,'BT':1,'P':1,'SUSP':1,'INT':1,'LIVE':1},FT={'FT':1,'AET':1,'PEN':1};
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function hm(ts){return new Date(ts*1000).toLocaleTimeString(L==='bg'?'bg-BG':L==='de'?'de-DE':'en-GB',{hour:'2-digit',minute:'2-digit',timeZone:L==='bg'?'Europe/Sofia':'Europe/Berlin'})}
function draw(d){if(!d||!d.ok||!d.m||!d.m.length){b.hidden=true;return false}
var ms=d.m.slice().sort(function(x,y){var r=function(m){return LV[m.st]?0:FT[m.st]?1:2};return r(x)-r(y)||x.ts-y.ts});
var h=ms.map(function(m){var on=LV[m.st],fin=FT[m.st],sc=(on||fin)?esc(m.gh)+':'+esc(m.ga):'–:–',
st=on?(m.st==='HT'?esc(b.getAttribute('data-ht')):esc(m.min)+(m.ext?'+'+esc(m.ext):'')+'′'):fin?esc(b.getAttribute('data-ft')):hm(m.ts);
return '<span class="fq'+(on?' on':'')+'"><b class="fl">'+esc(m.ln)+'</b> '+esc(m.h)+' <span class="fs">'+sc+'</span> '+esc(m.a)+' <i class="fm">'+st+'</i></span><span class="sep" aria-hidden="true"></span>'}).join('');
sets[0].innerHTML=h;sets[1].innerHTML=h;b.hidden=false;return d.live}
function load(){fetch('/api/live',{cache:'no-store'}).then(function(r){return r.json()}).then(function(d){var live=draw(d);clearTimeout(t);t=setTimeout(load,live?60000:300000)}).catch(function(){clearTimeout(t);t=setTimeout(load,300000)})}
load();document.addEventListener('visibilitychange',function(){if(!document.hidden){clearTimeout(t);load()}})})();

/* Musik-Wochenplan: auf dem Handy den heutigen Tag in den sichtbaren Bereich schieben */
(function(){var d=document.querySelector('.mp-days .mp-d.on');if(d&&d.parentNode.scrollWidth>d.parentNode.clientWidth){d.parentNode.scrollLeft=Math.max(0,d.offsetLeft-d.parentNode.offsetLeft-8)}})();

/* Menü v4: Unterpunkte auf dem Handy auf- und zuklappen (Akkordeon) */
(function(){var n=document.getElementById('mainnav');if(!n)return;
n.addEventListener('click',function(ev){var b=ev.target.closest&&ev.target.closest('.nv-exp');if(!b)return;ev.preventDefault();ev.stopPropagation();
var d=b.parentNode,o=!d.classList.contains('ex');
Array.prototype.forEach.call(n.querySelectorAll('.nav-dd.ex'),function(x){if(x!==d){x.classList.remove('ex');var y=x.querySelector('.nv-exp');if(y)y.setAttribute('aria-expanded','false');}});
d.classList.toggle('ex',o);b.setAttribute('aria-expanded',o?'true':'false');});
var c=n.querySelector('.nav-dd .dd a[aria-current="page"]');if(c){var d=c.closest('.nav-dd');if(d){d.classList.add('ex');var b=d.querySelector('.nv-exp');if(b)b.setAttribute('aria-expanded','true');}}})();

/* TERRA WORLD RADIO (Nedy 05.11.2026): futuristischer Player – TWN-Nachrichten (KI-Stimme, DE/BG/EN) + Musikkanäle (static/radio/stations.json),
   eigenes Fenster, Visualizer, „Artikel anhören“ (Gerätestimme). Musikkanäle erscheinen erst mit geklärtem Stream als abspielbar. */
(function(){var L=(document.documentElement.lang||'bg').slice(0,2),
T={de:{r:'TERRA WORLD RADIO',tvb:'TERRA WORLD TV',tvtag:'Live-Nachrichten aus aller Welt',pick:'Sender wählen – das Live-Bild startet hier.',via:'Livestream: {n} · offizieller YouTube-Kanal des Senders',chs:'Sender',tv:'TV live',yt:'Beim Abspielen wird das Video von YouTube (Google) geladen.',big:'Größer',tvx:'TV schließen',lf:'Musik von laut.fm – öffnet in einem neuen Fenster.',tag:'Nachrichten · Musik · Welt',news:'TWN Nachrichten',nd:'Die Top-Meldungen in 3 Minuten',mus:'Musikkanäle',soon:'Bald',p:'Im eigenen Fenster',ph:'Läuft weiter, während Sie lesen.',a:'Artikel anhören',s:'Vorlesen stoppen',ai:'Nachrichten gesprochen mit einer KI-Stimme (ElevenLabs) auf Grundlage geprüfter Meldungen der TWN-Redaktion.',none:'Die nächste Ausgabe erscheint morgen früh.',x:'Schließen',en:'auf Englisch',dev:'Vorgelesen von der Stimme Ihres Geräts.',now:'Jetzt läuft',vol:'Lautstärke',play:'Abspielen',pause:'Pause',live:'LIVE',old:'Frühere Ausgaben'},
bg:{r:'TERRA WORLD RADIO',tvb:'TERRA WORLD TV',tvtag:'Новини на живо от целия свят',pick:'Изберете канал – картината започва тук.',via:'Излъчване на живо: {n} · официален YouTube канал на медията',chs:'Канали',tv:'Телевизия на живо',yt:'При пускане видеото се зарежда от YouTube (Google).',big:'По-голямо',tvx:'Затвори',lf:'Музика от laut.fm – отваря се в нов прозорец.',tag:'Новини · Музика · Свят',news:'Новини TWN',nd:'Водещите новини за 3 минути',mus:'Музикални канали',soon:'Скоро',p:'В отделен прозорец',ph:'Продължава, докато четете.',a:'Слушай статията',s:'Спри четенето',ai:'Новините са озвучени с глас, генериран от изкуствен интелект (ElevenLabs), по проверени материали на редакцията на TWN.',none:'Следващото издание излиза утре сутринта.',x:'Затвори',en:'на английски',dev:'Чете гласът на вашето устройство.',now:'Сега звучи',vol:'Сила на звука',play:'Пусни',pause:'Пауза',live:'НА ЖИВО',old:'Предишни издания'},
en:{r:'TERRA WORLD RADIO',tvb:'TERRA WORLD TV',tvtag:'Live news from around the world',pick:'Choose a channel – the live picture starts here.',via:'Livestream: {n} · the broadcaster’s official YouTube channel',chs:'Channels',tv:'Live TV',yt:'Playing loads the video from YouTube (Google).',big:'Larger',tvx:'Close TV',lf:'Music from laut.fm – opens in a new window.',tag:'News · Music · World',news:'TWN News',nd:'The top stories in 3 minutes',mus:'Music channels',soon:'Soon',p:'Pop-out player',ph:'Keeps playing while you read.',a:'Listen to this article',s:'Stop reading',ai:'News read by an AI voice (ElevenLabs), based on stories checked by the TWN newsroom.',none:'The next edition will be out tomorrow morning.',x:'Close',en:'in English',dev:'Read aloud by your device’s voice.',now:'Now playing',vol:'Volume',play:'Play',pause:'Pause',live:'LIVE',old:'Earlier editions'},
tr:{r:'TERRA WORLD RADIO',tvb:'TERRA WORLD TV',tvtag:'Dünyadan canlı haberler',pick:'Bir kanal seçin – canlı yayın burada başlar.',via:'Canlı yayın: {n} · yayıncının resmî YouTube kanalı',chs:'Kanallar',tv:'Canlı TV',yt:'Oynatıldığında video YouTube’dan (Google) yüklenir.',big:'Büyüt',tvx:'TV’yi kapat',lf:'laut.fm’den müzik – yeni pencerede açılır.',tag:'Haberler · Müzik · Dünya',news:'TWN Haberleri',nd:'3 dakikada öne çıkan haberler',mus:'Müzik kanalları',soon:'Yakında',p:'Ayrı pencerede',ph:'Siz okurken çalmaya devam eder.',a:'Makaleyi dinle',s:'Okumayı durdur',ai:'Haberler, TWN editörlerinin doğruladığı metinlere dayanarak yapay zekâ sesiyle (ElevenLabs) okunur.',none:'Bir sonraki bülten yarın sabah yayımlanacak.',x:'Kapat',en:'İngilizce',dev:'Cihazınızın sesiyle okunur.',now:'Şimdi çalıyor',vol:'Ses',play:'Oynat',pause:'Duraklat',live:'CANLI',old:'Önceki bültenler'},
es:{r:'TERRA WORLD RADIO',tvb:'TERRA WORLD TV',tvtag:'Noticias en directo de todo el mundo',pick:'Elija un canal: la imagen en directo empieza aquí.',via:'Directo: {n} · canal oficial de YouTube de la emisora',chs:'Canales',tv:'TV en directo',yt:'Al reproducir, el vídeo se carga desde YouTube (Google).',big:'Ampliar',tvx:'Cerrar TV',lf:'Música de laut.fm – se abre en una ventana nueva.',tag:'Noticias · Música · Mundo',news:'Noticias TWN',nd:'Las noticias clave en 3 minutos',mus:'Canales de música',soon:'Pronto',p:'Ventana aparte',ph:'Sigue sonando mientras lee.',a:'Escuchar el artículo',s:'Detener la lectura',ai:'Noticias leídas con una voz de IA (ElevenLabs) a partir de textos verificados por la redacción de TWN.',none:'La próxima edición sale mañana por la mañana.',x:'Cerrar',en:'en inglés',dev:'Leído con la voz de su dispositivo.',now:'Sonando',vol:'Volumen',play:'Reproducir',pause:'Pausa',live:'EN VIVO',old:'Ediciones anteriores'}},
t=T[L]||T.en,AL={de:'de',bg:'bg',en:'en'},al=AL[L]||'en',isPop=document.body&&document.body.hasAttribute('data-radio'),popTV=/[?&]tv=1/.test(location.search);
function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
function el(h){var d=document.createElement('div');d.innerHTML=h.trim();return d.firstChild}
function ls(k,v){try{if(v===undefined)return localStorage.getItem(k);localStorage.setItem(k,v)}catch(e){return null}}
function day(s){try{return new Date(s+'T12:00:00').toLocaleDateString({bg:'bg-BG',de:'de-DE',tr:'tr-TR',es:'es-ES'}[L]||'en-GB',{weekday:'long',day:'numeric',month:'long'})}catch(e){return s}}
var NB=24,bars='';for(var i=0;i<NB;i++)bars+='<i style="--i:'+i+'"></i>';
var html='<section class="twr'+(isPop?' twr-pop':'')+'" aria-label="'+esc(t.r)+'"'+(isPop?'':' hidden')+'>'+
'<div class="twr-glow" aria-hidden="true"></div>'+
'<header class="twr-h"><div><b class="twr-brand">'+esc(t.r)+'</b><small>'+esc(t.tag)+'</small></div>'+(isPop?'':'<button type="button" class="twr-x" aria-label="'+esc(t.x)+'">×</button>')+'</header>'+
'<div class="twr-stage"><div class="twr-orb" aria-hidden="true"><span class="twr-ring"></span><span class="twr-core">📡</span></div>'+
'<div class="twr-np"><span class="twr-live"><i></i>'+esc(t.now)+'</span><b class="twr-title">'+esc(t.news)+'</b><span class="twr-sub">'+esc(t.nd)+'</span></div></div>'+
'<div class="twr-viz" aria-hidden="true">'+bars+'</div>'+
'<div class="twr-ctl"><button type="button" class="twr-prev" aria-label="◀">⏮</button><button type="button" class="twr-play" aria-label="'+esc(t.play)+'">▶</button><button type="button" class="twr-next" aria-label="▶">⏭</button>'+
'<label class="twr-vol"><span aria-hidden="true">🔊</span><input type="range" min="0" max="1" step="0.05" aria-label="'+esc(t.vol)+'"></label></div>'+
'<div class="twr-seek"><input type="range" min="0" max="1000" value="0" aria-label="seek"><small class="twr-time">0:00</small></div>'+
'<h3 class="twr-sh">'+esc(t.news)+'</h3><div class="twr-news"></div>'+
'<h3 class="twr-sh">'+esc(t.mus)+'</h3><div class="twr-ch"></div>'+
(isPop?'':'<button type="button" class="twr-popb">↗ '+esc(t.p)+' <small>'+esc(t.ph)+'</small></button>')+
'<p class="twr-ai">'+esc(t.ai)+'</p><audio preload="none"></audio></section>';
var V=el('<section class="twr twr-tvp'+(isPop?' twr-pop':'')+'" aria-label="'+esc(t.tvb)+'"'+(isPop?'':' hidden')+' style="--c1:#d4161c;--c2:#3b8bff"><div class="twr-glow" aria-hidden="true"></div>'+
'<header class="twr-h"><div><b class="twr-brand">'+esc(t.tvb)+'</b><small>'+esc(t.tvtag)+'</small></div>'+(isPop?'':'<button type="button" class="twr-x" aria-label="'+esc(t.x)+'">×</button>')+'</header>'+
'<div class="twr-scr"><div class="twr-vid"><p class="twr-pick"><span aria-hidden="true">📺</span>'+esc(t.pick)+'</p></div><div class="twr-scr-b"><small class="twr-via"></small><span><button type="button" class="twr-big">⤢ '+esc(t.big)+'</button> <button type="button" class="twr-tvx">× '+esc(t.tvx)+'</button></span></div></div>'+
'<h3 class="twr-sh">'+esc(t.chs)+'</h3><div class="twr-tv"></div>'+
(isPop?'':'<button type="button" class="twr-popb">↗ '+esc(t.p)+' <small>'+esc(t.ph)+'</small></button>')+'<p class="twr-ai">'+esc(t.yt)+'</p></section>');
var R=el(html),au=R.querySelector('audio'),list=[],cur=-1,ctx=null,an=null,raf=0,BAR=R.querySelectorAll('.twr-viz i');
function setVol(v){au.volume=v;R.querySelector('.twr-vol input').value=v;ls('twr-vol',String(v))}
setVol(parseFloat(ls('twr-vol')||'0.9'));R.querySelector('.twr-vol input').addEventListener('input',function(){setVol(parseFloat(this.value))});
function fmt(s){if(!isFinite(s))return t.live;s=Math.floor(s);return Math.floor(s/60)+':'+('0'+s%60).slice(-2)}
function wire(){R.classList.add('twr-fake')}   /* Balken per CSS: kein Web-Audio, damit fremde Streams nie stumm geschaltet werden */
function show(x){R.querySelector('.twr-title').textContent=x.title;R.querySelector('.twr-sub').textContent=x.sub;R.style.setProperty('--c1',x.c1);R.style.setProperty('--c2',x.c2);R.querySelector('.twr-core').textContent=x.emoji;
R.querySelector('.twr-seek').hidden=!!x.live;Array.prototype.forEach.call(R.querySelectorAll('[data-k]'),function(b){b.classList.toggle('on',b.getAttribute('data-k')===x.k)})}
function play(i,go){var x=list[i];if(!x||!x.src)return;cur=i;ls('twr-k',x.k);show(x);if(au.getAttribute('src')!==x.src){au.src=x.src}
if(go!==false){var p=au.play();if(p&&p.catch)p.catch(function(){});wire(x.local)}np()}
function np(){var x=list[cur];if(!x||!x.laut||!window.fetch)return;fetch('https://api.laut.fm/station/'+x.laut+'/current_song').then(function(r){return r.json()}).then(function(d){if(list[cur]===x&&d&&d.title)R.querySelector('.twr-sub').textContent=(d.artist&&d.artist.name?d.artist.name+' – ':'')+d.title}).catch(function(){})}
setInterval(function(){if(!au.paused)np()},30000);
au.addEventListener('play',function(){R.classList.add('twr-on');R.querySelector('.twr-play').textContent='❚❚';R.querySelector('.twr-play').setAttribute('aria-label',t.pause);if(btn)btn.classList.add('on')});
au.addEventListener('pause',function(){R.classList.remove('twr-on');R.querySelector('.twr-play').textContent='▶';R.querySelector('.twr-play').setAttribute('aria-label',t.play);if(btn)btn.classList.remove('on')});
au.addEventListener('timeupdate',function(){if(isFinite(au.duration)){R.querySelector('.twr-seek input').value=Math.round(au.currentTime/au.duration*1000);R.querySelector('.twr-time').textContent=fmt(au.currentTime)+' / '+fmt(au.duration)}});
R.querySelector('.twr-seek input').addEventListener('input',function(){if(isFinite(au.duration))au.currentTime=this.value/1000*au.duration});
R.querySelector('.twr-play').addEventListener('click',function(){if(cur<0){var j=list.findIndex(function(x){return x.src});if(j>=0)play(j);return}if(au.paused){au.play();wire(list[cur].local)}else au.pause()});
function step(d){var n=list.length;for(var k=1;k<=n;k++){var j=(cur+d*k+n*n)%n;if(list[j].src){play(j);return}}}
R.querySelector('.twr-prev').addEventListener('click',function(){step(-1)});R.querySelector('.twr-next').addEventListener('click',function(){step(1)});
function card(x,i){var b=el('<button type="button" class="twr-card'+(x.src?'':' soon')+'" data-k="'+esc(x.k)+'" style="--c1:'+esc(x.c1)+';--c2:'+esc(x.c2)+'"'+(x.src?'':' disabled')+'><span class="e">'+esc(x.emoji)+'</span><b>'+esc(x.name)+'</b><small>'+esc(x.sub)+'</small>'+(x.src?'':'<em>'+esc(t.soon)+'</em>')+'</button>');
if(x.src)b.addEventListener('click',function(){play(i)});return b}
function build(news,st){list=[];var nw=R.querySelector('.twr-news'),ch=R.querySelector('.twr-ch');nw.innerHTML='';ch.innerHTML='';
var its=(news.items||[]).filter(function(x){return x.lang===al}).sort(function(a,b){return a.date<b.date?1:-1});
if(!its.length){nw.innerHTML='<p class="twr-none">'+esc(t.none)+'</p>'}
its.slice(0,7).forEach(function(x,n){var o={k:'news-'+x.date,name:n?day(x.date):t.news,title:x.title+(al!==L?' ('+t.en+')':''),sub:day(x.date)+' · '+t.nd,emoji:'📡',c1:'#3b8bff',c2:'#d4161c',src:x.f,local:true};
var i=list.push(o)-1;if(n===0)nw.appendChild(card(Object.assign({},o,{name:t.news,sub:day(x.date)}),i));else{if(n===1)nw.appendChild(el('<details class="twr-old"><summary>'+esc(t.old)+'</summary></details>'));nw.lastChild.appendChild(card(Object.assign({},o,{sub:''}),i))}});
((st&&st.music)||[]).forEach(function(m){var ss=m.st||[];if(!ss.length)return;
var d=el('<details class="twr-cat" style="--c1:'+esc(m.c1)+';--c2:'+esc(m.c2)+'"><summary class="twr-card"><span class="e">'+esc(m.emoji||'🎶')+'</span><b>'+esc(m.name)+'</b><small>'+esc((m.g&&(m.g[L]||m.g.en))||'')+'</small><em>'+ss.length+'</em></summary><div class="twr-st">'+
ss.map(function(x){return '<a href="https://laut.fm/'+esc(x[1])+'" target="_blank" rel="noopener">▶ '+esc(x[0])+' <span aria-hidden="true">↗</span></a>'}).join('')+'</div></details>');
d.addEventListener('toggle',function(){if(d.open)Array.prototype.forEach.call(ch.querySelectorAll('details[open]'),function(o){if(o!==d)o.open=false})});
Array.prototype.forEach.call(d.querySelectorAll('a'),function(a){a.addEventListener('click',function(){au.pause()})});ch.appendChild(d)});
if(ch.childNodes.length)ch.insertAdjacentHTML('afterend','<p class="twr-lf">'+esc(t.lf)+'</p>');
var k=ls('twr-k'),j=-1;list.forEach(function(x,i){if(x.k===k&&x.src)j=i});if(j<0)j=list.findIndex(function(x){return x.src});if(j>=0){cur=j;show(list[j]);au.src=list[j].src}}
function load(){if(!window.fetch)return;Promise.all([fetch('/audio/news.json',{cache:'no-cache'}).then(function(r){return r.json()}).catch(function(){return{}}),fetch('/radio/stations.json',{cache:'no-cache'}).then(function(r){return r.json()}).catch(function(){return{}})]).then(function(a){build(a[0],a[1])})}
function loadTV(){if(window.fetch)fetch('/tv/channels.json',{cache:'no-cache'}).then(function(r){return r.json()}).then(tv).catch(function(){})}
function tvStop(){V.querySelector('.twr-vid').innerHTML='<p class="twr-pick"><span aria-hidden="true">📺</span>'+esc(t.pick)+'</p>';V.querySelector('.twr-via').textContent='';V.classList.remove('twr-on');Array.prototype.forEach.call(V.querySelectorAll('.twr-tv .twr-card'),function(b){b.classList.remove('on')})}
function tv(d){var box=V.querySelector('.twr-tv');box.innerHTML='';((d&&d.channels)||[]).forEach(function(c){if(!c.v)return;
var b=el('<button type="button" class="twr-card twr-tvc" style="--c1:'+esc(c.c1)+';--c2:'+esc(c.c2)+'"><span class="e">📺</span><b>'+esc(c.name)+'</b><small>'+esc(String(c.lang).toUpperCase())+'</small><em class="twr-lv">● LIVE</em></button>');
b.addEventListener('click',function(){au.pause();if(window.speechSynthesis)window.speechSynthesis.cancel();var sc=V.querySelector('.twr-scr');V.style.setProperty('--c1',c.c1);V.classList.add('twr-on');V.querySelector('.twr-via').textContent=t.via.replace('{n}',c.name);
sc.querySelector('.twr-vid').innerHTML='<iframe src="https://www.youtube-nocookie.com/embed/'+encodeURIComponent(c.v)+'?autoplay=1&rel=0&playsinline=1" title="'+esc(c.name)+' – Live" allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowfullscreen referrerpolicy="strict-origin-when-cross-origin"></iframe>';
Array.prototype.forEach.call(box.querySelectorAll('.twr-card'),function(x){x.classList.toggle('on',x===b)})});box.appendChild(b)});
}
V.querySelector('.twr-tvx').addEventListener('click',tvStop);V.querySelector('.twr-big').addEventListener('click',function(){V.classList.toggle('twr-wide')});au.addEventListener('play',tvStop);
var btn=null;
if(isPop){if(popTV){document.getElementById('radio').appendChild(V);loadTV();document.title=t.tvb}else{document.getElementById('radio').appendChild(R);load();document.title=t.r}return}
btn=el('<button type="button" class="twr-b" aria-expanded="false"><span aria-hidden="true">📻</span><span>Radio</span></button>');
var tb=el('<button type="button" class="twr-b twr-b2" aria-expanded="false"><span aria-hidden="true">📺</span><span>TV News</span></button>');
document.body.appendChild(tb);document.body.appendChild(btn);document.body.appendChild(V);document.body.appendChild(R);var loaded=false,tvl=false;
function sh(p,b,on){p.hidden=!on;b.setAttribute('aria-expanded',on?'true':'false')}
btn.addEventListener('click',function(){if(!loaded){load();loaded=true}var o=R.hidden;sh(R,btn,o);if(o)sh(V,tb,false)});
tb.addEventListener('click',function(){if(!tvl){loadTV();tvl=true}var o=V.hidden;sh(V,tb,o);if(o)sh(R,btn,false)});
R.querySelector('.twr-x').addEventListener('click',function(){au.pause();sh(R,btn,false)});V.querySelector('.twr-x').addEventListener('click',function(){tvStop();sh(V,tb,false)});   /* × beendet alles (Nedy 05.11.2026) */
V.querySelector('.twr-popb').addEventListener('click',function(){tvStop();window.open('/radio.html?l='+L+'&tv=1','twntv','width=720,height=640')});
R.querySelector('.twr-popb').addEventListener('click',function(){au.pause();window.open('/radio.html?l='+L,'twnradio','width=460,height=760')});
/* Artikel anhören – Gerätestimme (kostenlos) */
var art=document.querySelector('article.article'),S=window.speechSynthesis;if(!art||!S||!window.SpeechSynthesisUtterance)return;
var h1=art.querySelector('h1'),dek=art.querySelector('.dek');if(!h1)return;
var lb=el('<p class="tr-art"><button type="button">🔊 '+esc(t.a)+'</button><small>'+esc(t.dev)+'</small></p>'),on=false;(dek||h1).insertAdjacentElement('afterend',lb);
var lc={de:'de-DE',bg:'bg-BG',en:'en-GB',tr:'tr-TR',es:'es-ES'}[L]||L;
lb.querySelector('button').addEventListener('click',function(){var b=this;if(on){S.cancel();on=false;b.textContent='🔊 '+t.a;return}
au.pause();var parts=[h1.textContent];if(dek)parts.push(dek.textContent);Array.prototype.forEach.call(art.querySelectorAll('.body > p:not(.meta)'),function(p){parts.push(p.textContent)});
var vs=S.getVoices().filter(function(v){return v.lang&&v.lang.toLowerCase().indexOf(L)===0});S.cancel();
parts.forEach(function(x,i){var u=new SpeechSynthesisUtterance(x);u.lang=lc;if(vs.length)u.voice=vs[0];u.rate=1.02;if(i===parts.length-1)u.onend=function(){on=false;b.textContent='🔊 '+t.a};S.speak(u)});
on=true;b.textContent='⏹ '+t.s});
window.addEventListener('pagehide',function(){S.cancel()})})();
