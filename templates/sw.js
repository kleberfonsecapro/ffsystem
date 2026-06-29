const CACHE_NAME = "smartfinance-v2";
const STATIC_ASSETS = [
  "/static/manifest.json",
  "/static/css/style.css",
  "/static/icon-192.png",
  "/static/icon-512.png",
];

function isStatic(url) {
  return STATIC_ASSETS.some((path) => url.includes(path))
    || url.includes("/static/");
}

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS).catch(() => {});
    })
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))
      );
    })
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;

  // Navigation (HTML pages) — network-first: always fetch fresh auth state
  if (event.request.mode === "navigate" || event.request.headers.get("Accept")?.includes("text/html")) {
    event.respondWith(
      fetch(event.request).then((response) => {
        if (response.status === 200 && !event.request.url.includes("/admin/")) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        }
        return response;
      }).catch(() => caches.match(event.request))
    );
    return;
  }

  // Static assets — cache-first
  if (isStatic(event.request.url)) {
    event.respondWith(
      caches.match(event.request).then((cached) => cached || fetch(event.request))
    );
    return;
  }

  // Everything else — network-only
  event.respondWith(fetch(event.request));
});
