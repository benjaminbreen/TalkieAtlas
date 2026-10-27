"use strict";
(() => {
  const script = document.currentScript;
  const root = new URL("./", script.src);
  const footer = document.querySelector(".site-footer");
  if (!footer) return;
  const type = document.documentElement.dataset.type;
  const fonts = {source:"Source Sans 3",plex:"IBM Plex Sans",newsreader:"Newsreader and Source Sans 3"};
  footer.querySelector('[data-colophon-type]').textContent = fonts[type] || fonts.source;

  fetch(new URL("footer-personas.json", root))
    .then(response => {if (!response.ok) throw Error("Persona illustrations unavailable");return response.json();})
    .then(personas => {
      // Choose once per page load; no duplicates or automatic cycling while reading.
      const pool = personas.filter(p => typeof p.name === "string" && /^n\/\d+-\d+-(up|down)\/$/.test(p.path) && /^icons\/\d+-\d+-(up|down)\.svg$/.test(p.icon));
      if (pool.length < 3) return;
      for (let i = pool.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [pool[i],pool[j]] = [pool[j],pool[i]];
      }
      const links = pool.slice(0,3).map(persona => {
        const link = document.createElement('a');
        link.className = 'footer-persona';
        link.href = new URL(persona.path,root);
        const img = document.createElement('img');
        img.src = new URL(persona.icon,root);
        img.alt = '';
        img.width = 128; img.height = 152;
        img.loading = 'lazy'; img.decoding = 'async';
        const label = document.createElement('span');
        label.textContent = persona.name;
        link.append(img,label);
        return link;
      });
      footer.querySelector('.footer-personas').replaceChildren(...links);
    })
    .catch(() => {}); // Keep the three real, labeled fallback illustrations.
})();
