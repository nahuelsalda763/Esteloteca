from pathlib import Path
import os

#Carpeta principal
BASE_DIR = Path(__file__).resolve().parent

RAILWAY_VOLUME_MOUNT_PATH = os.getenv(
    "RAILWAY_VOLUME_MOUNT_PATH"
)

#SI estamos en railway se usa el volumen, si estamos en local se usa la carpeta del proyecto
if RAILWAY_VOLUME_MOUNT_PATH:
    STORAGE_DIR = Path(
        RAILWAY_VOLUME_MOUNT_PATH
    )
else:
    STORAGE_DIR = BASE_DIR

#ruta de la base de datos

DATABASE_PATH =(
    STORAGE_DIR / "perfumes.db"
)

# URL de conexión a la base de datos.
# Si existe DATABASE_URL se utiliza PostgreSQL.
# Si no existe, Esteloteca continúa utilizando SQLite.

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace(
            "postgres://",
            "postgresql+psycopg://",
            1,
        )

    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace(
            "postgresql://",
            "postgresql+psycopg://",
            1,
        )

else:
    DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

#carpeta raiz para los archivos subidos
UPLOAD_ROOT =(
    STORAGE_DIR / "uploads"
)

#carpeta especifica de imagenes
UPLOAD_DIR =(
    UPLOAD_ROOT / "perfumes"
)

#Cuando sea necesario se crea carpeta

STORAGE_DIR.mkdir(
    parents = True, exist_ok = True,
)

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

SESSION_SECRET_KEY = os.getenv(
    "SESSION_SECRET_KEY"
)

SESSION_COOKIE_SECURE = (
    os.getenv(
        "SESSION_COOKIE_SECURE",
        "false",
    )
    .strip()
    .lower()
    == "true"
)

SESSION_MAX_AGE =(
    60 * 60 * 24 * 7
)