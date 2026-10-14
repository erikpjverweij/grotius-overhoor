/* Grotius O&A · Rechtspraak — service worker
 * Statische assets cache-first; cases.json network-first (offline fallback op cache). */
const CACHE_NAME = 'grotius-rechtspraak-v1';
const STATIC_ASSETS = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png', './cases.js'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE_NAME).then(c => c.addAll(STATIC_ASSETS))); self.skipWaiting(); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))))); self.clients.claim(); });
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname.endsWith('cases.json') || url.pathname.endsWith('cases.js') || url.pathname.endsWith('index.html') || url.pathname.endsWith('/')) {
    e.respondWith(fetch(e.request).then(r => { const copy = r.clone(); caches.open(CACHE_NAME).then(c => c.put(e.request, copy)); return r; }).catch(() => caches.match(e.request)));
    return;
  }
  e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request)));
});
