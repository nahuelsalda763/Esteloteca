from pathlib import Path
import sqlite3

#Carpeta donde se ubica este archivo
BASE_DIR = Path(__file__).resolve().parent

#ruta completa de la base de datos
DATABASE_PATH = BASE_DIR / "perfumes.db"

def conectar():
    conexion = sqlite3.connect(DATABASE_PATH)
    conexion.row_factory = sqlite3.Row

    return conexion

def crear_tabla():
    conexion = conectar()

    try:
        conexion.execute(
            '''
            CREATE TABLE IF NOT EXISTS perfumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                marca TEXT NOT NULL,
                nombre TEXT NOT NULL,
                concentracion INTEGER NOT NULL,
                tamano_ml INTEGER NOT NULL,
                fragrantica_url TEXT
            )
            '''
        )

        conexion.commit()

    finally:
        conexion.close()


def agregar_perfume(
    marca: str,
    nombre: str,
    concentracion: str,
    tamano_ml: int,
    fragrantica_url: str | None,
):
    """
    Guarda un nuevo perfume en la base de datos.
    """

    conexion = conectar()

    try:
        consulta = """
            INSERT INTO perfumes (
                marca,
                nombre,
                concentracion,
                tamano_ml,
                fragrantica_url
            )
            VALUES (?, ?, ?, ?, ?)
        """

        valores = (
            marca,
            nombre,
            concentracion,
            tamano_ml,
            fragrantica_url,
        )

        conexion.execute(consulta, valores)
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
                fragrantica_url
            FROM perfumes
            ORDER BY id DESC
            """
        )

        filas = cursor.fetchall()

        return [dict(fila) for fila in filas]

    finally:
        conexion.close()