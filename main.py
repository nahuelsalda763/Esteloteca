
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
    FileResponse,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import database
import database_orm
from config import(
    BASE_DIR,
    UPLOAD_DIR,
    UPLOAD_ROOT,
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
        directory=str(
            UPLOAD_ROOT
        )
    ),
    name="uploads"
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

#SERVICE WORKER
@app.get(
        "/service-worker.js",
        include_in_schema = False,
)

def obtener_service_worker():
    return FileResponse(
        BASE_DIR
        / "static"
        / "service-worker.js",
        media_type="application/javascript",
        headers = {
            "Cache-Control": "no-cache",
        },
    )

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

def eliminar_imagen_local(nombre_imagen: str | None,):
    if not nombre_imagen:
        return

    ruta_imagen = UPLOAD_DIR / nombre_imagen
    ruta_imagen.unlink(missing_ok = True)
    


@app.get(
        "/",
        response_class = HTMLResponse,
)

def mostrar_coleccion(
    request: Request,
    buscar: str = "",
):
    termino_busqueda = buscar.strip()
    todos_los_perfumes = (database_orm.obtener_perfumes())

    if termino_busqueda:
        perfumes = (
            database_orm.buscar_perfumes(
                termino_busqueda
            )
        )

    else:
        perfumes = todos_los_perfumes

    return templates.TemplateResponse(
        request = request,
        name = "index.html",
        context ={
            "perfumes": perfumes,
            "buscar": termino_busqueda,
            "total_perfumes": len(todos_los_perfumes),
        },
    )

@app.get(
        "/perfume/{perfume_id}",
        response_class=HTMLResponse,
)
def mostrar_detalle_perfume(request: Request, perfume_id: int,):
    #perfume = database.obtener_perfume_por_id(perfume_id)
    perfume = database_orm.obtener_perfume_por_id(perfume_id)
    if perfume is None:
        raise HTTPException(
            status_code = 404,
            detail = "Perfume no encontrado",
        )

    return templates.TemplateResponse(
        request=request,
        name="detalle.html",
        context={"perfume" : perfume,},
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

    database_orm.agregar_perfume(
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


@app.get(
    "/editar/{perfume_id}",
    response_class = HTMLResponse,
)

def mostrar_formulario_edicion(
    request : Request,
    perfume_id: int,
):
    perfume = (
        database_orm.obtener_perfume_por_id(perfume_id)
    )

    if perfume is None:
        raise HTTPException(
            status_code = 404,
            detail = "Perfume no encontrado",
        )

    return templates.TemplateResponse(
        request = request,
        name = "editar.html",
        context={
            "perfume": perfume,
        },
    )


@app.post("/editar/{perfume_id}")
def editar_perfume(
    perfume_id: int,
    marca: str = Form(...),
    nombre: str = Form(...),
    concentracion: str = Form(...),
    tamano_ml: int = Form(...),
    fragrantica_url: str | None = Form(None),
    imagen: UploadFile | None = File(None),
    eliminar_imagen: bool = Form(False),
):
    """
    Actualiza los datos de un perfume.

    También permite conservar, reemplazar
    o eliminar su imagen.
    """

    perfume = (
        database_orm.obtener_perfume_por_id(perfume_id)
    )
    if perfume is None:
        raise HTTPException(
            status_code=404,
            detail="Perfume no encontrado",
        )

    # Evitamos una acción contradictoria:
    # seleccionar una imagen nueva y pedir
    # eliminar la imagen al mismo tiempo.
    if (
        eliminar_imagen
        and imagen is not None
        and imagen.filename
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "No podés seleccionar una imagen nueva "
                "y eliminar la imagen al mismo tiempo."
            ),
        )

    enlace_normalizado = normalizar_url(
        fragrantica_url
    )

    imagen_actual = perfume.imagen

    # Por defecto conservamos la imagen anterior.
    imagen_final = imagen_actual

    # Caso 1:
    # El usuario quiere eliminar la imagen.
    if eliminar_imagen:
        imagen_final = None

    # Caso 2:
    # El usuario seleccionó una imagen nueva.
    elif imagen is not None and imagen.filename:
        imagen_final = guardar_imagen(
            imagen
        )

    actualizado = (
        database_orm.actualizar_perfume(
            perfume_id = perfume_id,
            marca = marca.strip(),
            nombre = nombre.strip(),
            concentracion = concentracion,
            tamano_ml = tamano_ml,
            fragrantica_url = enlace_normalizado,
            imagen = imagen_final,
        )
    )

    if not actualizado:
        raise HTTPException( status_code = 404, detail="No se pudo actualizar el perfume",)



    # Si quitamos la imagen anterior,
    # eliminamos también su archivo.
    if eliminar_imagen:
        eliminar_imagen_local(
            imagen_actual
        )

    # Si reemplazamos una imagen,
    # eliminamos la anterior.
    elif (
        imagen_final != imagen_actual
        and imagen_actual
    ):
        eliminar_imagen_local(
            imagen_actual
        )

    return RedirectResponse(
        url=f"/perfume/{perfume_id}",
        status_code=303,
    )

@app.get(
    "/eliminar/{perfume_id}",
    response_class = HTMLResponse,
)
def mostrar_confirmacion_eliminacion(
    request: Request,
    perfume_id: int,
):
    perfume = (
        database_orm.obtener_perfume_por_id(perfume_id)
    )

    if perfume is None:
        raise HTTPException(
            status_code = 404,
            detail = "Perfume no encontrado",
        )

    return templates.TemplateResponse(
        request = request,
        name = "eliminar.html",
        context={
            "perfume" : perfume,
        }
    )

@app.post("/eliminar/{perfume_id}")
def procesar_eliminacion( perfume_id : int,):
    perfume = (
        database_orm.obtener_perfume_por_id(perfume_id)
    )

    if perfume is None:
        raise HTTPException(
            status_code = 404,
            detail = "Perfume no encontrado",
        )
    nombre_imagen = perfume.imagen

    eliminado = (
        database_orm.eliminar_perfume(perfume_id)
    )

    if not eliminado:
        raise HTTPException(
            status_code = 404,
            detail = "No se pudo eliminar el perfume",
        )

    eliminar_imagen_local(nombre_imagen)

    return RedirectResponse(
        url = "/",
        status_code = 303,
    )

