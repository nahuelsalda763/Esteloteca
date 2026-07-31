from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


app = FastAPI(title="Esteloteca")


# Indicamos dónde se encuentran los archivos CSS,
# JavaScript e imágenes.
app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)


# Indicamos dónde se encuentran las plantillas HTML.
templates = Jinja2Templates(directory="templates")


# Lista temporal de perfumes.
# Más adelante será reemplazada por una base de datos SQLite.
perfumes = []


@app.get("/", response_class=HTMLResponse)
def mostrar_coleccion(request: Request):
    """
    Muestra la página principal con todos los perfumes.
    """

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"perfumes": perfumes},
    )


@app.get("/agregar", response_class=HTMLResponse)
def mostrar_formulario(request: Request):
    """
    Muestra el formulario para agregar un perfume.
    """

    return templates.TemplateResponse(
        request=request,
        name="agregar.html",
        context={},
    )


@app.post("/agregar")
def agregar_perfume(
    marca: str = Form(...),
    nombre: str = Form(...),
    concentracion: str = Form(...),
    tamano_ml: int = Form(...),
    fragrantica_url: str = Form(""),
):
    """
    Recibe los datos del formulario y agrega el perfume
    a la lista temporal.
    """

    nuevo_perfume = {
        "marca": marca,
        "nombre": nombre,
        "concentracion": concentracion,
        "tamano_ml": tamano_ml,
        "fragrantica_url": fragrantica_url,
    }

    perfumes.append(nuevo_perfume)

    return RedirectResponse(
        url="/",
        status_code=303,
    )