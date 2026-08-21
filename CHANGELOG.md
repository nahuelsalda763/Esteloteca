# Changelog

Todos los cambios importantes realizados en Esteloteca se documentarán en este archivo.

---

## [Unreleased] - v0.4.0-dev

## Añadido

- Documentacion de arquitectura para la transición de Esteloteca hacia un sistema multiusuario.
- Modelo ORM user para representar las cuentas de usuario.
- Tabla users con identificadores, credenciales almacenadas mediante hash, estado de cuenta y fecha de creación de la misma.
- Migración de ALembic para incorporar la tabla users.
- Verificación segura de contraseñas contra hashes Argon2.
- Política centralizada de validación de contraseñas.
- Inicio y cierre de sesión para usuarios registrados.
- Sesiones web mediante cookies firmadas y configuracion segura por entorno.
- Configuración local persistente de las variables de sesión mediante `.env` y plantilla `.env.example`.
- Protección de las operaciones de alta, edición y eliminación de perfumes para requerir una sesión autenticada.
- Modelo rom "collection" para representar las colecciones pertenecientes a usuarios.
- Relacion de propiedad entre usuarios y colecciones mediante "owner_id"
- Relacion entre perfumes y colecciones mediante "collection_id"
- Creación automática de una colección principal al registrar un nuevo usuario
- MIgracion de Alembic para incorporar colecciones y asociar los perfumes históricos a una colección valida
- Autorizacion por propiedad para impedir que un usuario edite o elimine perfumes pertenecientes a colecciones de otro user.
- Respuesta HTTP 403 para intentos de edicion o eliminacion no autorizados

### Cambiado

- La validación de contraseñas del registro fue centralizada en "security.py"
- El registro de usuarios ahora enlaza directamente con el inicio de sesión.
- El inicio de sesión ahora permite autenticarse tanto con nombre de usuario como con correo electrónico.
- Los nuevos perfumes pasan a asociarse automáticamente a la colección principal del usuario autenticado
- Las operaciones ORM de actualización y eliminación de perfumes verifican también el propietario autenticado-
- Las acciones editar y eliminar se muestran en el listado y en el detalle solo cuando el perfume pertenece al usuario autentificado.

### En desarrollo

- Sistema multiusuario.
- Autenticación y autorización.
- COlecciones públicas y privadas.
- Catálogo global de perfumes.
- Integraciones de IA.
- SUstema de recomendaciones.
- Formulario web para el registro de usuarios.
- Persistencia de nuevas cuentas mediante sqlalchemy ORM.
- Validaciones de user, correo, y confirmacion de contraseña durante el registro.
- Hash de contraseñas mediante pwdlib y Argon2 antes de almacenarlas.

---

## [0.3.0] - 14-08-26

### Añadido

- Rama `develop` para el desarrollo de la nueva versión.
- Entorno `staging` separado de `production`.
- SQLAlchemy como ORM.
- Archivo `models.py`.
- Archivo `database_orm.py`.
- Modelo ORM `Perfume`.
- Conexión de SQLAlchemy con la base de datos SQLite existente.
- Alembic como sistema de migraciones de base de datos.
- Migración inicial versionada del esquema de Esteloteca.
- Migración para normalizar el esquema histórico de la tabla `perfumes`.
- Psycopg 3 como driver de PostgreSQL para SQLAlchemy.
- Servicio PostgreSQL preparado en el entorno `staging`.
- Script `scripts/migrate_sqlite_to_postgres.py` para migrar datos desde SQLite a PostgreSQL preservando los IDs existentes.
- Base PostgreSQL de `staging` inicializada y versionada mediante Alembic.
- Variable `DATABASE_URL` de Esteloteca vinculada al servicio PostgreSQL de Railway.

### Cambiado

- El listado principal de perfumes ahora utiliza SQLAlchemy.
- El buscador de perfumes ahora utiliza SQLAlchemy.
- La consulta de detalle por ID ahora utiliza SQLAlchemy.
- El alta, edición y eliminación de perfumes ahora utilizan SQLAlchemy.
- El formulario de edición trabaja directamente con objetos ORM.
- Los errores ya no se muestran como respuestas JSON al usuario de la web.
- Se realizó limpieza de código innecesario en `main.py`.
- Todo el CRUD principal fue migrado desde `sqlite3` a SQLAlchemy ORM.
- SQLAlchemy pasa a ser la única capa de acceso a la base de datos.
- Alembic pasa a ser responsable de la creación y evolución del esquema de la base de datos.
- Se eliminó el uso de `Base.metadata.create_all()` durante el inicio de la aplicación.
- Se normalizaron los tipos de columnas heredados de la antigua implementación con `sqlite3`.
- El entorno `staging` de Railway ejecuta las migraciones de Alembic mediante un Pre-Deploy Command antes de iniciar Uvicorn.
- La configuración de base de datos admite `DATABASE_URL` para PostgreSQL, con SQLite como fallback local.
- La conexión SQLAlchemy queda preparada para utilizar SQLite o PostgreSQL según el entorno.
- El entorno `staging` fue migrado de SQLite a PostgreSQL.
- PostgreSQL pasa a ser la base de datos activa de Esteloteca en `staging`.
- SQLite se mantiene como fallback para el entorno local.


---

## [0.2.0] - Demo

### Añadido
- Páginas visuales para errores HTTP
- Notificaciones visuales para altas, ediciones y eliminaciones exitosas.
- Mensajes de validación dentro del formulario de edición.
- Aplicación web creada con FastAPI.
- Plantillas HTML mediante Jinja2.
- Base de datos SQLite.
- Alta de perfumes.
- Edición de perfumes.
- Eliminación de perfumes.
- Vista individual de cada perfume.
- Buscador por marca y nombre.
- Campo opcional de enlace a Fragrantica.
- Carga de imágenes de perfumes.
- Reemplazo y eliminación de imágenes.
- Diseño responsive para PC, tablet y dispositivos móviles.
- Plantilla base mediante herencia de Jinja2.
- Web App Manifest.
- Iconos de la aplicación.
- Service Worker.
- Cache Storage.
- Página de fallback sin conexión.
- Soporte PWA básico.
- Deployment inicial en Railway.
- Configuración para almacenamiento local o Railway mediante `config.py`.


### Tecnologías utilizadas

- Python
- FastAPI
- Jinja2
- SQLite
- HTML
- CSS
- JavaScript
- Git
- GitHub
- Railway
- PWA