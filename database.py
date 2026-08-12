import sqlite3
from config import DATABASE_PATH



def conectar():
    """
    Abre una conexión con SQLite.
    """

    conexion = sqlite3.connect(DATABASE_PATH)

    # Permite acceder a las columnas por nombre:
    # fila["marca"], fila["nombre"], etc.
    conexion.row_factory = sqlite3.Row

    return conexion


def crear_tabla():
    """
    Crea la tabla perfumes cuando todavía no existe.
    """

    conexion = conectar()

    try:
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS perfumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                marca TEXT NOT NULL,
                nombre TEXT NOT NULL,
                concentracion TEXT NOT NULL,
                tamano_ml INTEGER NOT NULL,
                fragrantica_url TEXT,
                imagen TEXT
            )
            """
        )

        conexion.commit()

    finally:
        conexion.close()


def asegurar_columna_imagen():
    """
    Agrega la columna imagen a las bases de datos
    creadas antes de la Etapa 4.
    """

    conexion = conectar()

    try:
        cursor = conexion.execute(
            "PRAGMA table_info(perfumes)"
        )

        columnas = {
            fila["name"]
            for fila in cursor.fetchall()
        }

        if "imagen" not in columnas:
            conexion.execute(
                """
                ALTER TABLE perfumes
                ADD COLUMN imagen TEXT
                """
            )

            conexion.commit()

    finally:
        conexion.close()


def obtener_perfumes():
    """
    Devuelve todos los perfumes guardados,
    ordenados desde el más reciente.
    """

    conexion = conectar()

    try:
        cursor = conexion.execute(
            """
            SELECT
                id,
                marca,
                nombre,
                concentracion,
                tamano_ml,
                fragrantica_url,
                imagen
            FROM perfumes
            ORDER BY id DESC
            """
        )

        filas = cursor.fetchall()

        return [
            dict(fila)
            for fila in filas
        ]

    finally:
        conexion.close()


def agregar_perfume(
    marca: str,
    nombre: str,
    concentracion: str,
    tamano_ml: int,
    fragrantica_url: str | None,
    imagen: str | None,
):
    """
    Guarda un perfume nuevo en SQLite.
    """

    conexion = conectar()

    try:
        consulta = """
            INSERT INTO perfumes (
                marca,
                nombre,
                concentracion,
                tamano_ml,
                fragrantica_url,
                imagen
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """

        valores = (
            marca,
            nombre,
            concentracion,
            tamano_ml,
            fragrantica_url,
            imagen,
        )

        conexion.execute(
            consulta,
            valores,
        )

        conexion.commit()

    finally:
        conexion.close()


def obtener_perfume_por_id(perfume_id: int):
    #Aca busca un perfume por su id, devuelve un diccionario si existe, y none si no se encuentra
    conexion = conectar()

    try:
        cursor = conexion.execute(
            """
            SELECT
                id,
                marca,
                nombre,
                concentracion,
                tamano_ml,
                fragrantica_url,
                imagen
            FROM perfumes
            WHERE id = ?
            """,
            (perfume_id,),
        )

        fila = cursor.fetchone()

        if fila is None:
            return None

        return dict(fila)

    finally:
        conexion.close()
'''
def actualizar_perfume(
        perfume_id: int,
        marca: str,
        nombre: str,
        concentracion: str,
        tamano_ml: int,
        fragrantica_url: str | None,
):
    conexion = conectar()

    try:
        conexion.execute(
            """
            UPDATE perfumes
            SET
                marca = ?,
                nombre = ?,
                concentracion = ?,
                tamano_ml = ?,
                fragrantica_url = ?
            WHERE id = ?
            """,
            (
                marca,
                nombre,
                concentracion,
                tamano_ml,
                fragrantica_url,
                perfume_id,
            ),
        )

        conexion.commit()

    finally:
        conexion.close()
'''

#Nueva Edicion de perfumes

def actualizar_perfume(
        perfume_id: int,
        marca: str,
        nombre: str,
        concentracion: str,
        tamano_ml: int,
        fragrantica_url: str | None,
        imagen: str | None,
):
    conexion = conectar()

    try:
        conexion.execute(
            """
            UPDATE perfumes
            SET
                marca = ?,
                nombre = ?,
                concentracion = ?,
                tamano_ml = ?,
                fragrantica_url = ?,
                imagen = ?
            WHERE id = ?
            """,
            (
                marca,
                nombre,
                concentracion,
                tamano_ml,
                fragrantica_url,
                imagen,
                perfume_id,
            ),
        )
        conexion.commit()
    finally:
        conexion.close()


#Eliminacion de perfumes
def eliminar_perfume(perfume_id: int) -> bool:
    conexion = conectar()

    try:
        cursor = conexion.execute(
            '''
            DELETE FROM perfumes
            WHERE id = ?
            ''',
            (perfume_id,),
        )

        conexion.commit()

        return cursor.rowcount > 0

    finally:
        conexion.close()


def buscar_perfumes(termino:str):
    conexion = conectar()

    try:
        patron_busqueda = f"%{termino}%"
        cursor = conexion.execute(
            '''
            SELECT
                id,
                marca,
                nombre,
                concentracion,
                tamano_ml,
                fragrantica_url,
                imagen
            FROM perfumes
            WHERE marca COLLATE NOCASE LIKE ?
                OR nombre COLLATE NOCASE LIKE ?
            ORDER BY
                marca COLLATE NOCASE,
                nombre COLLATE NOCASE
            ''',
            (
                patron_busqueda,
                patron_busqueda,
            ),
        )

        filas = cursor.fetchall()

        return [ dict(fila) for fila in filas]

    finally:
        conexion.close()

