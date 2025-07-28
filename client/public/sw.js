// Service Worker for NexGuard Website
const CACHE_NAME = 'nexguard-v1';
const API_CACHE_NAME = 'nexguard-api-v1';

// Assets to cache immediately
const STATIC_ASSETS = [
  '/',
  '/features',
  '/invite',
  '/docs',
  '/manifest.json'
];

// API endpoints to cache
const API_ENDPOINTS = [
  '/api/bot/status',
  '/api/features',
  '/api/developers',
  '/api/news',
  '/api/config'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME && cacheName !== API_CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Handle API requests with network-first strategy
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      caches.open(API_CACHE_NAME).then(async (cache) => {
        try {
          // Try network first
          const networkResponse = await fetch(request);
          
          // Cache successful responses
          if (networkResponse.ok) {
            cache.put(request, networkResponse.clone());
          }
          
          return networkResponse;
        } catch (error) {
          // Fall back to cache if network fails
          const cachedResponse = await cache.match(request);
          if (cachedResponse) {
            return cachedResponse;
          }
          
          // Return offline fallback for critical endpoints
          if (url.pathname === '/api/bot/status') {
            return new Response(JSON.stringify({
              id: 1,
              isOnline: false,
              guildsCount: 0,
              usersCount: 0,
              message: 'Offline'
            }), {
              headers: { 'Content-Type': 'application/json' }
            });
          }
          
          throw error;
        }
      })
    );
    return;
  }

  // Handle static assets with cache-first strategy
  event.respondWith(
    caches.match(request).then((cachedResponse) => {
      if (cachedResponse) {
        return cachedResponse;
      }
      
      return fetch(request).then((response) => {
        // Don't cache non-successful responses
        if (!response.ok) {
          return response;
        }
        
        // Cache the response
        const responseClone = response.clone();
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(request, responseClone);
        });
        
        return response;
      });
    })
  );
});

// Background sync for failed requests
self.addEventListener('sync', (event) => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

async function doBackgroundSync() {
  // Retry failed API requests when connection is restored
  const cache = await caches.open(API_CACHE_NAME);
  const requests = await cache.keys();
  
  for (const request of requests) {
    try {
      const response = await fetch(request);
      if (response.ok) {
        await cache.put(request, response.clone());
      }
    } catch (error) {
      console.log('Background sync failed for:', request.url);
    }
  }
}