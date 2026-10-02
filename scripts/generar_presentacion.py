#!/usr/bin/env python3
"""Genera presentacion/presentacion.html con NextSlide (preset Data Story).

Embebe las figuras de resultados/figuras/ en base64 (HTML autocontenido),
incluye modo presentador (notas + timer) y JSON para export PPTX.
Uso: python3 scripts/generar_presentacion.py
"""
import base64
import os
import pathlib

SKILL = pathlib.Path.home() / ".config/opencode/skills/nextslide"
ROOT = pathlib.Path(__file__).resolve().parent.parent
FIG = ROOT / "resultados/figuras"
OUT = ROOT / "presentacion/presentacion.html"


def b64_img(name):
    data = (FIG / name).read_bytes()
    return "data:image/png;base64," + base64.b64encode(data).decode()


FIG_DDOS_FREQ = b64_img("fig_ddos_frecuencia.png")
FIG_SCAN_FREQ = b64_img("fig_scan_frecuencia.png")
FIG_SCATTER = b64_img("fig_scatter_est_exact.png")
FIG_HIST = b64_img("fig_error_hist.png")
FIG_DDOS_DELTA = b64_img("fig_ddos_delta.png")
FIG_SCAN_DELTA = b64_img("fig_scan_delta.png")
FIG_FRONTERA = b64_img("fig_frontera_mre_mem.png")

BASE_CSS = (SKILL / "viewport-base.css").read_text()

PRESET_CSS = """:root {
  --ns-bg: #ffffff;
  --ns-bg-alt: #f1f5f9;
  --ns-text: #1e293b;
  --ns-text-muted: #64748b;
  --ns-primary: #1e40af;
  --ns-secondary: #64748b;
  --ns-accent: #0891b2;
  --ns-font-heading: 'IBM Plex Serif', serif;
  --ns-font-body: 'IBM Plex Sans', sans-serif;
  --ns-font-mono: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace;
  --ns-heading-weight: 600;
  --ns-body-weight: 400;
  --ns-space-xs: 8px;
  --ns-space-sm: 16px;
  --ns-space-md: 24px;
  --ns-space-lg: 32px;
  --ns-space-xl: 48px;
  --ns-space-2xl: 64px;
  --ns-slide-padding: 48px 64px;
  --ns-border-radius: 6px;
}"""

ANIM_CSS = """[class*="animate-"] {
  opacity: 0;
  animation-duration: 500ms;
  animation-timing-function: cubic-bezier(0.16, 1, 0.3, 1);
  animation-fill-mode: forwards;
}
.slide.active [class*="animate-"] { animation-play-state: running; }
.slide:not(.active) [class*="animate-"] { animation-play-state: paused; opacity: 0; }
.animate-counter-up { opacity: 1; }
@keyframes ns-fade-up { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
.animate-fade-up { animation-name: ns-fade-up; }
@keyframes ns-fade-in { from { opacity: 0; } to { opacity: 1; } }
.animate-fade-in { animation-name: ns-fade-in; }
@keyframes ns-scale-up { from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); } }
.animate-scale-up { animation-name: ns-scale-up; }
.delay-100 { animation-delay: 100ms; }
.delay-200 { animation-delay: 200ms; }
.delay-300 { animation-delay: 300ms; }
.delay-400 { animation-delay: 400ms; }
.delay-500 { animation-delay: 500ms; }
.delay-600 { animation-delay: 600ms; }
.duration-fast { animation-duration: 300ms; }
.duration-slow { animation-duration: 800ms; }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; transition-duration: 0.01ms !important; }
  [class*="animate-"] { opacity: 1 !important; transform: none !important; filter: none !important; }
}"""

EXTRA_CSS = """.fig-slide .slide-content { padding-top: 40px; }
.fig-slide h1 { font-size: 34px; margin-bottom: 10px; }
.fig-slide h2 { font-size: 24px; margin-bottom: 6px; }
.fig-slide .fig-caption { margin-top: 12px; font-size: 18px; color: var(--ns-text-muted); text-align: center; max-width: 85%; align-self: center; }
.ns-fig { flex: 1; min-height: 0; display: flex; align-items: center; justify-content: center; gap: 20px; }
.ns-fig img { max-width: 100%; max-height: 100%; object-fit: contain; border-radius: 6px; }
.ns-fig img.wide { max-height: 82%; }
.ns-fig .pair { display: flex; gap: 16px; height: 100%; align-items: center; justify-content: center; }
.ns-fig .pair img { max-height: 100%; max-width: 49%; }
.kpis { display: flex; gap: 24px; justify-content: center; margin-top: 24px; }
.kpi { background: var(--ns-bg-alt); border-radius: 8px; padding: 16px 28px; text-align: center; }
.kpi .n { font-family: var(--ns-font-heading); font-size: 40px; font-weight: 600; color: var(--ns-primary); }
.kpi .l { font-size: 15px; color: var(--ns-text-muted); }
.eq { font-family: var(--ns-font-mono); font-size: 26px; color: var(--ns-primary); background: var(--ns-bg-alt); border-radius: 8px; padding: 14px 24px; display: inline-block; margin: 12px 0; }
.ring { display: flex; align-items: center; gap: 12px; margin-top: 20px; flex-wrap: wrap; }
.ring .slot { width: 118px; height: 74px; border-radius: 8px; background: var(--ns-bg-alt); border: 2px solid var(--ns-primary); display: flex; align-items: center; justify-content: center; font-family: var(--ns-font-mono); font-size: 15px; }
.ring .slot.exp { border-color: var(--ns-accent); color: var(--ns-accent); font-weight: 600; }
.ring .slot.new { border-color: var(--ns-accent); background: #ecfeff; color: #0e7490; font-weight: 600; }
.ring .agg { width: 150px; height: 74px; border-radius: 8px; background: var(--ns-primary); color: #fff; display: flex; align-items: center; justify-content: center; font-family: var(--ns-font-mono); font-size: 15px; font-weight: 600; }
.ring .arrow { font-size: 24px; color: var(--ns-primary); }
.ns-col h3 { font-size: 22px; margin-bottom: 10px; }
.ns-col p, .ns-compare-card p { font-size: 18px; }
.ns-bullets li { font-size: 20px; }
.mono-tag { font-family: var(--ns-font-mono); font-size: 18px; background: var(--ns-bg-alt); padding: 2px 8px; border-radius: 4px; }
.title-note { font-size: 15px; color: var(--ns-text-muted); }
.thanks-note { font-size: 18px; color: var(--ns-text-muted); }
[data-layout="content"] .slide-content,
[data-layout="bullets"] .slide-content,
[data-layout="two-column"] .slide-content,
[data-layout="comparison"] .slide-content { justify-content: center; }
[data-layout="content"] .slide-content,
[data-layout="bullets"] .slide-content,
[data-layout="two-column"] .slide-content,
[data-layout="comparison"] .slide-content { padding-top: 0; }
.fig-slide .slide-content { justify-content: center; padding-top: 24px; }
.ns-col .ns-bullets { max-width: 100%; }
.ns-col .ns-bullets li { font-size: 18px; padding: 8px 0 8px 32px; }
.ns-col .ns-bullets li::before { top: 22px; }
.fig-caption { margin-top: 12px; font-size: 18px; color: var(--ns-text-muted); text-align: center; max-width: 85%; align-self: center; }
.ns-legend {
  margin-top: 16px;
  padding: 10px 18px;
  background: var(--ns-bg-alt);
  border-left: 3px solid var(--ns-primary);
  border-radius: 4px;
  font-family: var(--ns-font-body);
  font-size: 15px;
  color: var(--ns-text-muted);
  line-height: 1.55;
  max-width: 88%;
  align-self: center;
}
.ns-legend .lbl { color: var(--ns-primary); font-weight: 600; margin-right: 6px; }
.ns-legend code { font-family: var(--ns-font-mono); font-size: 14px; color: var(--ns-primary); background: rgba(30,64,175,0.06); padding: 1px 5px; border-radius: 3px; }
.ns-legend .sw { display: inline-block; width: 12px; height: 12px; border-radius: 3px; margin: 0 4px 0 2px; vertical-align: -1px; border: 1px solid rgba(0,0,0,0.15); }"""

JS = r"""(function () {
  'use strict';
  const SLIDE_WIDTH = 1920, SLIDE_HEIGHT = 1080;
  let currentSlide = 1, totalSlides = 0, isBlackScreen = false;
  const deck = document.querySelector('.ns-deck');
  const slides = document.querySelectorAll('.slide');
  const progressBar = document.querySelector('.ns-progress-bar');
  const counterCurrent = document.querySelector('.ns-current');
  const counterTotal = document.querySelector('.ns-total');
  const navPrev = document.querySelector('.ns-nav-prev');
  const navNext = document.querySelector('.ns-nav-next');
  totalSlides = slides.length;
  function updateScale() {
    const scale = Math.min(window.innerWidth / SLIDE_WIDTH, window.innerHeight / SLIDE_HEIGHT);
    document.documentElement.style.setProperty('--ns-scale', scale);
  }
  let resizeTimer;
  window.addEventListener('resize', function () { clearTimeout(resizeTimer); resizeTimer = setTimeout(updateScale, 100); });
  updateScale();
  function goToSlide(n) {
    n = Math.max(1, Math.min(n, totalSlides));
    const prev = document.querySelector('.slide.active');
    if (prev) { prev.classList.remove('active'); resetAnimations(prev); }
    currentSlide = n;
    const target = document.querySelector('[data-slide="' + n + '"]');
    if (target) { target.classList.add('active'); triggerAnimations(target); runCounterAnimations(target); }
    updateProgressBar(); updateCounter(); updateHash(); syncPresenter();
  }
  function nextSlide() { if (currentSlide < totalSlides) goToSlide(currentSlide + 1); }
  function prevSlide() { if (currentSlide > 1) goToSlide(currentSlide - 1); }
  function updateProgressBar() { if (progressBar) progressBar.style.width = (currentSlide / totalSlides) * 100 + '%'; }
  function updateCounter() { if (counterCurrent) counterCurrent.textContent = currentSlide; if (counterTotal) counterTotal.textContent = totalSlides; }
  function updateHash() { history.replaceState(null, '', '#slide-' + currentSlide); }
  function readHash() { const m = window.location.hash.match(/^#slide-(\d+)$/); if (m) { const n = parseInt(m[1], 10); if (n >= 1 && n <= totalSlides) return n; } return 1; }
  window.addEventListener('hashchange', function () { const n = readHash(); if (n !== currentSlide) goToSlide(n); });
  function triggerAnimations(slide) {
    const animated = slide.querySelectorAll('[class*="animate-"]');
    animated.forEach(function (el) {
      const classes = Array.from(el.classList);
      const animClass = classes.find(function (c) { return c.startsWith('animate-'); });
      if (animClass && animClass !== 'animate-counter-up') {
        el.classList.remove(animClass); void el.offsetWidth; el.classList.add(animClass);
      }
    });
  }
  function resetAnimations(slide) { slide.querySelectorAll('[class*="animate-"]').forEach(function (el) { el.style.opacity = '0'; }); }
  function runCounterAnimations(slide) {
    const counters = slide.querySelectorAll('.animate-counter-up');
    counters.forEach(function (el) {
      const target = parseFloat(el.getAttribute('data-target'));
      if (isNaN(target)) return;
      const duration = 1500, startTime = performance.now();
      const isFloat = target % 1 !== 0;
      const prefix = el.textContent.match(/^[^0-9]*/)[0] || '';
      const suffix = el.textContent.match(/[^0-9]*$/)[0] || '';
      function tick(now) {
        const p = Math.min((now - startTime) / duration, 1);
        const eased = 1 - Math.pow(1 - p, 3);
        const value = eased * target;
        if (isFloat) el.textContent = prefix + value.toFixed(1) + suffix;
        else el.textContent = prefix + Math.round(value) + suffix;
        if (p < 1) requestAnimationFrame(tick); else el.textContent = prefix + target + suffix;
      }
      requestAnimationFrame(tick);
    });
  }
  document.addEventListener('keydown', function (e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    switch (e.key) {
      case 'ArrowRight': case 'ArrowDown': case 'PageDown': case ' ':
        e.preventDefault(); nextSlide(); break;
      case 'ArrowLeft': case 'ArrowUp': case 'PageUp':
        e.preventDefault(); prevSlide(); break;
      case 'Home': e.preventDefault(); goToSlide(1); break;
      case 'End': e.preventDefault(); goToSlide(totalSlides); break;
      case 'f': case 'F': e.preventDefault(); toggleFullscreen(); break;
      case 'p': case 'P': e.preventDefault(); openPresenterWindow(); break;
      case 'b': case 'B': case '.': e.preventDefault(); toggleBlackScreen(); break;
      case 'Escape': if (document.fullscreenElement) document.exitFullscreen(); break;
      default:
        if (e.key >= '1' && e.key <= '9') { const n = parseInt(e.key, 10); if (n <= totalSlides) { e.preventDefault(); goToSlide(n); } }
    }
  });
  let touchStartX = 0, touchStartY = 0;
  document.addEventListener('touchstart', function (e) { touchStartX = e.changedTouches[0].clientX; touchStartY = e.changedTouches[0].clientY; }, { passive: true });
  document.addEventListener('touchend', function (e) {
    const dx = e.changedTouches[0].clientX - touchStartX, dy = e.changedTouches[0].clientY - touchStartY;
    if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) { if (dx < 0) nextSlide(); else prevSlide(); }
  }, { passive: true });
  if (navPrev) navPrev.addEventListener('click', prevSlide);
  if (navNext) navNext.addEventListener('click', nextSlide);
  function toggleFullscreen() { if (!document.fullscreenElement) document.documentElement.requestFullscreen().catch(function () {}); else document.exitFullscreen(); }
  document.addEventListener('fullscreenchange', function () { setTimeout(updateScale, 100); });
  function toggleBlackScreen() { isBlackScreen = !isBlackScreen; document.body.classList.toggle('black-screen', isBlackScreen); if (presenterChannel) presenterChannel.postMessage({ type: 'black-screen', active: isBlackScreen }); }
  let presenterChannel = null;
  try {
    presenterChannel = new BroadcastChannel('nextslide-presenter');
    presenterChannel.onmessage = function (event) { if (event.data.type === 'navigate') goToSlide(event.data.slide); };
  } catch (e) {}
  function syncPresenter() { if (!presenterChannel) return; presenterChannel.postMessage({ type: 'slide-change', slide: currentSlide, total: totalSlides, notes: getNotesForSlide(currentSlide) }); }
  function getNotesForSlide(n) { const slide = document.querySelector('[data-slide="' + n + '"]'); if (!slide) return ''; const notes = slide.querySelector('.notes'); return notes ? notes.textContent.trim() : ''; }
  function openPresenterWindow() {
    const title = document.title || 'Presentation';
    const pw = window.open('', 'nextslide-presenter', 'width=1200,height=800,menubar=no,toolbar=no,location=no,status=no');
    if (!pw) { alert('Popup blocked. Allow popups and try again.'); return; }
    pw.document.write(generatePresenterHTML(title)); pw.document.close();
    setTimeout(function () { if (presenterChannel) presenterChannel.postMessage({ type: 'init', slide: currentSlide, total: totalSlides, notes: getNotesForSlide(currentSlide) }); }, 500);
  }
  function generatePresenterHTML(title) {
    return '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Presenter - ' + title + '</title><style>' +
      '*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#1a1a2e;color:#e0e0e0;height:100vh;overflow:hidden}' +
      '.p-layout{display:grid;grid-template-columns:2fr 1fr;grid-template-rows:1fr auto;height:100vh;gap:12px;padding:12px}' +
      '.p-current{background:#000;border-radius:8px;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden}' +
      '.p-current-label,.p-next-label{position:absolute;top:8px;left:12px;font-size:11px;color:rgba(255,255,255,.4);text-transform:uppercase;letter-spacing:.1em}' +
      '.p-right{display:flex;flex-direction:column;gap:12px}' +
      '.p-next{background:#000;border-radius:8px;flex:0 0 180px;display:flex;align-items:center;justify-content:center;position:relative;overflow:hidden}' +
      '.p-notes{flex:1;background:#16213e;border-radius:8px;padding:16px;overflow-y:auto}' +
      '.p-notes h3{font-size:11px;text-transform:uppercase;letter-spacing:.1em;color:rgba(255,255,255,.4);margin-bottom:12px}' +
      '.p-notes-content{font-size:18px;line-height:1.6;white-space:pre-wrap}' +
      '.p-bar{grid-column:1/-1;display:flex;justify-content:space-between;align-items:center;padding:8px 16px;background:#16213e;border-radius:8px}' +
      '.p-timer{font-size:32px;font-weight:700;font-variant-numeric:tabular-nums;color:#60a5fa}' +
      '.p-clock{font-size:16px;color:rgba(255,255,255,.4);margin-left:16px}' +
      '.p-counter{font-size:24px;font-weight:600;color:rgba(255,255,255,.6)}' +
      '.p-controls{display:flex;gap:8px}.p-controls button{background:rgba(255,255,255,.1);border:none;color:#fff;padding:8px 16px;border-radius:6px;cursor:pointer;font-size:14px}' +
      '.p-controls button:hover{background:rgba(255,255,255,.2)}' +
      '.p-slide-num{font-size:48px;font-weight:700;color:rgba(255,255,255,.15)}' +
      '</style></head><body>' +
      '<div class="p-layout">' +
      '<div class="p-current"><span class="p-current-label">Current Slide</span><span class="p-slide-num" id="p-cur-num">1</span></div>' +
      '<div class="p-right"><div class="p-next"><span class="p-next-label">Next</span><span class="p-slide-num" id="p-next-num">2</span></div>' +
      '<div class="p-notes"><h3>Speaker Notes</h3><div class="p-notes-content" id="p-notes">No notes for this slide.</div></div></div>' +
      '<div class="p-bar"><div><span class="p-timer" id="p-timer">00:00:00</span><span class="p-clock" id="p-clock"></span></div>' +
      '<span class="p-counter" id="p-counter">1 / 1</span><div class="p-controls">' +
      '<button id="p-reset">Reset Timer</button><button id="p-prev">\u2190 Prev</button><button id="p-next-btn">Next \u2192</button>' +
      '</div></div></div><script>' +
      'var ch=new BroadcastChannel("nextslide-presenter");var cur=1,tot=1,start=Date.now();' +
      'ch.onmessage=function(e){if(e.data.type==="init"||e.data.type==="slide-change"){cur=e.data.slide;tot=e.data.total;' +
      'document.getElementById("p-cur-num").textContent=cur;document.getElementById("p-next-num").textContent=cur<tot?cur+1:"End";' +
      'document.getElementById("p-notes").textContent=e.data.notes||"No notes for this slide.";' +
      'document.getElementById("p-counter").textContent=cur+" / "+tot;}};' +
      'document.getElementById("p-prev").onclick=function(){ch.postMessage({type:"navigate",slide:cur-1})};' +
      'document.getElementById("p-next-btn").onclick=function(){ch.postMessage({type:"navigate",slide:cur+1})};' +
      'document.getElementById("p-reset").onclick=function(){start=Date.now()};' +
      'function tick(){var e=Date.now()-start,h=Math.floor(e/36e5),m=Math.floor(e%36e5/6e4),s=Math.floor(e%6e4/1e3);' +
      'document.getElementById("p-timer").textContent=String(h).padStart(2,"0")+":"+String(m).padStart(2,"0")+":"+String(s).padStart(2,"0");' +
      'var n=new Date;document.getElementById("p-clock").textContent=n.toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"});requestAnimationFrame(tick)}tick();' +
      'document.addEventListener("keydown",function(e){if(e.key==="ArrowRight"||e.key===" "){e.preventDefault();ch.postMessage({type:"navigate",slide:cur+1})}' +
      'if(e.key==="ArrowLeft"){e.preventDefault();ch.postMessage({type:"navigate",slide:cur-1})}});' +
      '<\/script></body></html>';
  }
  function init() { const startSlide = readHash(); if (counterTotal) counterTotal.textContent = totalSlides; goToSlide(startSlide); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();
})();"""

SLIDES = f"""<section class="slide" data-slide="1" data-layout="title">
  <div class="slide-content">
    <h1 class="animate-fade-up">Count-Min Sketch y CountSketch en ventanas deslizantes</h1>
    <p class="subtitle animate-fade-up delay-200">Detecci&oacute;n de ataques DDoS y Scan sobre tr&aacute;fico real (MAWI)</p>
    <p class="meta animate-fade-up delay-400">Joaqu&iacute;n Arriagada &middot; Benjamin D&iacute;az &middot; Vicente Hern&aacute;ndez &mdash; T&oacute;picos en Grandes Vol&uacute;menes de Datos &middot; 1 de octubre de 2026</p>
  </div>
  <aside class="notes">Saludo. Hoy presentamos c&oacute;mo mantenemos Count-Min Sketch y CountSketch sobre una ventana deslizante de 60 s usando la linealidad, y c&oacute;mo los usamos para detectar DDoS y Scan. 10 minutos.</aside>
</section>

<section class="slide" data-slide="2" data-layout="bullets">
  <div class="slide-content">
    <h1 class="animate-fade-up">Agenda</h1>
    <ul class="ns-bullets">
      <li class="animate-fade-up delay-100">Contexto y objetivo</li>
      <li class="animate-fade-up delay-200">Count-Min Sketch vs CountSketch</li>
      <li class="animate-fade-up delay-300">Ventana deslizante y linealidad</li>
      <li class="animate-fade-up delay-400">Resultados: DDoS y Scan (precisi&oacute;n, memoria, latencia)</li>
      <li class="animate-fade-up delay-500">Cambio de frecuencia &Delta;f y conclusiones</li>
    </ul>
  </div>
  <aside class="notes">Estructura de la charla: primero el problema, luego las dos estructuras, el mecanismo de ventana (lo central), los resultados de ambos ataques y el an&aacute;lisis de cambio de frecuencia.</aside>
</section>

<section class="slide" data-slide="3" data-layout="two-column">
  <div class="slide-content">
    <h1 class="animate-fade-up">Contexto y objetivo</h1>
    <div class="ns-columns">
      <div class="ns-col animate-fade-up delay-200">
        <h3>Problema</h3>
        <p>Tr&aacute;fico de red a <strong>137 mil pps</strong>: detectar <em>heavy hitters</em> en tiempo real con memoria sublineal.</p>
        <p style="margin-top:12px"><strong>DDoS</strong>: muchas fuentes &rarr; una v&iacute;ctima (clave: IP <em>destino</em>).</p>
        <p style="margin-top:12px"><strong>Scan</strong>: una fuente &rarr; muchos destinos (clave: IP <em>origen</em>).</p>
      </div>
      <div class="ns-col animate-fade-up delay-400">
        <h3>Enfoque</h3>
        <p>Sketches <strong>lineales</strong> sobre ventana deslizante de 60 s, evaluada cada 10 s.</p>
        <p style="margin-top:12px">Estimar frecuencia, decidir heavy hitter con &phi; = 0,01 y estimar el cambio &Delta;f entre ventanas.</p>
        <p style="margin-top:12px">Validar contra el conteo exacto (<span class="mono-tag">exact_hh</span>).</p>
      </div>
    </div>
    <p class="fig-caption animate-fade-up delay-500">Heavy hitter: f<sub>j</sub>(x) &ge; &lceil;&phi;&middot;N<sub>j</sub>&rceil; &nbsp;&middot;&nbsp; clave: IP <em>destino</em> (DDoS) / IP <em>origen</em> (Scan)</p>
  </div>
  <aside class="notes">El problema es compactar el conteo de frecuencias para detectar anomal&iacute;as. Definimos heavy hitter como f(x) >= ceil(0.01*N). La clave es destino en DDoS y origen en Scan.</aside>
</section>

<section class="slide" data-slide="4" data-layout="comparison">
  <div class="slide-content">
    <h1 class="animate-fade-up">Count-Min Sketch vs CountSketch</h1>
    <div class="ns-compare">
      <div class="ns-compare-card animate-scale-up delay-200">
        <h3>Count-Min Sketch</h3>
        <p>Actualiza <span class="mono-tag">+1</span> por fila.</p>
        <p>Estima con el <strong>m&iacute;nimo</strong> sobre d filas.</p>
        <p><strong>Sobreestima</strong>: las colisiones suman ruido positivo.</p>
        <p>Sesgo positivo creciente al reducir w.</p>
        <p class="title-note">d = 5 filas &middot; contadores sin signo</p>
      </div>
      <div class="ns-compare-card animate-scale-up delay-400">
        <h3>CountSketch</h3>
        <p>Actualiza <span class="mono-tag">&plusmn;1</span> (hash de signo).</p>
        <p>Estima con la <strong>mediana</strong> (signo corregido).</p>
        <p><strong>Insesgado</strong>: el signo cancela colisiones.</p>
        <p>La mediana filtra valores at&iacute;picos.</p>
        <p class="title-note">d = 5 filas &middot; contadores con signo</p>
      </div>
    </div>
  </div>
  <aside class="notes">Diferencias clave: CMS usa solo incrementos positivos y m&iacute;nimo (sobreestima); CS firma cada actualizaci&oacute;n con +/-1 y usa mediana (insesgado). Esto explica todo lo que viene.</aside>
</section>

<section class="slide" data-slide="5" data-layout="content">
  <div class="slide-content">
    <h1 class="animate-fade-up">Ventana deslizante y linealidad</h1>
    <p class="animate-fade-up delay-100">Anillo de <strong>m = 6</strong> sub-sketchs de 10 s + un agregado A. Por linealidad, la ventana activa es la suma de sus sub-sketchs:</p>
    <div class="eq animate-fade-up delay-200">A &nbsp;&larr;&nbsp; A &minus; S<sub>expira</sub> + S<sub>entra</sub></div>
    <div class="ring animate-fade-in delay-300">
      <div class="slot exp">S<sub>1</sub> expira</div>
      <div class="arrow">&rarr;</div>
      <div class="slot">S<sub>2</sub></div>
      <div class="slot">S<sub>3</sub></div>
      <div class="slot">S<sub>4</sub></div>
      <div class="slot">S<sub>5</sub></div>
      <div class="slot">S<sub>6</sub></div>
      <div class="arrow">&rarr;</div>
      <div class="agg">A = &Sigma; S<sub>q</sub></div>
    </div>
    <p class="animate-fade-up delay-400" style="margin-top:16px">Costo por rotaci&oacute;n <strong>O(d&middot;w)</strong>, <strong>independiente de N<sub>j</sub></strong>. Siete arreglos d&times;w por tipo (6 + agregado).</p>
    <div class="ns-legend animate-fade-in delay-500"><span class="lbl">Notaci&oacute;n:</span><code>S<sub>q</sub></code> sub-sketch de la subventana q &middot; <code>A</code> agregado de la ventana &middot; <code>m</code> = n&deg; de ranuras &middot; <code>N<sub>j</sub></code> paquetes de la ventana activa</div>
  </div>
  <aside class="notes">El coraz&oacute;n de la tarea. No se reprocesan los 60 s: al avanzar se resta la subventana que expira y se suma la nueva. La ranura del anillo se reutiliza. La actualizaci&oacute;n toca solo 2*d*w contadores.</aside>
</section>

<section class="slide" data-slide="6" data-layout="bullets">
  <div class="slide-content">
    <h1 class="animate-fade-up">Alineaci&oacute;n y verificaci&oacute;n</h1>
    <ul class="ns-bullets">
      <li class="animate-fade-up delay-100">Subventana q cubre (t<sub>0</sub>+(q&minus;1)p, t<sub>0</sub>+qp]; ranura (q&minus;1) mod 6.</li>
      <li class="animate-fade-up delay-200">Evaluaciones en &tau;<sub>j</sub> = t<sub>0</sub>+60+j&middot;10: primero se expira, luego se carga.</li>
      <li class="animate-fade-up delay-300">Anillo escalar de contadores para N<sub>j</sub> exacto.</li>
      <li class="animate-fade-up delay-400">Verificaci&oacute;n contra <span class="mono-tag">exact_hh</span>: N<sub>j</sub> id&eacute;ntico en las 8 corridas (traza base y ataques, 3 anchos).</li>
    </ul>
    <div class="kpis animate-fade-in delay-500">
      <div class="kpi"><div class="n animate-counter-up" data-target="84">0</div><div class="l">ventanas evaluadas</div></div>
      <div class="kpi"><div class="n">84</div><div class="l">id&eacute;nticas (100%)</div></div>
    </div>
    <div class="ns-legend animate-fade-in delay-500"><span class="lbl">Notaci&oacute;n:</span><code>&tau;<sub>j</sub></code> instante de evaluaci&oacute;n &middot; <code>q</code> subventana (ranura <code>(q&minus;1) mod 6</code>) &middot; <code>t<sub>0</sub></code> primer paquete &middot; <code>N<sub>j</sub></code> conteo exacto del anillo escalar</div>
  </div>
  <aside class="notes">La alineaci&oacute;n es cr&iacute;tica: un desfase de una subventana no se nota casi nunca y aparece justo al salir el ataque. El anillo escalar N_j debe coincidir exactamente con exact_hh; fue la primera verificaci&oacute;n.</aside>
</section>

<section class="slide" data-slide="7" data-layout="two-column">
  <div class="slide-content">
    <h1 class="animate-fade-up">Datos y configuraci&oacute;n</h1>
    <div class="ns-columns">
      <div class="ns-col animate-fade-up delay-200">
        <h3>DDoS</h3>
        <p><span class="mono-tag">pps=10 000</span> &middot; 4 000 fuentes</p>
        <p>V&iacute;ctima 163.210.30.13 &middot; clave <em>dst</em></p>
      </div>
      <div class="ns-col animate-fade-up delay-400">
        <h3>Scan</h3>
        <p><span class="mono-tag">pps=8 000</span> &middot; 60 000 destinos</p>
        <p>Atacante 198.18.0.7 &middot; clave <em>src</em></p>
      </div>
    </div>
    <p class="animate-fade-up delay-500" style="margin-top:20px">Traza MAWI 2018-12-03 (123,4 M paquetes, ~900 s) &middot; W=60, p=10, m=6 &middot; d=5, w &isin; {{256, 1024, 4096}} &middot; &phi;=0,01 &middot; semilla 42 &middot; ataque en [300, 330] s.</p>
    <div class="ns-legend animate-fade-in delay-500"><span class="lbl">Par&aacute;metros:</span><code>W</code> ancho de la ventana (60 s) &middot; <code>p</code> paso (10 s) &middot; <code>m = W/p</code> subventanas &middot; <code>d</code> filas del sketch &middot; <code>w</code> contadores por fila &middot; <code>&phi;</code> umbral heavy hitter</div>
  </div>
  <aside class="notes">Par&aacute;metros fijos del enunciado. El ataque va de t=300 a 330 s con seed 42. Se eval&uacute;a la calidad del estimador y la latencia, no la enumeraci&oacute;n de claves.</aside>
</section>

<section class="slide fig-slide" data-slide="8" data-layout="fig">
  <div class="slide-content">
    <h1 class="animate-fade-up">DDoS: la v&iacute;ctima como heavy hitter</h1>
    <div class="ns-fig animate-fade-in delay-200"><img class="wide" src="{FIG_DDOS_FREQ}" alt="DDoS frecuencia"></div>
    <p class="fig-caption animate-fade-up delay-300">Meseta de ~300k mientras el ataque est&aacute; en la ventana; la frecuencia "arrastra" 60 s. Latencia 10 s. MRE &le; 4,11% (CMS) y 0,16% (CS) con w=256.</p>
    <div class="ns-legend animate-fade-in delay-400"><span class="lbl">Leyenda:</span><span class="sw" style="background:#000"></span> exacto &middot; <span class="sw" style="background:#e41a1c"></span><span class="sw" style="background:#ff7f00"></span><span class="sw" style="background:#f0c000"></span> CMS (w=256/1024/4096) &middot; <span class="sw" style="background:#08519c"></span><span class="sw" style="background:#3182bd"></span><span class="sw" style="background:#6baed6"></span> CS &middot; <span class="sw" style="background:#c0c0c0"></span> ataque [300,330] s &middot; <span class="sw" style="border:1px dashed #777;background:none"></span> umbral T<sub>j</sub> &middot; <code>f<sub>j</sub>(x)</code> frecuencia por IP <em>destino</em></div>
  </div>
  <aside class="notes">Curva de la v&iacute;ctima por destino. Sube de ~90 a 300k, meseta de 4 evaluaciones (t=330-360) porque la ventana entera contiene el ataque, y baja gradual hasta t=390 (60 s despu&eacute;s del &uacute;ltimo paquete). Ambos sketches detectan en t=310, igual que exacto.</aside>
</section>

<section class="slide fig-slide" data-slide="9" data-layout="fig">
  <div class="slide-content">
    <h1 class="animate-fade-up">Scan: contraste desde IP de origen</h1>
    <div class="ns-fig animate-fade-in delay-200"><img class="wide" src="{FIG_SCAN_FREQ}" alt="Scan frecuencia"></div>
    <p class="fig-caption animate-fade-up delay-300">El atacante pasa de f&asymp;0 a ~80k pps. Latencia 20 s (CMS w=256 detecta 1 ventana antes: falso positivo esperado). MRE &le; 3,78%.</p>
    <div class="ns-legend animate-fade-in delay-400"><span class="lbl">Leyenda:</span><span class="sw" style="background:#000"></span> exacto &middot; <span class="sw" style="background:#e41a1c"></span><span class="sw" style="background:#ff7f00"></span><span class="sw" style="background:#f0c000"></span> CMS (w=256/1024/4096) &middot; <span class="sw" style="background:#08519c"></span><span class="sw" style="background:#3182bd"></span><span class="sw" style="background:#6baed6"></span> CS &middot; <span class="sw" style="background:#c0c0c0"></span> ataque &middot; <span class="sw" style="border:1px dashed #777;background:none"></span> umbral T<sub>j</sub> &middot; <code>f<sub>j</sub>(x)</code> frecuencia por IP <em>origen</em></div>
  </div>
  <aside class="notes">Aqu&iacute; el contraste es m&aacute;ximo porque la IP de origen del atacante casi no aparece antes. Con CMS y w=256 el sesgo positivo adelanta la detecci&oacute;n una ventana (latencia 10 vs 20 s): es el comportamiento esperado del m&iacute;nimo, no un error.</aside>
</section>

<section class="slide fig-slide" data-slide="10" data-layout="fig">
  <div class="slide-content">
    <h1 class="animate-fade-up">Comparaci&oacute;n: CMS sobreestima, CS insesgado</h1>
    <div class="ns-fig animate-fade-in delay-200">
      <div class="pair">
        <img src="{FIG_SCATTER}" alt="Scatter estimado vs exacto">
        <img src="{FIG_HIST}" alt="Histograma del error relativo">
      </div>
    </div>
    <p class="fig-caption animate-fade-up delay-300">19 claves por tipo, 84 ventanas: CMS queda sobre la diagonal (sesgo positivo); CS rodea la diagonal (mediana de error relativo &asymp; 0).</p>
    <div class="ns-legend animate-fade-in delay-400"><span class="lbl">Leyenda:</span><code>f<sub>j</sub>(x)</code> frecuencia en la ventana &middot; izquierda: estimado vs exacto (log-log) &middot; derecha: distribuci&oacute;n del error relativo con <code>f &ge; 1000</code> &middot; <span class="sw" style="background:#fdd0a2"></span><span class="sw" style="background:#fd8d3c"></span><span class="sw" style="background:#a63603"></span> CMS &middot; <span class="sw" style="background:#c6dbef"></span><span class="sw" style="background:#6baed6"></span><span class="sw" style="background:#08519c"></span> CS &middot; tono claro&rarr;oscuro = w creciente</div>
  </div>
  <aside class="notes">La evidencia de los estimadores: scatter log-log y distribuci&oacute;n del error relativo. Con f>=1000, la mediana del error de CMS en w=256 es +13% mientras CS queda centrada en 0.</aside>
</section>

<section class="slide fig-slide" data-slide="11" data-layout="fig">
  <div class="slide-content">
    <h1 class="animate-fade-up">Cambio de frecuencia &Delta;f<sub>j</sub></h1>
    <div class="ns-fig animate-fade-in delay-200">
      <div class="pair">
        <img src="{FIG_DDOS_DELTA}" alt="Delta DDoS">
        <img src="{FIG_SCAN_DELTA}" alt="Delta Scan">
      </div>
    </div>
    <p class="fig-caption animate-fade-up delay-300">Picos de +100k (DDoS) y +80k (Scan) al inicio y sim&eacute;tricos al salir la ventana. CountSketch con garant&iacute;as; CMS-mediana experimental comparable.</p>
    <div class="ns-legend animate-fade-in delay-400"><span class="lbl">Leyenda:</span><code>&Delta;f<sub>j</sub> = f<sub>j</sub> &minus; f<sub>j&minus;1</sub></code> cambio entre ventanas consecutivas (firmado) &middot; <span class="sw" style="background:#000"></span> exacto &middot; <span class="sw" style="background:#377eb8"></span> CountSketch &middot; <span class="sw" style="background:#e41a1c"></span> CMS-mediana &middot; <span class="sw" style="background:#c0c0c0"></span> ataque</div>
  </div>
  <aside class="notes">Sobre el vector firmado A_{{j-1}} - A_j: el ataque aparece como salto positivo (inicio) y negativo (fin), con &Delta;f ~ 0 en la meseta. CS usa su estimador habitual (mediana con signo); CMS usa mediana (experimental), porque el m&iacute;nimo no aplica a valores firmados.</aside>
</section>

<section class="slide" data-slide="12" data-layout="two-column">
  <div class="slide-content">
    <h1 class="animate-fade-up">Conclusiones</h1>
    <div class="ns-columns">
      <div class="ns-col animate-fade-up delay-200">
        <ul class="ns-bullets">
          <li class="animate-fade-up delay-100">Linealidad: ventana de 60 s con costo <strong>O(d&middot;w)</strong> por rotaci&oacute;n, independiente de N<sub>j</sub> (verificado 84/84).</li>
          <li class="animate-fade-up delay-200">CountSketch es <strong>m&aacute;s preciso</strong> a igual memoria y robusto a w peque&ntilde;o (insesgado).</li>
          <li class="animate-fade-up delay-300">Count-Min compite a w grande; su sesgo puede adelantar la detecci&oacute;n (FP reportado en Scan, w=256).</li>
          <li class="animate-fade-up delay-400"><strong>w = 1024</strong>: mejor equilibrio precisi&oacute;n-memoria (280 KiB, MRE &lt; 1%).</li>
          <li class="animate-fade-up delay-500">&Delta;f estimado sin reprocesar: CS con garant&iacute;as; CMS-mediana comparable en la pr&aacute;ctica.</li>
        </ul>
      </div>
      <div class="ns-col animate-fade-in delay-300" style="justify-content:center">
        <img src="{FIG_FRONTERA}" alt="Frontera precisión-memoria" style="max-width:100%; max-height:520px; object-fit:contain; border-radius:6px">
      </div>
    </div>
    <div class="ns-legend animate-fade-in delay-400"><span class="lbl">Leyenda:</span><code>mem = 7&middot;d&middot;w&middot;8 B</code> (6 sub-sketchs + agregado, int64) &middot; MRE sobre las ventanas del ataque &middot; ejes logar&iacute;tmicos &middot; <span class="sw" style="background:#d62728"></span> CMS &middot; <span class="sw" style="background:#1f77b4"></span> CS &middot; puntos = w &isin; {{256, 1024, 4096}}</div>
  </div>
  <aside class="notes">Resumen ejecutivo. La linealidad es lo que hace viable monitorear 137 kpps. El grafico de frontera muestra el tradeoff MRE-memoria: CS domina en ambos ataques y el MRE cae al crecer w.</aside>
</section>

<section class="slide" data-slide="13" data-layout="title">
  <div class="slide-content">
    <h1 class="animate-fade-up">&iexcl;Gracias!</h1>
    <p class="subtitle animate-fade-up delay-200">Preguntas</p>
    <p class="thanks-note animate-fade-up delay-400">Reproducibilidad: traza MAWI samplepoint-F 2018-12-03 (URL en el informe) &middot; semilla 42 &middot; c&oacute;digo y scripts en el repositorio.</p>
  </div>
  <aside class="notes">Cierre. Invitamos a preguntas sobre el mecanismo de ventana, la comparaci&oacute;n de estimadores o los resultados de los ataques. La semilla 42 y la URL de la traza garantizan reproducibilidad.</aside>
</section>"""

JSON_DATA = """{
  "meta": {
    "title": "Count-Min Sketch y CountSketch en ventanas deslizantes",
    "author": "Joaquín Arriagada · Benjamin Díaz · Vicente Hernández",
    "date": "2026-10-01",
    "theme": "data-story",
    "slideWidth": 13.333,
    "slideHeight": 7.5
  },
  "slides": [
    {"layout": "title", "background": {"color": "#ffffff"}, "elements": [
      {"type": "text", "content": "Count-Min Sketch y CountSketch en ventanas deslizantes", "role": "title", "position": {"x": "10%", "y": "30%", "w": "80%", "h": "25%"}, "style": {"fontSize": 40, "fontFace": "IBM Plex Serif", "bold": true, "color": "#1e293b", "align": "center"}},
      {"type": "text", "content": "Detección de ataques DDoS y Scan sobre tráfico real (MAWI)", "role": "subtitle", "position": {"x": "15%", "y": "55%", "w": "70%", "h": "10%"}, "style": {"fontSize": 22, "fontFace": "IBM Plex Sans", "color": "#64748b", "align": "center"}},
      {"type": "text", "content": "Joaquín Arriagada · Benjamin Díaz · Vicente Hernández", "role": "caption", "position": {"x": "15%", "y": "70%", "w": "70%", "h": "8%"}, "style": {"fontSize": 16, "fontFace": "IBM Plex Sans", "color": "#64748b", "align": "center"}}
    ], "notes": "Saludo e introducción."},
    {"layout": "bullets", "background": {"color": "#ffffff"}, "elements": [
      {"type": "text", "content": "Agenda", "role": "title", "position": {"x": "5%", "y": "8%", "w": "90%", "h": "12%"}, "style": {"fontSize": 36, "fontFace": "IBM Plex Serif", "bold": true, "color": "#1e293b"}},
      {"type": "text", "content": "Contexto y objetivo · CMS vs CS · Ventana deslizante y linealidad · Resultados DDoS/Scan · Δf y conclusiones", "role": "body", "position": {"x": "10%", "y": "30%", "w": "80%", "h": "50%"}, "style": {"fontSize": 22, "fontFace": "IBM Plex Sans", "color": "#1e293b"}}
    ], "notes": "Estructura de la charla."},
    {"layout": "two-column", "background": {"color": "#ffffff"}, "elements": [
      {"type": "text", "content": "Contexto y objetivo", "role": "title", "position": {"x": "5%", "y": "8%", "w": "90%", "h": "10%"}, "style": {"fontSize": 36, "fontFace": "IBM Plex Serif", "bold": true, "color": "#1e293b"}},
      {"type": "text", "content": "Tráfico a 137 kpps; heavy hitters con memoria sublineal. DDoS por destino, Scan por origen.", "role": "body", "position": {"x": "6%", "y": "22%", "w": "42%", "h": "60%"}, "style": {"fontSize": 20, "fontFace": "IBM Plex Sans", "color": "#1e293b"}},
      {"type": "text", "content": "Sketches lineales sobre ventana de 60 s; estimar frecuencia, HH con φ=0.01 y Δf.", "role": "body", "position": {"x": "52%", "y": "22%", "w": "42%", "h": "60%"}, "style": {"fontSize": 20, "fontFace": "IBM Plex Sans", "color": "#1e293b"}}
    ], "notes": "Problema y enfoque."},
    {"layout": "comparison", "background": {"color": "#ffffff"}, "elements": [
      {"type": "text", "content": "Count-Min Sketch vs CountSketch", "role": "title", "position": {"x": "5%", "y": "8%", "w": "90%", "h": "12%"}, "style": {"fontSize": 36, "fontFace": "IBM Plex Serif", "bold": true, "color": "#1e293b", "align": "center"}},
      {"type": "text", "content": "CMS: +1 por fila, estima con mínimo, sobreestima.", "role": "body", "position": {"x": "6%", "y": "25%", "w": "42%", "h": "50%"}, "style": {"fontSize": 20, "fontFace": "IBM Plex Sans", "color": "#1e293b"}},
      {"type": "text", "content": "CS: ±1 con signo, estima con mediana, insesgado.", "role": "body", "position": {"x": "52%", "y": "25%", "w": "42%", "h": "50%"}, "style": {"fontSize": 20, "fontFace": "IBM Plex Sans", "color": "#1e293b"}}
    ], "notes": "Diferencia de estimadores."},
    {"layout": "content", "background": {"color": "#ffffff"}, "elements": [
      {"type": "text", "content": "Ventana deslizante y linealidad", "role": "title", "position": {"x": "5%", "y": "8%", "w": "90%", "h": "10%"}, "style": {"fontSize": 36, "fontFace": "IBM Plex Serif", "bold": true, "color": "#1e293b"}},
      {"type": "text", "content": "Anillo de 6 sub-sketchs; A ← A − S_exp + S_entra; costo O(d·w) independiente de N_j.", "role": "body", "position": {"x": "8%", "y": "25%", "w": "84%", "h": "40%"}, "style": {"fontSize": 24, "fontFace": "IBM Plex Sans", "color": "#1e293b"}}
    ], "notes": "El mecanismo central."},
    {"layout": "bullets", "background": {"color": "#ffffff"}, "elements": [
      {"type": "text", "content": "Alineación y verificación", "role": "title", "position": {"x": "5%", "y": "8%", "w": "90%", "h": "12%"}, "style": {"fontSize": 36, "fontFace": "IBM Plex Serif", "bold": true, "color": "#1e293b"}},
      {"type": "text", "content": "84/84 ventanas idénticas contra exact_hh (traza base y ataques, 3 anchos).", "role": "body", "position": {"x": "10%", "y": "30%", "w": "80%", "h": "40%"}, "style": {"fontSize": 22, "fontFace": "IBM Plex Sans", "color": "#1e293b"}}
    ], "notes": "Gate de verificación."},
    {"layout": "two-column", "background": {"color": "#ffffff"}, "elements": [
      {"type": "text", "content": "Datos y configuración", "role": "title", "position": {"x": "5%", "y": "8%", "w": "90%", "h": "10%"}, "style": {"fontSize": 36, "fontFace": "IBM Plex Serif", "bold": true, "color": "#1e293b"}},
      {"type": "text", "content": "DDoS: pps=10 000, 4 000 fuentes, víctima 163.210.30.13, clave dst.", "role": "body", "position": {"x": "6%", "y": "22%", "w": "42%", "h": "30%"}, "style": {"fontSize": 20, "fontFace": "IBM Plex Sans", "color": "#1e293b"}},
      {"type": "text", "content": "Scan: pps=8 000, 60 000 destinos, atacante 198.18.0.7, clave src.", "role": "body", "position": {"x": "52%", "y": "22%", "w": "42%", "h": "30%"}, "style": {"fontSize": 20, "fontFace": "IBM Plex Sans", "color": "#1e293b"}},
      {"type": "text", "content": "W=60, p=10, m=6, d=5, w∈{256,1024,4096}, φ=0.01, seed 42.", "role": "body", "position": {"x": "8%", "y": "62%", "w": "84%", "h": "20%"}, "style": {"fontSize": 20, "fontFace": "IBM Plex Sans", "color": "#1e293b"}}
    ], "notes": "Parámetros."},
    {"layout": "fig", "background": {"color": "#ffffff"}, "elements": [
      {"type": "text", "content": "DDoS: la víctima como heavy hitter", "role": "title", "position": {"x": "5%", "y": "5%", "w": "90%", "h": "10%"}, "style": {"fontSize": 32, "fontFace": "IBM Plex Serif", "bold": true, "color": "#1e293b"}},
      {"type": "image", "src": "fig_ddos_frecuencia.png", "alt": "DDoS frecuencia", "position": {"x": "8%", "y": "18%", "w": "84%", "h": "70%"}, "style": {"objectFit": "contain"}},
      {"type": "text", "content": "Meseta ~300k; arrastre 60 s; latencia 10 s; MRE ≤ 4,11%.", "role": "caption", "position": {"x": "8%", "y": "90%", "w": "84%", "h": "8%"}, "style": {"fontSize": 16, "fontFace": "IBM Plex Sans", "color": "#64748b", "align": "center"}}
    ], "notes": "Curva DDoS."},
    {"layout": "fig", "background": {"color": "#ffffff"}, "elements": [
      {"type": "text", "content": "Scan: contraste desde IP de origen", "role": "title", "position": {"x": "5%", "y": "5%", "w": "90%", "h": "10%"}, "style": {"fontSize": 32, "fontFace": "IBM Plex Serif", "bold": true, "color": "#1e293b"}},
      {"type": "image", "src": "fig_scan_frecuencia.png", "alt": "Scan frecuencia", "position": {"x": "8%", "y": "18%", "w": "84%", "h": "70%"}, "style": {"objectFit": "contain"}},
      {"type": "text", "content": "De f≈0 a 80k; latencia 20 s; FP esperado CMS w=256.", "role": "caption", "position": {"x": "8%", "y": "90%", "w": "84%", "h": "8%"}, "style": {"fontSize": 16, "fontFace": "IBM Plex Sans", "color": "#64748b", "align": "center"}}
    ], "notes": "Curva Scan."},
    {"layout": "fig", "background": {"color": "#ffffff"}, "elements": [
      {"type": "text", "content": "Comparación: CMS sobreestima, CS insesgado", "role": "title", "position": {"x": "5%", "y": "5%", "w": "90%", "h": "10%"}, "style": {"fontSize": 32, "fontFace": "IBM Plex Serif", "bold": true, "color": "#1e293b"}},
      {"type": "image", "src": "fig_scatter_est_exact.png", "alt": "Scatter", "position": {"x": "5%", "y": "16%", "w": "45%", "h": "72%"}, "style": {"objectFit": "contain"}},
      {"type": "image", "src": "fig_error_hist.png", "alt": "Histograma", "position": {"x": "50%", "y": "16%", "w": "45%", "h": "72%"}, "style": {"objectFit": "contain"}}
    ], "notes": "Evidencia de estimadores."},
    {"layout": "fig", "background": {"color": "#ffffff"}, "elements": [
      {"type": "text", "content": "Cambio de frecuencia Δf_j", "role": "title", "position": {"x": "5%", "y": "5%", "w": "90%", "h": "10%"}, "style": {"fontSize": 32, "fontFace": "IBM Plex Serif", "bold": true, "color": "#1e293b"}},
      {"type": "image", "src": "fig_ddos_delta.png", "alt": "Delta DDoS", "position": {"x": "5%", "y": "16%", "w": "45%", "h": "72%"}, "style": {"objectFit": "contain"}},
      {"type": "image", "src": "fig_scan_delta.png", "alt": "Delta Scan", "position": {"x": "50%", "y": "16%", "w": "45%", "h": "72%"}, "style": {"objectFit": "contain"}}
    ], "notes": "Picos de Δf."},
    {"layout": "bullets", "background": {"color": "#ffffff"}, "elements": [
      {"type": "text", "content": "Conclusiones", "role": "title", "position": {"x": "5%", "y": "8%", "w": "90%", "h": "12%"}, "style": {"fontSize": 36, "fontFace": "IBM Plex Serif", "bold": true, "color": "#1e293b"}},
      {"type": "text", "content": "Linealidad → O(d·w); CS más preciso y robusto; CMS competitivo a w grande; w=1024 equilibrio; Δf estimado sin reprocesar.", "role": "body", "position": {"x": "10%", "y": "28%", "w": "80%", "h": "50%"}, "style": {"fontSize": 22, "fontFace": "IBM Plex Sans", "color": "#1e293b"}}
    ], "notes": "Cierre técnico."},
    {"layout": "title", "background": {"color": "#ffffff"}, "elements": [
      {"type": "text", "content": "¡Gracias!", "role": "title", "position": {"x": "10%", "y": "35%", "w": "80%", "h": "20%"}, "style": {"fontSize": 56, "fontFace": "IBM Plex Serif", "bold": true, "color": "#1e293b", "align": "center"}},
      {"type": "text", "content": "Preguntas", "role": "subtitle", "position": {"x": "15%", "y": "55%", "w": "70%", "h": "10%"}, "style": {"fontSize": 24, "fontFace": "IBM Plex Sans", "color": "#64748b", "align": "center"}},
      {"type": "text", "content": "URL traza MAWI + semilla 42", "role": "caption", "position": {"x": "15%", "y": "70%", "w": "70%", "h": "8%"}, "style": {"fontSize": 16, "fontFace": "IBM Plex Sans", "color": "#64748b", "align": "center"}}
    ], "notes": "Cierre y preguntas."}
  ]
}"""

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Serif:wght@600&family=IBM+Plex+Sans:wght@400;500&display=swap" rel="stylesheet">')

html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Count-Min Sketch y CountSketch en ventanas deslizantes</title>
  {FONTS}
  <style>
{PRESET_CSS}
{BASE_CSS}
{ANIM_CSS}
{EXTRA_CSS}
  </style>
</head>
<body>
  <div class="ns-deck">
    <div class="ns-progress"><div class="ns-progress-bar"></div></div>
{SLIDES}
    <div class="ns-nav">
      <button class="ns-nav-prev" aria-label="Anterior">&#8249;</button>
      <button class="ns-nav-next" aria-label="Siguiente">&#8250;</button>
    </div>
    <div class="ns-counter"><span class="ns-current">1</span> / <span class="ns-total">13</span></div>
  </div>

  <script type="application/json" id="slide-data">
{JSON_DATA}
  </script>

  <script>
{JS}
  </script>
</body>
</html>"""

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(html, encoding="utf-8")
print(f"Generado: {OUT} ({os.path.getsize(OUT)/1e6:.2f} MB, {SLIDES.count('<section class=\"slide\"')} slides)")