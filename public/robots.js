"use strict";
// Steam-man icons for the hundred strangest coherent personas (icons/build_icons.mjs).
// Kept out of app.js: watches the cards, the detail dialog and the hero chat, and adds a robot where one exists.
(async () => {
  let icons;
  try { icons = await (await fetch("icons/index.json")).json(); } catch { return; }
  const img = (id, cls) => Object.assign(document.createElement("img"), { src: icons[id], alt: "", className: cls, width: 128, height: 152, decoding: "async" });
  const watch = (el, fn) => { if (!el) return; fn(); new MutationObserver(fn).observe(el, { childList: true, characterData: true, subtree: true }); };

  const cards = document.getElementById("cards");
  watch(cards, () => {
    for (const card of cards.querySelectorAll(".card[data-id]:not(.has-robot)"))
      if (icons[card.dataset.id]) { card.classList.add("has-robot"); card.prepend(img(card.dataset.id, "card-robot")); }
  });

  // app.js keeps the open row in `current` and the hero rows in `heroRows`/`heroIndex`.
  const place = (box, id, cls, before) => {
    const old = box.querySelector("." + cls);
    if (old?.dataset.id === id) return;
    old?.remove();
    if (!id || !icons[id]) return;
    const el = img(id, cls); el.dataset.id = id;
    box.insertBefore(el, before ? box.querySelector(before) : box.firstChild);
  };
  const title = document.getElementById("detail-title");
  watch(title, () => place(document.querySelector("#detail .modal-head"), typeof current !== "undefined" && current?.id, "detail-robot"));
  // The highlight carousel places its own compact robot beside the persona name.
  if (document.getElementById("hero-icon")) return;
  const answer = document.getElementById("hero-answer");
  watch(answer, () => {
    const r = typeof heroRows !== "undefined" && heroRows.length ? heroRows[heroIndex % heroRows.length] : null;
    place(document.querySelector(".hero-chat"), r?.id, "hero-robot");
  });
})();
