const CACHE_NAME = "esteloteca-static-v2";

const STATIC_ASSETS = [
    "/static/css/styles.css",
    "/static/manifest.json",
    "/static/icons/icon-192.png",
    "/static/icons/icon-512.png",
    "/static/offline.html"
];


self.addEventListener("install", (event) => {

    event.waitUntil(
        caches
            .open(CACHE_NAME)
            .then((cache) => {
                return cache.addAll(STATIC_ASSETS);
            })
    );

    self.skipWaiting();
});


self.addEventListener("activate", (event) => {

    event.waitUntil(
        caches
            .keys()
            .then((cacheNames) => {

                return Promise.all(
                    cacheNames
                        .filter((cacheName) => {
                            return cacheName !== CACHE_NAME;
                        })
                        .map((cacheName) => {
                            return caches.delete(cacheName);
                        })
                );

            })
            .then(() => {
                return self.clients.claim();
            })
    );

});


self.addEventListener("fetch", (event) => {

    if (event.request.method !== "GET") {
        return;
    }

    const requestUrl = new URL(
        event.request.url
    );


    if (
        requestUrl.origin !==
        self.location.origin
    ) {
        return;
    }


    /*
        Navegaciones HTML.

        Primero intentamos utilizar la red.
        Si FastAPI no responde, mostramos
        nuestra página offline.
    */
    if (event.request.mode === "navigate") {

        event.respondWith(
            fetch(event.request)
                .catch(() => {
                    return caches.match(
                        "/static/offline.html"
                    );
                })
        );

        return;
    }


    /*
        Recursos de /static/.

        Primero buscamos en caché.
        Si no están, los pedimos al servidor.
    */
    if (
        requestUrl.pathname.startsWith(
            "/static/"
        )
    ) {

        event.respondWith(

            caches
                .match(event.request)
                .then((respuestaCache) => {

                    if (respuestaCache) {
                        return respuestaCache;
                    }

                    return fetch(event.request)
                        .then((respuestaRed) => {

                            const copiaRespuesta =
                                respuestaRed.clone();

                            caches
                                .open(CACHE_NAME)
                                .then((cache) => {

                                    cache.put(
                                        event.request,
                                        copiaRespuesta
                                    );

                                });

                            return respuestaRed;

                        });

                })

        );

    }

});