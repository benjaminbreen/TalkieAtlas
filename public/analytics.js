"use strict";
// Vercel's framework-free Web Analytics integration; skip local development.
if (!['localhost','127.0.0.1','::1'].includes(location.hostname)) {
  window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
  const analytics = document.createElement('script');
  analytics.defer = true;
  analytics.src = '/_vercel/insights/script.js';
  document.head.append(analytics);
}
