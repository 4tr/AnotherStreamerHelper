const CACHE_NAME = "offline-cache-v1";
const FILES_TO_CACHE = ["/", "/index.html", "static/offline.js", "static/sw.js"];

// Устанавливаем SW и кэшируем ресурсы
self.addEventListener("install", (event) => {
  console.log("Service Worker: install");
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(FILES_TO_CACHE))
  );
  self.skipWaiting();
});

// Активируем и очищаем старые кэши
self.addEventListener("activate", (event) => {
  console.log("Service Worker: activate");
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.map((key) => key !== CACHE_NAME && caches.delete(key)))
    )
  );
  self.clients.claim();
});

// Перехватываем запросы
self.addEventListener("fetch", (event) => {
  event.respondWith(
    fetch(event.request).catch(() => {
      // Если сети нет — вернуть из кэша
      return caches.match(event.request).then((response) => {
        if (response) return response;
        // Если нет в кэше, отдать index.html
        return caches.match("/index.html");
      });
    })
  );
});
