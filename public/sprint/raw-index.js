/* Complete raw replies; only visible table rows are mounted. No model calls. */
(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const ROW = 61, HEAD = 42, OVERSCAN = 7;
  const controls = ['search', 'kind', 'rating', 'sort', 'layer', 'neuron', 'direction', 'strength', 'run', 'stage', 'reset', 'jump', 'download-csv', 'download-json'];
  const state = { rows: [], filtered: [], selected: null, sort: 'weirdness', descending: true, from: -1, to: -1, byId: new Map() };
  const escape = value => String(value ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const number = n => n.toLocaleString();
  const types = { single: 'One neuron', pair: 'Two neurons', multiple: 'Several neurons', control: 'Control' };
  const runNames = {
    pilot: 'Initial library sample', discovery: 'Library discovery', 'novelty-sprint': 'Larger neuron search',
    'neuron-expansion': 'Neuron expansion', 'pair-strength-study': 'Pair strength study',
    playground: 'Pair playground', 'full-reply-review': 'Full-reply reruns',
    'fresh-neuron-calibration': 'Fresh-neuron calibration'
  };
  const runName = id => runNames[id] || id.replace(/-(2026)(\d{2})(\d{2})(?:T(\d{2})(\d{2})\d{2}Z)?/g, (_, y, m, d, h, minute) => ` · ${m}/${d}${h ? ' ' + h + ':' + minute + ' UTC' : ''}`).replace(/-/g, ' ');
  const settings = r => r.edits.map(e => `L${e[0]} · N${e[1]} ${e[2] > 0 ? '↑' : '↓'} · ${e[3]}×`).join(' + ') || 'No neuron intervention';
  const score = (n, cls = '') => n == null ? '—' : `<span class="score ${cls}">${escape(n)}</span>`;
  function setSort(value) {
    const split = value.lastIndexOf('-');
    state.sort = value.slice(0, split); state.descending = value.slice(split + 1) === 'desc';
  }
  function selectedIndex() { return state.filtered.findIndex(r => r.id === state.selected); }
  function sortRows(a, b) {
    let x, y;
    if (state.sort === 'name') { x = a.name; y = b.name; }
    else if (state.sort === 'run') { x = runName(a.run); y = runName(b.run); }
    else if (state.sort === 'layer') { x = a.edits.length ? Math.min(...a.edits.map(e => e[0])) : null; y = b.edits.length ? Math.min(...b.edits.map(e => e[0])) : null; }
    else { x = a[state.sort]; y = b[state.sort]; }
    if (x == null || y == null) return x == null && y == null ? a.id.localeCompare(b.id) : x == null ? 1 : -1;
    const order = typeof x === 'string' ? x.localeCompare(y) : x - y;
    return order ? order * (state.descending ? -1 : 1) : a.id.localeCompare(b.id);
  }
  function applyFilters({ resetScroll = true, preserveSelection = true } = {}) {
    const words = $('search').value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    const kind = $('kind').value, rating = $('rating').value, layer = $('layer').value;
    const unit = $('neuron').value, direction = $('direction').value, strength = $('strength').value;
    const run = $('run').value, stage = $('stage').value;
    state.filtered = state.rows.filter(r => {
      if (kind !== 'all' && kind !== r.kind || run !== 'all' && run !== r.run || stage !== 'all' && stage !== r.stage) return false;
      if (rating === 'rated' && r.weirdness == null || rating === 'unrated' && r.weirdness != null || rating === 'v3' && !r.rating_source.startsWith('Saved v3')) return false;
      if (layer !== 'all' || unit !== '' || direction !== 'all' || strength !== 'all') {
        if (!r.edits.some(e => (layer === 'all' || e[0] === +layer) && (unit === '' || e[1] === +unit) && (direction === 'all' || e[2] === +direction) && (strength === 'all' || e[3] === +strength))) return false;
      }
      return words.every(word => r.searchText.includes(word));
    }).sort(sortRows);
    const total = state.filtered.length;
    const units = new Set();
    state.filtered.forEach(r => r.edits.forEach(e => units.add(e[0] + ':' + e[1])));
    $('result-count').textContent = `${number(total)} matching saved ${total === 1 ? 'reply' : 'replies'} · ${number(state.rows.length)} total`;
    $('neuron-count').textContent = `${number(units.size)} physical neurons in these results`;
    $('jump').max = Math.max(1, total);
    document.querySelector('table').setAttribute('aria-rowcount', total + 1);
    if (resetScroll) $('table-scroll').scrollTop = 0;
    if (!preserveSelection || !state.filtered.some(r => r.id === state.selected)) state.selected = state.filtered[0]?.id || null;
    state.from = state.to = -1;
    renderWindow(); renderReader(); updateHeaders();
    ['download-csv', 'download-json', 'jump'].forEach(id => $(id).disabled = total === 0);
  }
  function updateHeaders() {
    document.querySelectorAll('th [data-sort]').forEach(button => {
      const active = button.dataset.sort === state.sort;
      button.parentElement.setAttribute('aria-sort', active ? state.descending ? 'descending' : 'ascending' : 'none');
      button.querySelector('span').textContent = active ? state.descending ? '↓' : '↑' : '↕';
    });
  }
  function renderWindow(force = false) {
    const scroller = $('table-scroll'), total = state.filtered.length;
    const firstVisible = Math.max(0, Math.floor(scroller.scrollTop / ROW));
    const from = Math.max(0, firstVisible - OVERSCAN);
    const to = Math.min(total, firstVisible + Math.ceil(scroller.clientHeight / ROW) + OVERSCAN);
    if (!force && from === state.from && to === state.to) return;
    state.from = from; state.to = to;
    const spacer = height => `<tr class="spacer" aria-hidden="true"><td colspan="6" style="height:${height}px"></td></tr>`;
    $('reply-rows').innerHTML = total ? spacer(from * ROW) + state.filtered.slice(from, to).map((r, offset) => {
      const index = from + offset;
      return `<tr class="reply-row${r.id === state.selected ? ' selected' : ''}" data-record="${escape(r.id)}" aria-rowindex="${index + 2}" aria-selected="${r.id === state.selected}"><td class="row-number">${number(index + 1)}</td><td><button class="reply-name" data-record="${escape(r.id)}" title="${escape(r.name)}">${escape(r.name)}</button><div class="reply-snippet">${escape(r.text || '[Empty saved reply]')}</div></td><td><span class="type-label ${r.kind}">${types[r.kind]}</span></td><td class="layer-value">${r.edits.map(e => e[0]).join(' + ') || '—'}</td><td>${score(r.weirdness)}</td><td>${score(r.coherence, 'coherence')}</td></tr>`;
    }).join('') + spacer((total - to) * ROW) : '<tr><td colspan="6" class="empty-result">No matching replies. Try fewer filters.</td></tr>';
    const end = Math.min(total, Math.ceil((scroller.scrollTop + scroller.clientHeight - HEAD) / ROW));
    $('visible-range').textContent = total ? `Rows ${number(firstVisible + 1)}–${number(end)} of ${number(total)}` : 'No matching rows';
  }
  const stopName = reason => ({ finished: 'Finished', length: 'Token limit', repeating: 'Repetition stop', stop: 'Stop token' }[reason] || reason || 'Not recorded');
  function renderReader() {
    const r = state.byId.get(state.selected);
    if (!r) { $('reader').innerHTML = '<div class="reader-empty">No matching reply. Try a different search or filter.</div>'; return; }
    const index = selectedIndex();
    let sourceLink = '';
    if (r.source_id) {
      const source = state.rows.find(row => row.original_id === r.source_id && row.id !== r.id);
      sourceLink = source ? `<button data-related="${escape(source.id)}">Read source reply ↗</button>` : '';
    }
    const libraryLink = r.library_path ? `<a href="../${escape(r.library_path)}">Open in library ↗</a>` : '';
    const history = Object.fromEntries(Object.entries(r.ratings || {}).filter(([, value]) => value));
    const parents = r.parents.map(id => {
      const parent = state.rows.find(row => row.original_id === id);
      return parent ? `<button data-related="${escape(parent.id)}">${escape(parent.name)}</button>` : escape(id);
    }).join(' + ');
    $('reader').innerHTML = `<div class="reader-top"><span class="reader-label">Full saved reply</span><div class="reader-arrows"><button data-move="-1" aria-label="Previous reply" ${index <= 0 ? 'disabled' : ''}>←</button><button data-move="1" aria-label="Next reply" ${index < 0 || index >= state.filtered.length - 1 ? 'disabled' : ''}>→</button></div></div><h2>${escape(r.name)}</h2><div class="reader-settings"><span class="type-label ${r.kind}">${types[r.kind]}</span> · ${escape(settings(r))}</div>${r.prompt ? `<div class="prompt">${escape(r.prompt)}</div>` : '<div class="reader-settings">Prompt not recorded in this source</div>'}<p class="raw-reply">${escape(r.text || '[Empty saved reply]')}</p><dl class="reader-facts"><div><dt>Stop reason</dt><dd>${escape(stopName(r.stop))}</dd></div><div><dt>Reply length</dt><dd>${r.tokens == null ? 'Not recorded' : r.tokens + ' tokens'}${r.max_tokens ? ' / ' + r.max_tokens + ' cap' : ''}</dd></div><div><dt>Saved weirdness</dt><dd>${r.weirdness == null ? 'Unscored' : r.weirdness + ' / 10'}</dd></div><div><dt>Saved coherence</dt><dd>${r.coherence == null ? 'Unscored' : r.coherence + ' / 10'}</dd></div><div><dt>Generation</dt><dd>${escape(r.stage)}${r.preview ? ' · short screen' : ''}</dd></div><div><dt>Same normalized text</dt><dd>${number(r.same_text_records)} saved ${r.same_text_records === 1 ? 'record' : 'records'}</dd></div></dl><div class="reader-links"><button id="copy-link">Copy reply link</button><button id="download-reply">Save record ↓</button>${sourceLink}${libraryLink}</div><div class="status-message" id="reader-status" role="status"></div><div class="record-provenance">${escape(runName(r.run))}<br>${escape(r.original_id)}${parents ? `<div class="reader-links">Parents: ${parents}</div>` : ''}<details><summary>Source and score history</summary><p>${r.sources.map(escape).join('<br>')}${r.source_line ? '<br>Source line or export record: ' + r.source_line : ''}</p><pre>${escape(JSON.stringify({ prompt: r.prompt, max_tokens: r.max_tokens, batch: r.batch, temperature: r.temperature, seed: r.seed, source_id: r.source_id, ratings: history }, null, 2))}</pre></details></div>`;
    $('reader').scrollTop = 0;
    const header = $('reader').querySelector('h2'); header.setAttribute('id', 'selected-reply-name');
    $('reader').setAttribute('aria-labelledby', 'selected-reply-name');
  }
  function revealSelection() {
    const index = selectedIndex(); if (index < 0) return;
    const scroller = $('table-scroll'), top = HEAD + index * ROW, bottom = top + ROW;
    if (top < scroller.scrollTop + HEAD) scroller.scrollTop = top - HEAD;
    else if (bottom > scroller.scrollTop + scroller.clientHeight) scroller.scrollTop = bottom - scroller.clientHeight;
    renderWindow(true);
  }
  function selectRecord(id, reveal = false) {
    if (!state.byId.has(id)) return;
    state.selected = id; renderWindow(true); renderReader();
    if (reveal) revealSelection();
    history.replaceState(null, '', location.pathname + location.search + '#reply=' + encodeURIComponent(id));
  }
  function navigate(step) {
    const index = selectedIndex(), next = state.filtered[index + step];
    if (next) selectRecord(next.id, true);
  }
  function reset() {
    $('search').value = ''; $('neuron').value = '';
    ['kind', 'rating', 'layer', 'direction', 'strength', 'run', 'stage'].forEach(id => $(id).value = 'all');
    $('sort').value = 'weirdness-desc'; setSort($('sort').value);
  }
  function publicRecord(r) { const { searchText, ...record } = r; return record; }
  function download(content, name, type) {
    const url = URL.createObjectURL(new Blob([content], { type }));
    const a = document.createElement('a'); a.href = url; a.download = name; a.click();
    setTimeout(() => URL.revokeObjectURL(url), 30000);
  }
  function csvValue(value) {
    let text = value == null ? '' : String(value);
    // Spreadsheet apps must not execute model text as a formula.
    if (/^[=+\-@\t\r]/.test(text)) text = "'" + text;
    return '"' + text.replace(/"/g, '""') + '"';
  }
  function exportCSV() {
    const fields = ['id', 'name', 'kind', 'stage', 'run', 'prompt', 'weirdness', 'coherence', 'rating_source', 'tokens', 'max_tokens', 'stop', 'text'];
    const lines = [fields.map(csvValue).join(',')];
    state.filtered.forEach(r => lines.push(fields.map(f => csvValue(r[f])).join(',')));
    download('\ufeff' + lines.join('\r\n'), 'talkie-raw-replies.csv', 'text/csv;charset=utf-8');
  }
  function populateSelect(id, values, label = x => x) {
    const select = $(id);
    select.querySelectorAll('option:not(:first-child)').forEach(option => option.remove());
    values.forEach(value => { const option = document.createElement('option'); option.value = value; option.textContent = label(value); select.append(option); });
  }
  async function load() {
    $('load-error').hidden = true; $('workspace').setAttribute('aria-busy', 'true');
    controls.forEach(id => $(id).disabled = true);
    try {
      const manifestResponse = await fetch('index-data.json?v=' + encodeURIComponent(document.body.dataset.version), { cache: 'no-cache' });
      if (!manifestResponse.ok) throw Error('Manifest HTTP ' + manifestResponse.status);
      const manifest = await manifestResponse.json();
      if (manifest.version !== document.body.dataset.version) { location.reload(); return; }
      const chunks = new Array(manifest.files.length); let next = 0, loaded = 0;
      async function worker() {
        while (next < manifest.files.length) {
          const index = next++, response = await fetch(manifest.files[index]);
          if (!response.ok) throw Error('Data HTTP ' + response.status);
          chunks[index] = await response.json(); loaded += chunks[index].length;
          $('result-count').textContent = `Loading ${number(loaded)} of ${number(manifest.summary.replies)} saved replies…`;
        }
      }
      await Promise.all(Array.from({ length: Math.min(5, manifest.files.length) }, worker));
      state.rows = chunks.flat();
      if (state.rows.length !== manifest.summary.replies) throw Error('Incomplete data export');
      state.rows.forEach(r => {
        r.searchText = [r.name, r.text, r.original_id, r.id, r.prompt, r.run, runName(r.run), r.stage, r.category, settings(r), ...r.edits.map(e => `${e[0]}:${e[1]} L${e[0]} N${e[1]}`)].join(' ').toLowerCase();
      });
      state.byId = new Map(state.rows.map(r => [r.id, r]));
      if (state.byId.size !== state.rows.length) throw Error('Duplicate record IDs');
      populateSelect('layer', Array.from({ length: 40 }, (_, i) => i));
      populateSelect('strength', [...new Set(state.rows.flatMap(r => r.edits.map(e => e[3])))].sort((a, b) => a - b), n => n + '×');
      populateSelect('run', [...new Set(state.rows.map(r => r.run))].sort((a, b) => runName(a).localeCompare(runName(b))), runName);
      populateSelect('stage', [...new Set(state.rows.map(r => r.stage))].sort());
      const summary = manifest.summary;
      $('coverage-summary').textContent = `${number(summary.replies)} saved replies across ${number(summary.physical_neurons)} physical neurons and ${number(summary.signed_directions)} signed neuron directions. ${number(summary.library_attempts)} records come from the library export; earlier screens and follow-up studies are also included. Exported ${new Date(summary.generated_utc).toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' })}.`;
      controls.forEach(id => $(id).disabled = false);
      reset();
      const params = new URLSearchParams(location.search);
      ['layer', 'neuron', 'direction', 'kind', 'run', 'rating', 'strength', 'stage'].forEach(id => { if (params.has(id)) $(id).value = params.get(id); });
      $('search').value = params.get('q') || '';
      let linkId = null;
      try { linkId = decodeURIComponent(location.hash.replace(/^#reply=/, '')); } catch { /* Ignore malformed external fragments. */ }
      if (state.byId.has(linkId)) { reset(); state.selected = linkId; }
      applyFilters();
      if (state.byId.has(linkId)) selectRecord(linkId, true);
      $('workspace').setAttribute('aria-busy', 'false');
    } catch (error) {
      console.error('Raw reply index:', error);
      $('result-count').textContent = 'Saved replies could not be loaded.';
      $('workspace').setAttribute('aria-busy', 'false'); $('load-error').hidden = false;
    }
  }
  let searchTimer, scrollFrame;
  $('search').addEventListener('input', () => { clearTimeout(searchTimer); searchTimer = setTimeout(() => applyFilters(), 100); });
  $('neuron').addEventListener('input', () => applyFilters());
  ['kind', 'rating', 'layer', 'direction', 'strength', 'run', 'stage'].forEach(id => $(id).addEventListener('change', () => applyFilters()));
  $('sort').addEventListener('change', () => { setSort($('sort').value); applyFilters(); });
  $('reset').addEventListener('click', () => { reset(); applyFilters({ preserveSelection: false }); });
  $('table-scroll').addEventListener('scroll', () => { cancelAnimationFrame(scrollFrame); scrollFrame = requestAnimationFrame(() => renderWindow()); });
  new ResizeObserver(() => renderWindow(true)).observe($('table-scroll'));
  $('reply-rows').addEventListener('click', event => {
    const row = event.target.closest('[data-record]'); if (!row) return;
    selectRecord(row.dataset.record);
    if (matchMedia('(max-width:720px)').matches) $('reader').scrollIntoView({ behavior: 'smooth', block: 'start' });
  });
  document.querySelectorAll('th [data-sort]').forEach(button => button.addEventListener('click', () => {
    const key = button.dataset.sort;
    state.descending = state.sort === key ? !state.descending : ['weirdness', 'coherence', 'tokens'].includes(key);
    state.sort = key;
    const value = key + (state.descending ? '-desc' : '-asc');
    if (![...$('sort').options].some(option => option.value === value)) {
      const option = document.createElement('option'); option.value = value; option.textContent = `${key === 'name' ? 'Name' : key === 'layer' ? 'Layer' : key === 'weirdness' ? 'Weirdness' : 'Coherence'} ${state.descending ? '↓' : '↑'}`; $('sort').append(option);
    }
    $('sort').value = value; applyFilters();
  }));
  $('reader').addEventListener('click', async event => {
    const move = event.target.closest('[data-move]'); if (move) navigate(+move.dataset.move);
    const related = event.target.closest('[data-related]');
    if (related) { reset(); applyFilters(); selectRecord(related.dataset.related, true); }
    if (event.target.id === 'download-reply') download(JSON.stringify(publicRecord(state.byId.get(state.selected)), null, 2), 'talkie-reply.json', 'application/json');
    if (event.target.id === 'copy-link') {
      const url = new URL(location.href); url.search = ''; url.hash = 'reply=' + encodeURIComponent(state.selected);
      try { await navigator.clipboard.writeText(url.href); $('reader-status').textContent = 'Reply link copied.'; }
      catch { $('reader-status').textContent = 'Select and copy this link: ' + url.href; }
    }
  });
  function jumpToRow() {
    const index = Math.min(state.filtered.length - 1, Math.max(0, Math.floor(+$('jump').value) - 1));
    if (state.filtered[index]) selectRecord(state.filtered[index].id, true);
  }
  let jumpTimer;
  $('jump').addEventListener('input', () => { clearTimeout(jumpTimer); jumpTimer = setTimeout(jumpToRow, 200); });
  $('jump').addEventListener('change', jumpToRow);
  $('jump').addEventListener('keydown', event => { if (event.key === 'Enter') { clearTimeout(jumpTimer); jumpToRow(); } });
  document.addEventListener('keydown', event => {
    if (event.target.closest('input,select,textarea,summary') || event.altKey || event.ctrlKey || event.metaKey) return;
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') { event.preventDefault(); navigate(event.key === 'ArrowDown' ? 1 : -1); }
  });
  $('download-csv').addEventListener('click', exportCSV);
  $('download-json').addEventListener('click', () => download(JSON.stringify(state.filtered.map(publicRecord)), 'talkie-raw-replies.json', 'application/json'));
  $('retry').addEventListener('click', load);
  window.addEventListener('hashchange', () => {
    try { const id = decodeURIComponent(location.hash.replace(/^#reply=/, '')); if (state.byId.has(id)) { reset(); applyFilters(); selectRecord(id, true); } } catch { /* Invalid fragment. */ }
  });
  load();
})();
