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
