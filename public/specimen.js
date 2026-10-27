"use strict";
// Hovering the headline resets the model's name in a random period typeface,
// from Gutenberg's textura to Franklin Gothic; tapping does the same on touch screens.
(() => {
  const FACES = [
    ["UnifrakturMaguntia", 400], ["EB Garamond", 500], ["IM Fell English", 400], ["Libre Caslon Display", 400],
    ["Libre Baskerville", 400], ["Bodoni Moda", 500], ["Abril Fatface", 400], ["Libre Franklin", 650],
  ];
  const morph = document.getElementById("morph"), headline = morph?.closest("h1");
  if (!morph || !headline) return;
  let last = -1;
  const base = morph.querySelector('.morph-base');
  const historical = morph.querySelector('.morph-historical');
  if (!base || !historical) return;

  function randomFace() {
    let i;
    do i = Math.floor(Math.random() * FACES.length); while (i === last);
    last = i;
    historical.style.fontFamily = `'${FACES[i][0]}'`;
    historical.style.fontWeight = FACES[i][1];
    historical.style.fontSize = '';
    historical.style.transform = '';
    morph.classList.add('is-historical');
    // Keep the word's original space so historical faces do not move the headline.
    const range = document.createRange();
    range.selectNodeContents(historical);
    const width = range.getBoundingClientRect().width;
    if (width > base.offsetWidth) historical.style.transform = `scaleX(${base.offsetWidth / width})`;
  }
  const reset = () => morph.classList.remove('is-historical');

  headline.addEventListener("mouseenter", randomFace);
  headline.addEventListener("mouseleave", reset);
  morph.addEventListener("click", e => { if (!matchMedia("(hover: hover)").matches) { e.preventDefault(); randomFace(); } });
  // Warm the subset faces (a few KB each) so the first hover doesn't flash.
  for (const [font, weight] of FACES) document.fonts?.load(`${weight} 1em '${font}'`, 'Talkie');
})();
