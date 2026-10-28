"use strict";
(() => {
  const script = document.currentScript;
  const root = new URL("./", script.src);
  const footer = document.querySelector(".site-footer");
  if (!footer) return;
  const type = document.documentElement.dataset.type;
  const fonts = {source:"Source Sans 3",plex:"IBM Plex Sans",newsreader:"Newsreader and Source Sans 3"};
  footer.querySelector('[data-colophon-type]').textContent = fonts[type] || fonts.source;

  fetch(new URL("footer-personas.json", root), {cache: "no-cache"})
    .then(response => {if (!response.ok) throw Error("Persona illustrations unavailable");return response.json();})
    .then(personas => {
      // Draw once per page, sharing a shuffled deck across this tab's page visits.
      // Use every illustrated name, including custom robots and pair outcomes.
      const seen = new Set();
      const pool = personas.filter(p => {
        if (typeof p.name !== "string" || !p.name.trim() || !/^[np]\/[A-Za-z0-9_-]+\/$/.test(p.path) || !/^icons\/[A-Za-z0-9_-]+\.svg$/.test(p.icon)) return false;
        const name = p.name.trim().toLocaleLowerCase();
        if (seen.has(name)) return false;
        seen.add(name);
        return true;
      });
      if (pool.length < 3) return;
      const shuffle = rows => {
        for (let i = rows.length - 1; i > 0; i--) {
          const j = Math.floor(Math.random() * (i + 1));
          [rows[i],rows[j]] = [rows[j],rows[i]];
        }
        return rows;
      };
      const byPath = new Map(pool.map(p => [p.path, p]));
      const version = [...byPath.keys()].sort().join("|");
      const storageKey = "talkie-footer-deck-v2";
      let saved;
      try { saved = JSON.parse(sessionStorage.getItem(storageKey)); } catch {}
      const validPaths = paths => Array.isArray(paths) ? [...new Set(paths.filter(p => byPath.has(p)))] : [];
      let remaining = saved?.version === version ? validPaths(saved.remaining) : shuffle([...byPath.keys()]);
      const recent = saved?.version === version ? validPaths(saved.recent) : [];
      const currentPath = pool.length > 3 ? location.pathname.replace(root.pathname, "") : null;
      const selected = [];
      for (let n = 0; n < 3; n++) {
        const available = path => path !== currentPath && !selected.includes(path);
        let index = remaining.findIndex(path => available(path) && !recent.includes(path));
        if (index < 0) {
          remaining = shuffle([...byPath.keys()].filter(path => available(path) && !recent.includes(path)));
          // Small pools may need recent entries to fill the trio.
          if (!remaining.length) remaining = shuffle([...byPath.keys()].filter(available));
          index = 0;
        }
        if (!remaining.length) break;
        selected.push(remaining.splice(index, 1)[0]);
      }
      try { sessionStorage.setItem(storageKey, JSON.stringify({version, remaining, recent: selected})); } catch {}
      const links = selected.map(path => {
        const persona = byPath.get(path);
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
