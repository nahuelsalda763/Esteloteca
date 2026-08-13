const notificacion = document.querySelector( ".notificacion");
if (notificacion) {
    setTImeout(
        () => {
            notificaciones.classList.add("notificacion-coluta");
        },
        3500
    );

    const url = new URL(window.location.href);
    if (url.searchParams.has("estado")){
        url.searchParams.delete("estado");
        window.history.replaceState(
            {},
            "",
            url
        );
    }
}