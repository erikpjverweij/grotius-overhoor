/* Grotius O&A · Rechtspraak — service worker
 *
 * - index.html / startpagina: network-first (altijd de nieuwste app), offline uit de cache.
 * - cases.js / cases.json (1 MB): stale-while-revalidate — direct uit de cache zodat de app snel start,
 *   op de achtergrond ververst; eerste keer gewoon via het netwerk.
 * - overige bestanden (iconen, manifest): cache-first.
 * Alle netwerkverzoeken omzeilen de HTTP-cache van de browser (GitHub Pages stuurt max-age=600),
 * zodat een nieuwe versie direct na het pushen doorkomt. Alleen geslaagde antwoorden worden bewaard.
 */
const CACHE_NAME = 'grotius-rechtspraak-v11';
const STATIC_ASSETS = ['./', './index.html', './manifest.webmanifest', './icon-192.png', './icon-512.png', './apple-touch-icon.png', './favicon.png', './cases.js'];

const fresh = req => fetch(req, { cache: 'no-cache' });
const store = (cache, req, resp) => { if (resp && resp.ok) cache.put(req, resp.clone()); return resp; };

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE_NAME).then(c => Promise.all(STATIC_ASSETS.map(u => fresh(u).then(r => store(c, u, r)).catch(() => {})))));
  self.skipWaiting();
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (url.origin !== self.location.origin || e.request.method !== 'GET') return;
  const p = url.pathname;
  const isApp = p.endsWith('/') || p.endsWith('index.html');
  const isData = p.endsWith('cases.js') || p.endsWith('cases.json');
  e.respondWith(caches.open(CACHE_NAME).then(async cache => {
    const cached = await cache.match(e.request, { ignoreSearch: true });
    if (isApp) {
      try { const r = await fresh(e.request); return store(cache, e.request, r); }
      catch (err) { return cached || Response.error(); }
    }
    if (isData) {
      const update = fresh(e.request).then(r => store(cache, e.request, r)).catch(() => null);
      if (cached) { e.waitUntil(update); return cached; }
      return (await update) || Response.error();
    }
    if (cached) return cached;
    try { const r = await fresh(e.request); return store(cache, e.request, r); }
    catch (err) { return Response.error(); }
  }));
});
