// Service Worker para PWA - Loja de Bebidas
const CACHE_NAME = 'loja-bebidas-v1';
const urlsToCache = [
  '/',
  '/manifest.json',
  'https://cdnjs.cloudflare.com/ajax/libs/streamlit/1.28.0/static/css/bootstrap.min.css'
];

// Instalar o Service Worker
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        console.log('Cache aberto');
        return cache.addAll(urlsToCache);
      })
  );
});

// Buscar arquivos do cache
self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        // Retorna o cache se encontrado
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});

// Atualizar o Service Worker
self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});