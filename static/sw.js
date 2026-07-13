const CACHE_NAME = 'ibinovi-v1.0.0';
const urlsToCache = [
  '/',
  '/static/img/logo.png',
  '/static/manifest.json',
  '/static/css/style.css',
  'https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&family=Playfair+Display:wght@400;600;700&family=Inter:wght@400;600;700&display=swap',
  'https://cdn.tailwindcss.com'
];

// Instalação do Service Worker
self.addEventListener('install', event => {
  console.log('Service Worker: Instalado');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: Cacheando arquivos essenciais');
        return cache.addAll(urlsToCache);
      })
      .catch(error => {
        console.log('Service Worker: Falha ao cachear', error);
      })
  );
});

// Ativação do Service Worker
self.addEventListener('activate', event => {
  console.log('Service Worker: Ativado');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('Service Worker: Removendo cache antigo', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Interceptação de requisições
self.addEventListener('fetch', event => {
  // Estratégia: Cache First para arquivos estáticos
  if (event.request.url.includes('/static/') || 
      event.request.url.includes('fonts.googleapis.com') ||
      event.request.url.includes('cdn.tailwindcss.com')) {
    
    event.respondWith(
      caches.match(event.request)
        .then(response => {
          // Cache hit - retorna resposta do cache
          if (response) {
            return response;
          }

          // Cache miss - busca na rede
          return fetch(event.request).then(response => {
            // Verifica se resposta é válida
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // Clona a resposta para armazenar no cache
            const responseToCache = response.clone();
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });

            return response;
          });
        })
    );
  } else {
    // Para páginas dinâmicas, usa Network First com fallback para cache
    event.respondWith(
      fetch(event.request)
        .then(response => {
          // Se a requisição for bem-sucedida, armazena no cache
          if (response.status === 200) {
            const responseToCache = response.clone();
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });
          }
          return response;
        })
        .catch(() => {
          // Se falhar, tenta do cache
          return caches.match(event.request);
        })
    );
  }
});

// Background Sync para sincronização quando voltar online
self.addEventListener('sync', event => {
  if (event.tag === 'background-sync') {
    console.log('Service Worker: Background sync');
    event.waitUntil(
      // Aqui podemos sincronizar dados pendentes
      Promise.resolve()
    );
  }
});

// Push Notifications
self.addEventListener('push', event => {
  console.log('Service Worker: Push notification recebida');
  
  const options = {
    body: event.data ? event.data.text() : 'Nova notificação da IBINOVI',
    icon: '/static/img/icons/icon-192x192.png',
    badge: '/static/img/icons/icon-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Ver detalhes',
        icon: '/static/img/icons/icon-96x96.png'
      },
      {
        action: 'close',
        title: 'Fechar',
        icon: '/static/img/icons/icon-96x96.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('IBINOVI', options)
  );
});

// Handle notification click
self.addEventListener('notificationclick', event => {
  console.log('Service Worker: Notification click');
  
  event.notification.close();

  if (event.action === 'explore') {
    // Abre o aplicativo
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Cache cleanup periódico
self.addEventListener('message', event => {
  if (event.data && event.data.type === 'CACHE_CLEANUP') {
    console.log('Service Worker: Cache cleanup solicitado');
    event.waitUntil(
      caches.open(CACHE_NAME).then(cache => {
        return cache.keys().then(requests => {
          return Promise.all(
            requests
              .filter(request => {
                // Remove arquivos antigos ou não utilizados
                return !urlsToCache.includes(request.url);
              })
              .map(request => {
                console.log('Service Worker: Removendo do cache', request.url);
                return cache.delete(request);
              })
          );
        });
      })
    );
  }
});
