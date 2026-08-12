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