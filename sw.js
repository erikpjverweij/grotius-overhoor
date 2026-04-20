/* Grotius Overhoor — service worker
 *
 * Strategie:
 *   - Statische assets (index.html, iconen, manifest) worden gecached bij install.
 *   - cards.json wordt "network first" geladen: altijd proberen de nieuwste versie
 *     te pakken, maar bij geen netwerk valt hij terug op de cache. Zo werkt de app
 *     offline maar zie je wel direct nieuwe kaarten zodra je weer bereik hebt.
 */

const CACHE_NAME = 'grotius-overhoor-v3';
const STATIC_ASSETS = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icon-192.png',
  './icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);

  // Alleen same-origin requests afhandelen; CDN (Tailwind) mag direct naar het netwerk
  if (url.origin !== self.location.origin) return;

  // cards.json: network-first
  if (url.pathname.endsWith('/cards.json') || url.pathname.endsWith('cards.json')) {
    event.respondWith(
      fetch(event.request)
        .then(resp => {
          const copy = resp.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, copy));
          return resp;
        })
        .catch(() => caches.match(event.request))
    );
    return;
  }

  // Alle andere same-origin assets: cache-first
  event.respondWith(
    caches.match(event.request).then(hit => hit || fetch(event.request))
  );
});
