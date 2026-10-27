"use strict";
(() => {
  const root = new URL('./', document.currentScript.src);
  const images = [...document.querySelectorAll('.brand-robot')];
  if (images.length !== 2) return;
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  let active = 0, current = 'icons/17-10423-down.svg', pool = [], timer, loading = false;
  async function nextRobot() {
    if (document.hidden || motion.matches || pool.length < 2 || loading) return;
    loading = true;
    try {
    const choices = pool.filter(icon => icon !== current);
    const icon = choices[Math.floor(Math.random() * choices.length)];
    const next = images[1 - active];
    next.src = new URL(icon, root);
    await next.decode();
    if (document.hidden || motion.matches) return;
    images[active].classList.remove('is-visible');
    next.classList.add('is-visible');
    active = 1 - active;
    current = icon;
    } catch {} finally { loading = false; }
  }
  function schedule() {
    clearInterval(timer);
    if (!document.hidden && !motion.matches) timer = setInterval(nextRobot, 5000);
  }
  fetch(new URL('footer-personas.json', root)).then(r => r.ok ? r.json() : [])
    .then(personas => {
      pool = [...new Set(personas.map(p => p.icon).filter(icon => /^icons\/\d+-\d+-(up|down)\.svg$/.test(icon)))];
      schedule();
    }).catch(() => {});
  document.addEventListener('visibilitychange', schedule);
  motion.addEventListener('change', schedule);
})();
