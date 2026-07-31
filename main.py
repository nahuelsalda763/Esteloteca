from pathlib import Path
import shutil
from uuid import uuid4

from fastapi import (
    FastAPI,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.responses import (
    HTMLResponse,
    RedirectResponse,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import database


# Carpeta principal del proyecto.
BASE_DIR = Path(__file__).resolve().parent

# Carpeta donde guardaremos las imágenes.
UPLOAD_DIR = BASE_DIR / "uploads" / "perfumes"

# Crea la carpeta si todavía no existe.
UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


app = FastAPI(title="Esteloteca")


# Archivos CSS, JavaScript e imágenes estáticas.
app.mount(
    "/static",
    StaticFiles(
        directory=str(BASE_DIR / "static")
    ),
    name="static",
)


# Imágenes subidas por los usuarios.
app.mount(
    "/uploads",
    StaticFiles(
        directory=str(BASE_DIR / "uploads")
    ),
    name="uploads",
)


# Plantillas HTML.
templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


# Crea la tabla si no existe.
database.crear_tabla()

# Agrega la columna imagen a bases anteriores.
database.asegurar_columna_imagen()


# Tipos de imágenes permitidos.
TIPOS_IMAGEN_PERMITIDOS = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def normalizar_url(
    url: str | None,
) -> str | None:
    """
    Limpia el enlace de Fragrantica.

    Devuelve None cuando está vacío.
    Agrega https:// cuando falta.
    """

    if url is None:
        return None

    url = url.strip()

    if not url:
        return None

    if not url.startswith(
        ("http://", "https://")
    ):
        url = f"https://{url}"

    return url


def guardar_imagen(
    imagen: UploadFile | None,
) -> str | None:
    """
    Guarda una imagen y devuelve su nombre.

    Si no se seleccionó ninguna imagen,
    devuelve None.
    """

    if imagen is None or not imagen.filename:
        return None

    extension = TIPOS_IMAGEN_PERMITIDOS.get(
        imagen.content_type
    )

    if extension is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Formato de imagen no permitido. "
                "Usá JPG, PNG o WebP."
            ),
        )

    # Generamos un nombre único.
    nombre_archivo = (
        f"{uuid4().hex}{extension}"
    )

    ruta_archivo = (
        UPLOAD_DIR / nombre_archivo
    )

    # Copiamos el archivo al almacenamiento local.
    with ruta_archivo.open("wb") as destino:
        shutil.copyfileobj(
            imagen.file,
            destino,
        )

    return nombre_archivo


@app.get(
    "/",
    response_class=HTMLResponse,
)
def mostrar_coleccion(
    request: Request,
):
    """
    Muestra todos los perfumes guardados.
    """

    perfumes = database.obtener_perfumes()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "perfumes": perfumes,
        },
    )


@app.get(
    "/agregar",
    response_class=HTMLResponse,
)
def mostrar_formulario(
    request: Request,
):
    """
    Muestra el formulario de perfumes.
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
    fragrantica_url: str | None = Form(None),
    imagen: UploadFile | None = File(None),
):
    """
    Recibe el formulario y guarda el perfume.
    """

    enlace_normalizado = normalizar_url(
        fragrantica_url
    )

    nombre_imagen = guardar_imagen(
        imagen
    )

    database.agregar_perfume(
        marca=marca.strip(),
        nombre=nombre.strip(),
        concentracion=concentracion,
        tamano_ml=tamano_ml,
        fragrantica_url=enlace_normalizado,
        imagen=nombre_imagen,
    )

    return RedirectResponse(
        url="/",
        status_code=303,
    )