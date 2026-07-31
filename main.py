from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import database


app = FastAPI(title="Esteloteca")

#Aca indicamos donde se encuentran los archivos css, js e imagenes

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name = "static",
)

#aca donde se encuentra las plantillas html
templates = Jinja2Templates(directory="templates")

#Aca se crea la tabla cuando inicia la aplicacion. SI esta existe, sqlite no la vuelve a crear
database.crear_tabla()

def normalizar_url(url: str | None) -> str | None:
    """
    Limpia y normaliza una dirección web.

    Devuelve None cuando el campo está vacío.
    Agrega https:// cuando el usuario no lo escribió.
    """

    if url is None:
        return None

    url = url.strip()

    if not url or url.lower() in {"none", "null"}:
        return None

    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    return url

@app.get("/", response_class = HTMLResponse)
def mostrar_coleccion(request : Request):
    perfumes = database.obtener_perfumes()

    return templates.TemplateResponse(
        request = request,
        name = "index.html",
        context = {"perfumes" : perfumes},
    )

@app.get("/agregar", response_class = HTMLResponse)
def mostrar_formulario(request: Request):

    return templates.TemplateResponse(
        request = request,
        name = "agregar.html",
        context = {}
    )


@app.post("/agregar")
def agregar_perfume(
    marca: str = Form(...),
    nombre: str = Form(...),
    concentracion: str = Form(...),
    tamano_ml: int = Form(...),
    fragrantica_url: str | None = Form(None),
):
    enlace_normalizado = normalizar_url(fragrantica_url)

    database.agregar_perfume(
        marca=marca.strip(),
        nombre=nombre.strip(),
        concentracion=concentracion,
        tamano_ml=tamano_ml,
        fragrantica_url=enlace_normalizado,
    )

    return RedirectResponse(
        url="/",
        status_code=303,
    )