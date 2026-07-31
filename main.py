from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates



app = FastAPI(title="Esteloteca")

#Indico donde se ubican los archivos css js e imagenes

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)

#Indico donde se encuentran los html

templates = Jinja2Templates(directory="templates")


#TEMPORALMENTE USAMOS ESTOS DATOS TEMPORALES PARA PROBAR LA APLICACION
#MAS ADELANTE SE CAMBIA POR SQLITE

# Datos temporales para probar la aplicación.
# Más adelante serán reemplazados por SQLite.
perfumes = [
    {
        "marca": "Dior",
        "nombre": "Homme Intense",
        "concentracion": "Eau de Parfum",
        "tamano_ml": 100,
        "fragrantica_url": "https://www.fragrantica.es/",
    },
    {
        "marca": "Lattafa",
        "nombre": "Khamrah",
        "concentracion": "Eau de Parfum",
        "tamano_ml": 100,
        "fragrantica_url": "https://www.fragrantica.es/",
    },
]


@app.get("/", response_class=HTMLResponse)
def mostrar_coleccion(request : Request):
    """
    Muestra la pagina principal de la coleccion de perfumes
    
    """
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"perfumes": perfumes},

    )