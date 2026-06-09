const CACHE="ai-workflow-os-v2";
self.addEventListener("install",event=>{event.waitUntil(caches.open(CACHE).then(cache=>cache.addAll(["/","/static/app.css","/static/app.js","/manifest.webmanifest"])))});
self.addEventListener("fetch",event=>{event.respondWith(fetch(event.request).catch(()=>caches.match(event.request)))});
