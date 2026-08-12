if ("serviceWorker" in navigator) {

    window.addEventListener(
        "load",
        async () => {

            try {

                const registration =
                    await navigator.serviceWorker.register(
                        "/service-worker.js",
                        {
                            scope: "/"
                        }
                    );

                console.log(
                    "Service Worker registrado:",
                    registration.scope
                );

            } catch (error) {

                console.error(
                    "Error al registrar Service Worker:",
                    error
                );

            }

        }
    );

}