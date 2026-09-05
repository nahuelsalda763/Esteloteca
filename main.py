
import shutil
from uuid import uuid4
import re

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

import database_orm
from security import (
    generar_password_hash,
    validar_password,
    verificar_password,
)

from config import(
    BASE_DIR,
    UPLOAD_DIR,
    UPLOAD_ROOT,
)

from starlette.exceptions import (
    HTTPException as StarletteHTTPException,
)
from starlette.middleware.sessions import (SessionMiddleware)

from config import(
    SESSION_COOKIE_SECURE,
    SESSION_MAX_AGE,
    SESSION_SECRET_KEY,
)

app = FastAPI(title="Esteloteca")

if not SESSION_SECRET_KEY:
    raise RuntimeError(
        "SESSION_SECRET_KEY no está configurada."
    )

app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET_KEY,
    session_cookie="esteloteca_session",
    max_age=SESSION_MAX_AGE,
    same_site="lax",
    https_only=SESSION_COOKIE_SECURE,
)

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

@app.exception_handler(StarletteHTTPException)
async def manejar_error_http(
    request: Request,
    exc: StarletteHTTPException,
):
    errores = {
        400: (
            "Solicitud incorrecta",
            (
                "No pudimos procesar la solicitud. "
                "Revisá los datos e intentá nuevamente."
            ),
        ),
        403: (
            "Acceso no permitido",
            (
                "No tenes permiso para acceder "
                "a este contenido."
            ),
        ),
        404: (
            "No encontrado",
            (
                "El contenido que estás buscando "
                "no existe o ya no está disponible."
            ),
        ),
        405: (
            "Acción no permitida",
            (
                "Esta acción no está disponible "
                "desde esta página."
            ),
        ),
    }
    titulo, mensaje = errores.get(
        exc.status_code,
        (
            "Ocurrió un problema",
            str(exc.detail),
        ),
    )
    return templates.TemplateResponse(
        request = request,
        name = "error.html",
        context ={
            "titulo": titulo,
            "mensaje": mensaje,
            "status_code": exc.status_code,
        },
        status_code=exc.status_code,
    )

@app.exception_handler(Exception)
async def manejar_error_interno(
    request: Request,
    exc: Exception,
):
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={
            "titulo": "Algo salió mal",
            "mensaje": (
                "Ocurrió un error inesperado. "
                "Intentá nuevamente más tarde."
            ),
            "status_code": 500,
        },
        status_code=500,
    )

def email_valido(email:str) -> bool:
    patron=(
        r"^[^@\s]+@"
        r"[^@\s]+\."
        r"[^@\s]+$"
    )
    return bool(
        re.fullmatch(patron, email)
    )

def renderizar_registro(
        request: Request,
        *,
        error: str | None = None,
        datos: dict | None = None,
        creado: bool = False,
        status_code: int = 200,
):
    return templates.TemplateResponse(
        request=request,
        name="registro.html",
        context={
            "error":error,
            "datos":datos,
            "creado":creado,
        },
        status_code=status_code,
    )

def renderizar_login(
        request: Request,
        *,
        error: str | None = None,
        datos: dict | None = None,
        status_code: int = 200,
):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "error":error,
            "datos":datos,
        },
        status_code=status_code,
    )


def obtener_usuario_actual(request: Request,):
    user_id = request.session.get("user_id")
    if user_id is None:
        return None

    usuario = (
        database_orm
        .obtener_usuario_por_id(user_id)
    )

    if (
        usuario is None
        or not usuario.is_active
    ):
        request.session.clear()
        return None

    return usuario

def requerir_usuario(request: Request):
    return obtener_usuario_actual(request)

def requerir_propiedad_item(item_id: int, usuario_actual):
    item = (
        database_orm
        .obtener_item_coleccion_por_id(item_id)
    )

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Elemento de colección no encontrado. ",
        )

    es_propietario = (
        database_orm
        .usuario_es_propietario_del_item(
            item_id=item_id,
            user_id=usuario_actual.id,
        )
    )

    if not es_propietario:
        raise HTTPException(
            status_code=403,
            detail=(
                "No tenés permiso para modificar "
                "este elemento de la colección."
            ),
        )

    return item

def requerir_propiedad_coleccion(collection_id: int, usuario_actual):
    coleccion = (
        database_orm
        .obtener_coleccion_por_id(collection_id)
    )

    if coleccion is None:
        raise HTTPException(
            status_code= 404,
            detail= "Colección no encontrada.",
        )

    if coleccion.owner_id != usuario_actual.id:
        raise HTTPException(
            status_code=403,
            detail = (
                "No tenés permiso para modificar "
                "esta colección."
            )
        )

    return coleccion


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

def mostrar_coleccion(request: Request, buscar: str = ""):
    usuario_actual = obtener_usuario_actual(request)

    if usuario_actual is None:
        return templates.TemplateResponse(
            request = request,
            name = "bienvenida.html",
            context = {},
        )

    coleccion = (
        database_orm
        .obtener_coleccion_principal_por_usuario(usuario_actual.id)
    )
    if coleccion is None:
        raise HTTPException(
            status_code=500,
            detail=(
                "El usuario autenticado no tiene "
                "una colección principal."          
            ),
        )

    termino_busqueda = buscar.strip()

    todos_los_items = (
        database_orm
        .obtener_items_por_coleccion(coleccion.id)
    )

    if termino_busqueda:
        items = (
            database_orm
            .buscar_items_por_coleccion(
                coleccion.id,
                termino_busqueda,
            )
        )

    else:
        items = todos_los_items

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "items": items,
            "buscar": termino_busqueda,
            "total_perfumes": len(todos_los_items),
        },
    )

@app.get(
        "/catalogo",
        response_class=HTMLResponse,
)

def mostrar_catalogo(request: Request, buscar: str = ""):
    termino_busqueda = buscar.strip()

    if termino_busqueda:
        perfumes_catalogo = (
            database_orm
            .buscar_catalogo_perfumes(termino_busqueda)
        )

    else:
        perfumes_catalogo = (
            database_orm
            .obtener_catalogo_perfumes()
        )

    usuario_actual = obtener_usuario_actual(request)

    return templates.TemplateResponse(
        request = request,
        name = "catalogo.html",
        context = {
            "perfumes": perfumes_catalogo,
            "buscar": termino_busqueda,
            "total_perfumes": len(perfumes_catalogo),
            "usuario_actual": usuario_actual,
        },
    )

@app.get(
        "/perfume/{item_id}",
        response_class=HTMLResponse,
)

def mostrar_detalle_perfume(
    request:Request,
    item_id: int,
):
    item =(
        database_orm
        .obtener_item_coleccion_por_id(item_id)
    )

    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Perfume no encontrado.",
        )

    usuario_actual = obtener_usuario_actual(request)
    user_id = (
        usuario_actual.id
        if usuario_actual is not None
        else None
    )

    puede_ver = (
        database_orm
        .usuario_puede_ver_item(
            item_id=item_id,
            user_id=user_id,
        )
    )

    if not puede_ver:
        raise HTTPException(
            status_code=404,
            detail="Perfume no disponible.",
        )

    puede_modificar = False
    if usuario_actual is not None:
        puede_modificar = (
            database_orm
            .usuario_es_propietario_del_item(
                item_id = item_id,
                user_id = usuario_actual.id,
            )
        )

        return templates.TemplateResponse(
            request=request,
            name="detalle.html",
            context={
                "item": item,
                "puede_modificar": puede_modificar
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

    usuario_actual = requerir_usuario(request)

    if usuario_actual is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    return templates.TemplateResponse(
        request=request,
        name="agregar.html",
        context={},
    )


@app.post("/agregar")
def agregar_perfume(
    request : Request,
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

    usuario_actual = requerir_usuario(request)

    if usuario_actual is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    coleccion = (
        database_orm
        .obtener_coleccion_principal_por_usuario(usuario_actual.id)
    )
    if coleccion is None:
        raise HTTPException(
            status_code=500,
            detail=(
                "El usuario autenticado "
                "no tiene una colección."
            )
        )

    enlace_normalizado = normalizar_url(
        fragrantica_url
    )

    nombre_imagen = guardar_imagen(
        imagen
    )

    database_orm.agregar_item_coleccion(
        marca=marca.strip(),
        nombre=nombre.strip(),
        concentracion=concentracion,
        tamano_ml=tamano_ml,
        fragrantica_url=enlace_normalizado,
        imagen=nombre_imagen,
        collection_id=coleccion.id,
    )

    return RedirectResponse(
        url="/?estado=agregado",
        status_code=303,
    )


@app.get(
    "/editar/{item_id}",
    response_class=HTMLResponse,
)
def mostrar_formulario_edicion(
    request: Request,
    item_id: int,
):
    usuario_actual = requerir_usuario(request)

    if usuario_actual is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    item = requerir_propiedad_item(
        item_id=item_id,
        usuario_actual=usuario_actual,
    )

    return templates.TemplateResponse(
        request=request,
        name="editar.html",
        context={
            "item": item,
            "error": None,
        },
    )


@app.post("/editar/{item_id}")
def editar_perfume(
    request: Request,
    item_id: int,
    tamano_ml: int = Form(...),
    fragrantica_url: str | None = Form(None),
    imagen: UploadFile | None = File(None),
    eliminar_imagen: bool = Form(False),
):
    """
    Actualiza los datos personales de un perfume
    dentro de la colección del usuario.

    La identidad global del perfume se conserva.
    """

    usuario_actual = requerir_usuario(request)

    if usuario_actual is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    item = requerir_propiedad_item(
        item_id=item_id,
        usuario_actual=usuario_actual,
    )

    # Evitamos una acción contradictoria:
    # seleccionar una imagen nueva y pedir
    # eliminar la imagen al mismo tiempo.
    if (
        eliminar_imagen
        and imagen is not None
        and imagen.filename
    ):
        return templates.TemplateResponse(
            request=request,
            name="editar.html",
            context={
                "item": item,
                "tamano_ml_formulario": tamano_ml,
                "fragrantica_url_formulario": (
                    fragrantica_url or ""
                ),
                "error": (
                    "No podés seleccionar una imagen "
                    "nueva y eliminar la actual "
                    "al mismo tiempo."
                ),
            },
            status_code=400,
        )

    enlace_normalizado = normalizar_url(
        fragrantica_url
    )

    imagen_actual = item.imagen

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
        database_orm.actualizar_item_coleccion(
            item_id=item_id,
            tamano_ml=tamano_ml,
            fragrantica_url=enlace_normalizado,
            imagen=imagen_final,
            user_id=usuario_actual.id,
        )
    )

    if not actualizado:
        raise HTTPException(
            status_code=404,
            detail="No se pudo actualizar el perfume",
        )

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
        url=(
            f"/perfume/{item_id}"
            "?estado=editado"
        ),
        status_code=303,
    )

@app.get(
    "/eliminar/{item_id}",
    response_class=HTMLResponse,
)
def mostrar_confirmacion_eliminacion(
    request: Request,
    item_id: int,
):
    usuario_actual = requerir_usuario(request)

    if usuario_actual is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    item = requerir_propiedad_item(
        item_id=item_id,
        usuario_actual=usuario_actual,
    )


    return templates.TemplateResponse(
        request=request,
        name="eliminar.html",
        context={
            "item": item,
        },
    )


@app.post("/eliminar/{item_id}")
def procesar_eliminacion(
    request: Request,
    item_id: int,
):
    usuario_actual = requerir_usuario(request)

    if usuario_actual is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    item = requerir_propiedad_item(
        item_id=item_id,
        usuario_actual=usuario_actual,
    )

    nombre_imagen = item.imagen

    eliminado = (
        database_orm.eliminar_item_coleccion(
            item_id=item_id,
            user_id=usuario_actual.id,
        )
    )

    if not eliminado:
        raise HTTPException(
            status_code=404,
            detail="No se pudo eliminar el perfume",
        )

    eliminar_imagen_local(nombre_imagen)

    return RedirectResponse(
        url="/?estado=eliminado",
        status_code=303,
    )

@app.get(
    "/registro",
    response_class=HTMLResponse,
)

def mostrar_registro(
    request: Request,
    creado: bool = False,
):
    return renderizar_registro(
        request,
        creado=creado,
    )

@app.post(
    "/registro",
    response_class=HTMLResponse,
)

def registrar_usuario(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
):
    username = (
        username
        .strip()
        .lower()
    )

    email = (
        email
        .strip()
        .lower()
    )

    datos = {
        "username": username,
        "email": email,
    }

    if not(
        3 <= len(username) <= 50
    ):
        return renderizar_registro(
            request,
            error=(
                "El nombre de usuario debe "
                "tener entre 3 y 50 caracteres."
            ),
            datos=datos,
            status_code=400,
        )

    if not re.fullmatch(
        r"[a-z0-9_]+",
        username,
    ):
        return renderizar_registro(
            request,
            error=(
                "El nombre de usuario solo "
                "puede contener letras, "
                "números y guion bajo"
            ),
            datos=datos,
            status_code=400,
        )

    if len(email) > 255:
        return renderizar_registro(
            request,
            error=(
                "EL correo electrónico "
                "es demasiado largo."
            ),
            datos=datos,
            status_code=400,
        )
    error_password = validar_password(password)

    if error_password:
        return renderizar_registro(
            request,
            error=error_password,
            datos=datos,
            status_code=400,
        )


    if password != password_confirm:
        return renderizar_registro(
            request,
            error=(
                "Las contraseñas "
                "no coinciden."
            ),
            datos=datos,
            status_code=400,
        )

    usuario_existente = (
        database_orm
        .obtener_usuario_por_username(username)
    )

    if usuario_existente:
        return renderizar_registro(
            request,
            error=(
                "Ese nombre de usuario "
                "ya está registrado."
            ),
            datos=datos,
            status_code=409,
        )

    email_existente = (
        database_orm
        .obtener_usuario_por_email(email)
    )

    if email_existente:
        return renderizar_registro(
            request,
            error=(
                "Ese correo electrónico "
                "ya está registrado."
            ),
            datos=datos,
            status_code=409,
        )

    hash_password = (
        generar_password_hash(password)
    )

    database_orm.agregar_usuario(
        username=username,
        email=email,
        password_hash=hash_password,
    )

    return RedirectResponse(
        url="/registro?creado=true",
        status_code=303,
    )

@app.get(
    "/login",
    response_class=HTMLResponse,
)

def mostrar_login(
    request: Request,
):
    return renderizar_login(request)

@app.post(
    "/login",
    response_class=HTMLResponse,
)

def iniciar_sesion(
    request: Request,
    identificador: str = Form(...),
    password: str = Form(...),
):
    identificador = (
        identificador
        .strip()
        .lower()
    )

    datos = {"identificador": identificador}

    usuario = (
        database_orm
        .obtener_usuario_por_identificador(identificador)
    )

    if (
        usuario is None
        or not usuario.is_active
    ):
        return renderizar_login(
            request,
            error=(
                "El usuario, correo electrónico "
                "o la contraseña son incorrectos."
            ),
            datos=datos,
            status_code=401,
        )

    password_correcta = (
        verificar_password(password, usuario.password_hash)
    )

    if not password_correcta:
        return renderizar_login(
            request,
            error = (
                "El usuario, correo electrónico "
                "o la contraseña son incorrectos."
            ),
            datos=datos,
            status_code=401,
        )

    request.session.clear()

    request.session["user_id"] = usuario.id
    return RedirectResponse(
        url="/login",
        status_code=303,
    )

@app.get(
        "/perfil",
        response_class = HTMLResponse,
)

def mostrar_mi_perfil(request:Request):
    usuario_actual = requerir_usuario(request)

    if usuario_actual is None:
        return RedirectResponse(
            url="/login",
            status_code=303,
        )

    return RedirectResponse(
        url=f"/usuarios/{usuario_actual.username}",
        status_code=303,
    )

@app.get(
        "/usuarios/{username}",
        response_class=HTMLResponse,
)

def mostrar_perfil_usuario(request: Request, username: str):
    username_normalizado = (
        username
        .strip()
        .lower()
    )

    usuario = (
        database_orm
        .obtener_usuario_por_username(username_normalizado)
    )

    if usuario is None or not usuario.is_active:
        raise HTTPException(
            status_code=404,
            detail="Perfil no encontrado.",
        )

    usuario_actual = obtener_usuario_actual(request)

    es_perfil_propio = (usuario_actual is not None and usuario_actual.id == usuario.id)

    coleccion = (
        database_orm
        .obtener_coleccion_principal_por_usuario(usuario.id)
    )

    cantidad_perfumes = None

    if es_perfil_propio:
        cantidad_perfumes = len(
            database_orm
            .obtener_ids_items_por_usuario(usuario.id)
        )

    puede_ver_coleccion = (
        coleccion is not None
        and (
            es_perfil_propio or coleccion.is_public
        )
    )

    return templates.TemplateResponse(
        request= request,
        name= "perfil.html",
        context = {
            "usuario": usuario,
            "es_perfil_propio": es_perfil_propio,
            "coleccion": coleccion,
            "cantidad_perfumes": cantidad_perfumes,
            "puede_ver_coleccion": puede_ver_coleccion,
        },
    )

@app.get(
        "/usuarios/{username}/coleccion",
        response_class=HTMLResponse,
)

def mostar_coleccion_usuario(request: Request, username: str):
    username_normalizado = (
        username
        .strip()
        .lower()
    )

    usuario = (
        database_orm
        .obtener_usuario_por_username(username_normalizado)
    )

    if usuario is None or not usuario.is_active:
        raise HTTPException(
            status_code= 404,
            detail= "Perfil no encontrado.",
        )

    coleccion = (
        database_orm
        .obtener_coleccion_principal_por_usuario(usuario.id)
    )

    if coleccion is None:
        raise HTTPException(
            status_code= 404,
            detail="Colección no encontrada.",
        )

    usuario_actual = obtener_usuario_actual(request)

    es_propietario = (
        usuario_actual is not None
        and usuario_actual.id == usuario.id
    )

    if (
        not es_propietario
        and not coleccion.is_public
    ):
        raise HTTPException(
            status_code=404,
            detail="Colección no disponible.",
        )

    items = (
        database_orm
        .obtener_items_por_coleccion(coleccion.id)
    )

    return templates.TemplateResponse(
        request=request,
        name="coleccion_publica.html",
        context={
            "usuario": usuario,
            "coleccion": coleccion,
            "items": items,
            "es_propietario": es_propietario,
        },
    )



@app.post(
        "/colecciones/{collection_id}/visibilidad",
)

def cambiar_visibilidad_coleccion(
    request: Request,
    collection_id: int,
    is_public: bool = Form(...),
):
    usuario_actual = requerir_usuario(request)

    if usuario_actual is None:
        return RedirectResponse(
            url="/login",
            status_code= 303,
        )

    requerir_propiedad_coleccion(
        collection_id = collection_id,
        usuario_actual = usuario_actual,
    )

    actualizada = (
        database_orm
        .actualizar_visibilidad_coleccion(
            collection_id = collection_id,
            user_id = usuario_actual.id,
            is_public = is_public,
        )
    )

    if not actualizada:
        raise HTTPException(
            status_code= 404,
            detail = "No se pudo actualizar la colección",
        )

    return RedirectResponse(
        url = f"/usuarios/{usuario_actual.username}",
        status_code = 303,
    )



@app.post(
    "/logout",
)
def cerrar_sesion(
    request: Request
):
    request.session.clear()

    return RedirectResponse(
        url="/login?estado=cerrada",
        status_code=303,
    )