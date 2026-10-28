// Light or dark: follows the system unless the visitor picks one. Loaded blocking in <head> so the page never flashes.
(() => {
  const KEY = "talkie-theme", root = document.documentElement, system = matchMedia("(prefers-color-scheme: dark)");
  const read = () => { try { const v = localStorage.getItem(KEY); return v === "light" || v === "dark" ? v : null; } catch { return null; } };
  const write = v => { try { v ? localStorage.setItem(KEY, v) : localStorage.removeItem(KEY); } catch {} };
  const effective = () => read() || (system.matches ? "dark" : "light");
  const ICONS = {
    dark: '<svg viewBox="0 0 20 20" aria-hidden="true"><path d="M16.5 12.2A7 7 0 0 1 7.8 3.5a7 7 0 1 0 8.7 8.7Z"/></svg>',
    light: '<svg viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="3.6"/><path d="M10 1.5v2.2M10 16.3v2.2M1.5 10h2.2M16.3 10h2.2M4 4l1.6 1.6M14.4 14.4 16 16M4 16l1.6-1.6M14.4 5.6 16 4"/></svg>',
  };
  function sync() {
    // Browser toolbars tint to theme-color, so it follows the page background.
    const meta = document.querySelector('meta[name="theme-color"]');
    if (meta && document.body) meta.content = getComputedStyle(document.body).backgroundColor;
    const button = document.querySelector(".theme-toggle");
    if (!button) return;
    const next = root.dataset.theme === "dark" ? "light" : "dark";
    button.innerHTML = ICONS[root.dataset.theme];
    button.setAttribute("aria-label", `Switch to ${next} mode`);
    button.title = `Switch to ${next} mode`;
  }
  function apply() {
    const theme = effective();
    if (root.dataset.theme === theme) return sync();
    root.dataset.theme = theme;
    sync();
    dispatchEvent(new CustomEvent("themechange", { detail: theme }));
  }
  apply();
  system.addEventListener("change", apply);
  addEventListener("storage", e => { if (e.key === KEY) apply(); });
  function mount() {
    const nav = document.querySelector("body > header nav");
    if (!nav || nav.parentElement.querySelector(".theme-toggle")) return sync();
    const button = document.createElement("button");
    button.type = "button";
    button.className = "theme-toggle";
    // Choosing the system's own theme clears the override, so the page goes back to following the system.
    button.addEventListener("click", () => {
      const next = root.dataset.theme === "dark" ? "light" : "dark";
      write(next === (system.matches ? "dark" : "light") ? null : next);
      apply();
    });
    nav.after(button);
    sync();
  }
  document.readyState === "loading" ? document.addEventListener("DOMContentLoaded", mount) : mount();
})();
