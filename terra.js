(function(){
  var lang=document.documentElement.lang||'bg';
  var loc={bg:'bg-BG',de:'de-DE'}[lang]||lang;
  function clocks(){document.querySelectorAll('[data-tz]').forEach(function(b){try{b.textContent=new Intl.DateTimeFormat(loc,{hour:'2-digit',minute:'2-digit',timeZone:b.dataset.tz}).format(new Date())}catch(e){}})}
  clocks();setInterval(clocks,20000);
  var tk=document.getElementById('tick');
  if(tk){var tb=tk.closest('.ticker'),pb=tb.querySelector('.tk-pause');
    var setDur=function(){var w=tk.firstElementChild.getBoundingClientRect().width;tk.style.setProperty('--dur',Math.max(20,w/70)+'s')};
    setDur();window.addEventListener('resize',setDur);
    if(pb)pb.addEventListener('click',function(){var p=tb.classList.toggle('paused');pb.setAttribute('aria-pressed',p?'true':'false')});}
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

/* Wetter in der Kopfzeile */
(function(){var box=document.querySelector('.wx');if(!box||!window.fetch)return;
  function ico(s){s=s||'';if(/thunder/.test(s))return'\u26C8';if(/snow|sleet/.test(s))return'\u2744';if(/rain|shower|drizzle/.test(s))return'\u2602';if(/fog/.test(s))return'\u2248';if(/partly|fair/.test(s))return'\u26C5';if(/cloud/.test(s))return'\u2601';if(/clear/.test(s))return/night/.test(s)?'\u263E':'\u2600';return''}
  fetch('/api/weather').then(function(r){return r.json()}).then(function(d){d.forEach(function(w,i){var b=box.querySelector('[data-wx="'+i+'"] b');if(b&&w){b.textContent=w.t+'\u00B0';var c=ico(w.s);if(c){var i=document.createElement('i');i.className='wi';i.setAttribute('aria-hidden','true');i.textContent=c+'\uFE0E';b.prepend(i)}}})}).catch(function(){});
})();
