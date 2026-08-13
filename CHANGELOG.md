# Changelog

Todos los cambios importantes realizados en Esteloteca se documentarán en este archivo.

---

## [Unreleased] - v0.3.0-dev

### Añadido

- Rama `develop` para el desarrollo de la nueva versión.
- Entorno Staging separado de Production.
- SQLAlchemy como ORM.
- Archivo `models.py`.
- Archivo `database_orm.py`.
- Modelo ORM `Perfume`.
- Conexión de SQLAlchemy con la base de datos SQLite existente.

### Cambiado
- El buscador de perfumes ahora utiliza SQLAlchemy.
- Las principales operaciones de lectura fueron migradas desde `sqlite3` al ORM.
- Limpieza de código innecesario en `main.py`.
- El listado principal de perfumes ahora utiliza SQLAlchemy.
- La consulta de detalle por ID ahora utiliza SQLAlchemy.
- Se inició la migración progresiva desde `sqlite3` hacia SQLAlchemy.

### En desarrollo

- Migración completa del CRUD a SQLAlchemy.
- Migración futura de SQLite a PostgreSQL.
- Sistema multiusuario.
- Autenticación y autorización.
- Colecciones públicas y privadas.
- Catálogo global de perfumes.
- Integraciones de IA.
- Sistema de recomendaciones.

---

## [0.2.0] - Demo

### Añadido

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