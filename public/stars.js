"use strict";
(() => {
  const storageKey = "talkie-stars-v1";
  let counts = {}, ready = false;
  const busy = new Set(), local = new Map();
  const saved = id => { if (local.has(id)) return local.get(id); try { return localStorage.getItem(storageKey + ":" + id) === "1"; } catch { return false; } };
  const escape = value => String(value).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const icon = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m12 3 2.78 5.63 6.22.91-4.5 4.38 1.06 6.2L12 17.2l-5.56 2.92 1.06-6.2L3 9.54l6.22-.91Z"/></svg>';
  function button(id) {
    return `<button type="button" class="star-button" data-star-id="${escape(id)}" aria-pressed="false" aria-label="Star this persona">${icon}<span class="star-count">—</span></button>`;
  }
  function refresh(root = document) {
    for (const b of root.querySelectorAll('[data-star-id]')) {
      const id = b.dataset.starId, starred = saved(id), count = ready ? counts[id] || 0 : null;
      if (!b.querySelector('svg')) b.innerHTML = icon + '<span class="star-count">—</span>';
      b.setAttribute('aria-pressed', String(starred));
      b.setAttribute('aria-label', `${starred ? 'Unstar' : 'Star'} this persona${count === null ? '' : ` · ${count} ${count === 1 ? 'star' : 'stars'}`}`);
      b.title = ready ? (starred ? 'Unstar' : 'Star') : 'Loading stars';
      b.disabled = !ready || busy.has(id);
      b.querySelector('.star-count').textContent = count === null ? '—' : count.toLocaleString();
    }
  }
  function mount(element, id) { element.innerHTML = button(id); refresh(element); }
  async function load() {
    try {
      const r = await fetch('/api/stars', {credentials:'omit'});
      if (!r.ok) throw Error();
      counts = (await r.json()).counts; ready = true; refresh();
    } catch {
      for (const b of document.querySelectorAll('[data-star-id]')) { b.disabled = true; b.title = 'Stars unavailable. Reload to try again.'; }
    }
  }
  document.addEventListener('click', async event => {
    const b = event.target.closest('[data-star-id]');
    if (!b) return;
    event.preventDefault(); event.stopPropagation();
    const id = b.dataset.starId;
    if (!ready || busy.has(id)) return;
    const wasStarred = saved(id);
    busy.add(id); refresh();
    try {
      const r = await fetch('/api/stars', {method:'POST', credentials:'omit', headers:{'Content-Type':'application/json'}, body:JSON.stringify({id, delta:wasStarred ? -1 : 1})});
      if (!r.ok) throw Error();
      const result = await r.json(); counts[id] = result.count;
      local.set(id, !wasStarred);
      try { if (wasStarred) localStorage.removeItem(storageKey + ':' + id); else localStorage.setItem(storageKey + ':' + id, '1'); } catch { }
      busy.delete(id); refresh();
    } catch {
      busy.delete(id); refresh();
      for (const target of document.querySelectorAll('[data-star-id]')) if (target.dataset.starId === id) {
        target.title = 'Could not save star. Click to retry.';
        target.setAttribute('aria-label', 'Could not save star. Click to retry.');
      }
    }
  }, true);
  window.addEventListener('storage', e => { if (e.key?.startsWith(storageKey + ':')) { local.clear(); refresh(); load(); } });
  window.TalkieStars = {button, mount, refresh};
  load();
})();
