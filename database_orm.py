import unicodedata

from sqlalchemy import (create_engine, or_, select)
from sqlalchemy.orm import Session, joinedload

from config import DATABASE_URL
from models import Collection, CollectionItem, Perfume, User


engine = create_engine(
    DATABASE_URL,
)


def normalizar_valor_catalogo(valor: str) -> str:
    texto = unicodedata.normalize("NFKC", valor)
    texto = " ".join(texto.strip().split())
    return texto.casefold()


def crear_clave_catalogo(
    marca: str,
    nombre: str,
    concentracion: str,
) -> str:
    return "|".join(
        (
            normalizar_valor_catalogo(marca),
            normalizar_valor_catalogo(nombre),
            normalizar_valor_catalogo(concentracion),
        )
    )


def obtener_catalogo_perfumes():
    sentencia = (
        select(Perfume)
        .order_by(
            Perfume.marca,
            Perfume.nombre,
            Perfume.concentracion,
        )
    )

    with Session(engine) as session:
        return session.scalars(sentencia).all()


def buscar_catalogo_perfumes(termino: str):
    termino = termino.strip()

    if not termino:
        return obtener_catalogo_perfumes()

    patron = f"%{termino}%"

    sentencia = (
        select(Perfume)
        .where(
            or_(
                Perfume.marca.ilike(patron),
                Perfume.nombre.ilike(patron),
                Perfume.concentracion.ilike(patron),
            )
        )
        .order_by(
            Perfume.marca,
            Perfume.nombre,
            Perfume.concentracion,
        )
    )

    with Session(engine) as session:
        return session.scalars(sentencia).all()


def obtener_coleccion_principal_por_usuario(user_id: int):
    sentencia = (
        select(Collection)
        .where(Collection.owner_id == user_id)
        .order_by(Collection.id)
        .limit(1)
    )

    with Session(engine) as session:
        return session.scalar(sentencia)


def obtener_coleccion_por_id(collection_id: int):
    with Session(engine) as session:
        return session.get(Collection, collection_id)


def actualizar_visibilidad_coleccion(
    collection_id: int,
    user_id: int,
    is_public: bool,
) -> bool:
    sentencia = (
        select(Collection)
        .where(
            Collection.id == collection_id,
            Collection.owner_id == user_id,
        )
    )

    with Session(engine) as session:
        coleccion = session.scalar(sentencia)

        if coleccion is None:
            return False

        coleccion.is_public = is_public
        session.commit()
        return True


def obtener_items_por_coleccion(collection_id: int):
    sentencia = (
        select(CollectionItem)
        .options(
            joinedload(CollectionItem.perfume)
        )
        .where(
            CollectionItem.collection_id == collection_id
        )
        .order_by(CollectionItem.id.desc())
    )

    with Session(engine) as session:
        return session.scalars(sentencia).all()


def buscar_items_por_coleccion(
    collection_id: int,
    termino: str,
):
    termino = termino.strip()

    if not termino:
        return obtener_items_por_coleccion(collection_id)

    patron = f"%{termino}%"

    sentencia = (
        select(CollectionItem)
        .join(
            Perfume,
            CollectionItem.perfume_id == Perfume.id,
        )
        .options(
            joinedload(CollectionItem.perfume)
        )
        .where(
            CollectionItem.collection_id == collection_id,
            or_(
                Perfume.marca.ilike(patron),
                Perfume.nombre.ilike(patron),
            ),
        )
        .order_by(
            Perfume.marca,
            Perfume.nombre,
        )
    )

    with Session(engine) as session:
        return session.scalars(sentencia).all()


def obtener_item_coleccion_por_id(item_id: int):
    sentencia = (
        select(CollectionItem)
        .options(
            joinedload(CollectionItem.perfume)
        )
        .where(CollectionItem.id == item_id)
    )

    with Session(engine) as session:
        return session.scalar(sentencia)


def usuario_es_propietario_del_item(
    item_id: int,
    user_id: int,
) -> bool:
    sentencia = (
        select(CollectionItem.id)
        .join(
            Collection,
            CollectionItem.collection_id == Collection.id,
        )
        .where(
            CollectionItem.id == item_id,
            Collection.owner_id == user_id,
        )
    )

    with Session(engine) as session:
        return session.scalar(sentencia) is not None


def usuario_puede_ver_item(
    item_id: int,
    user_id: int | None,
) -> bool:
    sentencia = (
        select(CollectionItem.id)
        .join(
            Collection,
            CollectionItem.collection_id == Collection.id,
        )
        .where(CollectionItem.id == item_id)
    )

    if user_id is None:
        sentencia = sentencia.where(
            Collection.is_public.is_(True)
        )

    else:
        sentencia = sentencia.where(
            or_(
                Collection.is_public.is_(True),
                Collection.owner_id == user_id,
            )
        )

    with Session(engine) as session:
        return session.scalar(sentencia) is not None


def obtener_ids_items_por_usuario(user_id: int) -> set[int]:
    sentencia = (
        select(CollectionItem.id)
        .join(
            Collection,
            CollectionItem.collection_id == Collection.id,
        )
        .where(Collection.owner_id == user_id)
    )

    with Session(engine) as session:
        return set(session.scalars(sentencia).all())


def agregar_item_coleccion(
    marca: str,
    nombre: str,
    concentracion: str,
    tamano_ml: int,
    fragrantica_url: str | None,
    imagen: str | None,
    collection_id: int,
) -> int:
    catalog_key = crear_clave_catalogo(
        marca,
        nombre,
        concentracion,
    )

    with Session(engine) as session:
        perfume_global = session.scalar(
            select(Perfume)
            .where(Perfume.catalog_key == catalog_key)
        )

        if perfume_global is None:
            perfume_global = Perfume(
                marca=marca.strip(),
                nombre=nombre.strip(),
                concentracion=concentracion.strip(),
                catalog_key=catalog_key,
                fragrantica_url=fragrantica_url,
            )
            session.add(perfume_global)
            session.flush()

        elif (
            not perfume_global.fragrantica_url
            and fragrantica_url
        ):
            perfume_global.fragrantica_url = fragrantica_url

        item = CollectionItem(
            collection_id=collection_id,
            perfume_id=perfume_global.id,
            tamano_ml=tamano_ml,
            imagen=imagen,
        )

        session.add(item)
        session.commit()
        session.refresh(item)

        return item.id


def actualizar_item_coleccion(
    item_id: int,
    tamano_ml: int,
    fragrantica_url: str | None,
    imagen: str | None,
    user_id: int,
) -> bool:
    sentencia = (
        select(CollectionItem)
        .join(
            Collection,
            CollectionItem.collection_id == Collection.id,
        )
        .options(
            joinedload(CollectionItem.perfume)
        )
        .where(
            CollectionItem.id == item_id,
            Collection.owner_id == user_id,
        )
    )

    with Session(engine) as session:
        item = session.scalar(sentencia)

        if item is None:
            return False

        item.tamano_ml = tamano_ml
        item.imagen = imagen

        if (
            fragrantica_url
            and not item.perfume.fragrantica_url
        ):
            item.perfume.fragrantica_url = fragrantica_url

        session.commit()
        return True


def eliminar_item_coleccion(
    item_id: int,
    user_id: int,
) -> bool:
    sentencia = (
        select(CollectionItem)
        .join(
            Collection,
            CollectionItem.collection_id == Collection.id,
        )
        .where(
            CollectionItem.id == item_id,
            Collection.owner_id == user_id,
        )
    )

    with Session(engine) as session:
        item = session.scalar(sentencia)

        if item is None:
            return False

        session.delete(item)
        session.commit()

        return True


def obtener_usuario_por_username(username: str):
    sentencia = (
        select(User)
        .where(User.username == username)
    )

    with Session(engine) as session:
        return session.scalar(sentencia)


def obtener_usuario_por_email(email: str):
    sentencia = (
        select(User)
        .where(User.email == email)
    )

    with Session(engine) as session:
        return session.scalar(sentencia)


def obtener_usuario_por_identificador(identificador: str):
    sentencia = (
        select(User)
        .where(
            or_(
                User.username == identificador,
                User.email == identificador,
            )
        )
    )

    with Session(engine) as session:
        return session.scalar(sentencia)


def obtener_usuario_por_id(user_id: int):
    with Session(engine) as session:
        return session.get(User, user_id)


def agregar_usuario(
    username: str,
    email: str,
    password_hash: str,
):
    usuario = User(
        username=username,
        email=email,
        password_hash=password_hash,
    )

    with Session(engine) as session:
        session.add(usuario)
        session.flush()

        coleccion = Collection(
            owner_id=usuario.id,
            name="Mi colección",
            description=None,
            is_public=False,
        )

        session.add(coleccion)
        session.commit()
        session.refresh(usuario)

        return usuario
