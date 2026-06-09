const CACHE_NAME = "ai-workflow-os-shell-v1";
const SHELL = ["/", "/manifest.webmanifest", "/icons/ai-workflow-os-192.png", "/icons/ai-workflow-os-512.png", "/icons/ai-workflow-os-maskable-512.png"];
self.addEventListener("install", event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", event => {
  event.waitUntil(self.clients.claim());
});
self.addEventListener("fetch", event => {
  const url = new URL(event.request.url);
  if (url.pathname.startsWith("/api/")) return;
  event.respondWith(fetch(event.request).catch(() => caches.match(event.request).then(r => r || caches.match("/"))));
});
