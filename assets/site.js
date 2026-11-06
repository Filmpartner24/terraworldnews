(function(){
var store={get:function(k){try{return localStorage.getItem(k)}catch(e){return null}},set:function(k,v){try{localStorage.setItem(k,v)}catch(e){}}};
var orig=new Map();
var dsrc=document.querySelector('script[src*="assets/de.js"]');
var LANGS=['en','de','bg','es','pt','fr','it','ru','el','sr','ro','tr','ja','zh','ko','hi','ar'];
function url(l){return dsrc?dsrc.getAttribute('src').replace('de.js',l+'.js'):'/assets/'+l+'.js'}
var H=document.documentElement,PL=H.getAttribute('data-page-lang')||'en',BASE=H.getAttribute('data-base');
var URL_LANGS=['en','de','bg'];
function urlFor(l){return l==='en'?BASE:'/'+l+BASE}
function dicts(l){if(l===PL||l==='en')return[{},{}];var U=l.toUpperCase();return[window['NJC_'+U]||{},window['NJC_'+U+'B']||{}]}
var sel=document.querySelector('.langsel');
function apply(l){
  var d=dicts(l),T=d[0],B=d[1];
  document.documentElement.lang=l;document.documentElement.dir=(l==='ar')?'rtl':'ltr';
  document.querySelectorAll('[data-i18n]').forEach(function(el){
    if(!orig.has(el))orig.set(el,el.innerHTML);
    var k=el.getAttribute('data-i18n');
    el.innerHTML=T[k]?T[k]:orig.get(el);
  });
  document.querySelectorAll('template[data-lang-block="de"]').forEach(function(tp){
    var en=tp.previousElementSibling;if(!en||en.getAttribute('data-lang-block')!=='en')return;
    if(!tp._en)tp._en=en.innerHTML;
    var tr=tp.dataset.k?B[tp.dataset.k]:null;en.innerHTML=tr?tr:tp._en;en.setAttribute('lang',tr?l:PL);
  });
  if(sel){sel.value=l;var lc=document.querySelector('.langcode');if(lc)lc.textContent=l.toUpperCase();}
}
function setLang(l,explicit){
  if(LANGS.indexOf(l)<0)l='en';
  if(explicit)store.set('njc-lang',l);
  if(BASE&&URL_LANGS.indexOf(l)>=0&&l!==PL){location.href=urlFor(l)+location.hash;return}
  if(BASE&&URL_LANGS.indexOf(l)>=0&&l===PL){apply(PL);return}
  if(l!=='en'&&!window['NJC_'+l.toUpperCase()]){var sc=document.createElement('script');sc.src=url(l);sc.onload=function(){apply(l)};sc.onerror=function(){apply('en')};document.head.appendChild(sc);return}
  apply(l);
}
if(sel)sel.addEventListener('change',function(){setLang(sel.value,true)});
var nl=(navigator.language||'').slice(0,2).toLowerCase();
var saved=store.get('njc-lang');
if(saved){setLang(saved)}
else if(PL==='en'&&LANGS.indexOf(nl)>=0){setLang(nl)}
else{apply(PL)}

var nav=document.querySelector('.nav');
function upd(){nav.classList.toggle('solid',nav.dataset.solid==='always'||window.scrollY>window.innerHeight*0.35)}
addEventListener('scroll',upd,{passive:true});upd();
var b=nav.querySelector('.burger'),l=nav.querySelector('.links');
function close(){l.classList.remove('open');b.setAttribute('aria-expanded',false)}
b.addEventListener('click',function(){var o=l.classList.toggle('open');b.setAttribute('aria-expanded',o)});
l.querySelectorAll('a').forEach(function(a){a.addEventListener('click',close)});
document.addEventListener('click',function(e){if(l.classList.contains('open')&&!l.contains(e.target)&&!b.contains(e.target))close()});
document.addEventListener('keydown',function(e){if(e.key==='Escape'){close();lbClose()}});

document.querySelectorAll('.yt[data-yt]').forEach(function(t){
  t.addEventListener('click',function(){
    if(t.querySelector('iframe'))return;
    var f=document.createElement('iframe');
    f.src='https://www.youtube-nocookie.com/embed/'+t.dataset.yt+'?autoplay=1&rel=0';
    f.title=t.dataset.title||'YouTube';
    f.allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture';
    f.allowFullscreen=true;
    t.innerHTML='';t.appendChild(f);
  });
});

var hv=document.querySelector('.hero video');
if(hv){
  var reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
  var slow=navigator.connection&&(navigator.connection.saveData||/2g/.test(navigator.connection.effectiveType||''));
  var tg=document.querySelector('.vidtoggle');
  if(!reduce&&!slow){hv.src=hv.dataset.src;hv.play().catch(function(){});}
  else if(tg){tg.textContent='▶';}
  if(tg)tg.addEventListener('click',function(){
    if(!hv.src)hv.src=hv.dataset.src;
    if(hv.paused){hv.play();tg.textContent='❚❚';tg.setAttribute('aria-label','Pause')}else{hv.pause();tg.textContent='▶';tg.setAttribute('aria-label','Play')}
  });
}

var lb=document.querySelector('.lightbox');
function lbClose(){if(lb)lb.classList.remove('open')}
if(lb){
  document.querySelectorAll('.gallery figure').forEach(function(f){
    f.tabIndex=0;
    function open(){var i=f.querySelector('img');lb.querySelector('img').src=i.dataset.full||i.src;lb.querySelector('img').alt=i.alt;var c=f.querySelector('figcaption');lb.querySelector('p').textContent=c?c.textContent:'';lb.classList.add('open')}
    f.addEventListener('click',open);f.addEventListener('keydown',function(e){if(e.key==='Enter')open()});
  });
  lb.addEventListener('click',function(e){if(e.target===lb||e.target.tagName==='BUTTON')lbClose()});
}
document.querySelectorAll('audio').forEach(function(a){a.addEventListener('play',function(){document.querySelectorAll('audio').forEach(function(o){if(o!==a)o.pause()})})});

document.querySelectorAll('.filters').forEach(function(f){
  var cards=document.querySelectorAll('.pcard[data-cats]');
  f.querySelectorAll('button').forEach(function(b){b.addEventListener('click',function(){
    var k=b.dataset.filter;f.querySelectorAll('button').forEach(function(x){x.setAttribute('aria-pressed',x===b)});
    cards.forEach(function(c){c.hidden=!(k==='all'||c.dataset.cats.split(' ').indexOf(k)>=0)});
  })});
});
})();

/* TERRA WORLD NEWS bar (added 2026-11) */
(function(){
var T={"en": ["Media & Journalism", "International news portal · News. Facts. Context. · Bulgarian · German · English", "Editor-in-Chief", "Visit terraworldnews.com"], "de": ["Medien & Journalismus", "Internationales Nachrichtenportal · News. Facts. Context. · Bulgarisch · Deutsch · Englisch", "Chefredakteur", "Zu terraworldnews.com"], "bg": ["Медии и журналистика", "Международен новинарски портал · News. Facts. Context. · български · немски · английски", "Главен редактор", "Към terraworldnews.com"], "es": ["Medios y periodismo", "Portal internacional de noticias · News. Facts. Context. · búlgaro · alemán · inglés", "Redactor jefe", "Visitar terraworldnews.com"], "pt": ["Média e jornalismo", "Portal internacional de notícias · News. Facts. Context. · búlgaro · alemão · inglês", "Editor-chefe", "Visitar terraworldnews.com"], "fr": ["Médias & journalisme", "Portail d’information international · News. Facts. Context. · bulgare · allemand · anglais", "Rédacteur en chef", "Visiter terraworldnews.com"], "it": ["Media e giornalismo", "Portale di notizie internazionale · News. Facts. Context. · bulgaro · tedesco · inglese", "Caporedattore", "Visita terraworldnews.com"], "ru": ["Медиа и журналистика", "Международный новостной портал · News. Facts. Context. · болгарский · немецкий · английский", "Главный редактор", "Перейти на terraworldnews.com"], "el": ["Μέσα ενημέρωσης & δημοσιογραφία", "Διεθνής ειδησεογραφική πύλη · News. Facts. Context. · βουλγαρικά · γερμανικά · αγγλικά", "Αρχισυντάκτης", "Επίσκεψη στο terraworldnews.com"], "sr": ["Mediji i novinarstvo", "Međunarodni informativni portal · News. Facts. Context. · bugarski · nemački · engleski", "Glavni urednik", "Posetite terraworldnews.com"], "ro": ["Media și jurnalism", "Portal internațional de știri · News. Facts. Context. · bulgară · germană · engleză", "Redactor-șef", "Vizitați terraworldnews.com"], "tr": ["Medya ve gazetecilik", "Uluslararası haber portalı · News. Facts. Context. · Bulgarca · Almanca · İngilizce", "Genel Yayın Yönetmeni", "terraworldnews.com’u ziyaret edin"], "ja": ["メディア・ジャーナリズム", "国際ニュースポータル · News. Facts. Context. · ブルガリア語 · ドイツ語 · 英語", "編集長", "terraworldnews.com へ"], "zh": ["媒体与新闻", "国际新闻门户 · News. Facts. Context. · 保加利亚语 · 德语 · 英语", "总编辑", "访问 terraworldnews.com"], "ko": ["미디어 · 저널리즘", "국제 뉴스 포털 · News. Facts. Context. · 불가리아어 · 독일어 · 영어", "편집장", "terraworldnews.com 방문"], "hi": ["मीडिया और पत्रकारिता", "अंतरराष्ट्रीय समाचार पोर्टल · News. Facts. Context. · बुल्गारियाई · जर्मन · अंग्रेज़ी", "प्रधान संपादक", "terraworldnews.com पर जाएँ"], "ar": ["الإعلام والصحافة", "بوابة إخبارية دولية · News. Facts. Context. · البلغارية · الألمانية · الإنجليزية", "رئيس التحرير", "زيارة terraworldnews.com"]};
function lang(){var l=(document.documentElement.lang||'en').slice(0,2);return T[l]?l:'en'}
function ensure(){
  if(document.querySelector('.twn-bar'))return;
  var g=document.querySelector('.cgroups');if(!g)return;
  var t=T[lang()];var d=document.createElement('div');d.innerHTML='<div class="cgroup twn-group"><h3 class="subtitle" data-twn="0">'+t[0]+'</h3><a class="twn-bar" href="https://terraworldnews.com/" rel="noopener" target="_blank"><span class="twn-logo"><img alt="TERRA WORLD NEWS" width="800" height="209" loading="lazy" src="https://terraworldnews.com/assets/terra-masthead5-800.webp" srcset="https://terraworldnews.com/assets/terra-masthead5-800.webp 800w, https://terraworldnews.com/assets/terra-masthead5-1600.webp 1600w" sizes="(max-width:700px) 80vw, 340px"/></span><span class="twn-txt"><span class="cname">TERRA WORLD NEWS</span><span class="csub" data-twn="1">'+t[1]+'</span><span class="role" data-twn="2">'+t[2]+'</span><span class="twn-cta" data-twn="3">'+t[3]+'</span></span><span aria-hidden="true" class="carrow">↗</span></a></div>';
  g.insertBefore(d.firstChild,g.firstChild);
}
function tr(){var t=T[lang()];document.querySelectorAll('[data-twn]').forEach(function(e){e.textContent=t[+e.getAttribute('data-twn')]})}
if(!document.getElementById('twn-css')&&!/twn-bar/.test([].map.call(document.styleSheets,function(s){try{return [].map.call(s.cssRules,function(r){return r.selectorText||''}).join()}catch(e){return ''}}).join())){var st=document.createElement('style');st.id='twn-css';st.textContent="\n/* TERRA WORLD NEWS bar */\n.twn-bar{position:relative;display:grid;grid-template-columns:minmax(220px,380px) 1fr;align-items:stretch;border:1px solid rgba(201,160,78,.45);background:linear-gradient(90deg,#0a1528,#03060d 70%);text-decoration:none;transition:border-color .3s,background .3s}\n.twn-bar:hover{border-color:var(--gold-hi,#e3c27a);background:linear-gradient(90deg,#0d1c35,#060c18 70%)}\n.twn-logo{display:flex;align-items:center;justify-content:center;background:#fff;padding:26px 30px;border-right:4px solid #d6262b}\n.twn-logo img{display:block;width:100%;max-width:320px;height:auto}\n.twn-txt{display:flex;flex-direction:column;justify-content:center;padding:30px 64px 32px 36px}\n.twn-txt .cname{font-size:1.9rem}\n.twn-txt .csub{display:block;margin:12px 0 0;color:#c9d1dd;font-size:.98rem;line-height:1.5}\n.twn-txt .role{display:block;margin:14px 0 0;font-size:.74rem;letter-spacing:.16em;text-transform:uppercase;color:var(--gold,#c9a04e)}\n.twn-cta{display:inline-block;align-self:flex-start;margin-top:18px;padding:9px 18px;border:1px solid #d6262b;color:#fff;font-size:.8rem;font-weight:600;letter-spacing:.12em;text-transform:uppercase;background:rgba(214,38,43,.18)}\n.twn-bar:hover .twn-cta{background:#d6262b}\n.twn-bar .carrow{position:absolute;top:24px;right:24px;color:var(--gold-hi,#e3c27a)}\n[dir=rtl] .twn-bar .carrow{right:auto;left:24px}\n[dir=rtl] .twn-logo{border-right:0;border-left:4px solid #d6262b}\n[dir=rtl] .twn-txt{padding:30px 36px 32px 64px}\n@media (max-width:760px){.twn-bar{grid-template-columns:1fr}.twn-logo{border-right:0;border-bottom:4px solid #d6262b;padding:22px}.twn-txt{padding:24px 22px 28px}.twn-txt .cname{font-size:1.5rem}[dir=rtl] .twn-logo{border-left:0}.twn-bar .carrow{display:none}}\n";document.head.appendChild(st)}
ensure();tr();
new MutationObserver(tr).observe(document.documentElement,{attributes:true,attributeFilter:['lang']});
})();
