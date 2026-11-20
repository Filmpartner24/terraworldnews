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
        var host=el.closest('section')||el.parentNode;var r=host.getBoundingClientRect();
        if(r.bottom<0||r.top>vh)return;
        var c=(r.top+r.height/2-vh/2)*parseFloat(el.getAttribute('data-speed'));
        el.style.transform='translate3d(0,'+(-c).toFixed(1)+'px,0)';
      });ticking=false;
    }
    window.addEventListener('scroll',function(){if(!ticking){ticking=true;requestAnimationFrame(px)}},{passive:true});
    window.addEventListener('resize',px);px();
  }
})();
