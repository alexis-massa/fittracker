// Minimal service worker: no offline caching, since the app needs a live
// connection to the backend. Its only job is to satisfy the browser's PWA
// installability check (which requires a registered fetch handler).
self.addEventListener("fetch", (event) => {
  event.respondWith(fetch(event.request));
});
