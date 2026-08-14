# Esteloteca

Esteloteca es una aplicación web desarrollada con **Python y FastAPI** para gestionar colecciones de perfumes.

Nació como un proyecto personal para poner en práctica los conocimientos adquiridos durante mi formación como **Desarrollador Python Full Stack** y continúa evolucionando de forma incremental hacia una plataforma multiusuario con colecciones públicas y privadas, catálogo compartido, recomendaciones e integración de inteligencia artificial.

> Esteloteca se encuentra en desarrollo activo. La versión actual implementa una base funcional y una arquitectura preparada para continuar ampliando el proyecto.

---

## Estado del proyecto

**Versión estable actual:** `v0.3.0`

**Estado:** desarrollo activo

**Demo pública:**
https://esteloteca-production.up.railway.app

La versión `v0.3.0` representa un hito importante en la arquitectura del proyecto, incorporando SQLAlchemy, Alembic y soporte para PostgreSQL.

---

## Funcionalidades actuales

Actualmente Esteloteca permite:

- Registrar perfumes.
- Editar y eliminar perfumes.
- Consultar el detalle individual de cada perfume.
- Buscar perfumes por marca o nombre.
- Registrar marca, nombre, concentración y tamaño.
- Cargar, reemplazar y eliminar imágenes.
- Agregar opcionalmente un enlace a Fragrantica.
- Validar formularios antes de guardar información.
- Mostrar notificaciones después de altas, ediciones y eliminaciones.
- Mostrar páginas personalizadas para errores HTTP.
- Adaptarse a PC, tablet y dispositivos móviles.
- Instalarse como PWA básica en dispositivos compatibles.

---

## Tecnologías utilizadas

### Backend

- Python
- FastAPI
- Uvicorn
- SQLAlchemy ORM
- Alembic
- Psycopg 3
- python-multipart

### Bases de datos

- PostgreSQL
- SQLite

### Frontend

- HTML5
- CSS3
- JavaScript
- Jinja2

### PWA

- Web App Manifest
- Service Worker
- Cache Storage

### Infraestructura y herramientas

- Git
- GitHub
- Railway
- HTTPS

---

## Arquitectura

La aplicación utiliza FastAPI como backend, Jinja2 para el renderizado de las vistas y SQLAlchemy como capa de persistencia.

```text
Navegador
    ↓
FastAPI
    ↓
Jinja2
    ↓
SQLAlchemy ORM
    ↓
PostgreSQL / SQLite
```

**Alembic** se utiliza para versionar y aplicar los cambios del esquema de base de datos.

SQLite permanece disponible para desarrollo local, mientras que PostgreSQL forma parte de la arquitectura preparada para los entornos desplegados.

---

## Ejecución local

Clonar el repositorio:

```bash
git clone <URL_DEL_REPOSITORIO>
cd coleccion-perfumes
```

Crear y activar un entorno virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

Aplicar las migraciones:

```bash
alembic upgrade head
```

Iniciar el servidor:

```bash
uvicorn main:app --reload
```

La aplicación estará disponible en:

```text
http://127.0.0.1:8000
```

Si no existe una variable `DATABASE_URL`, Esteloteca utiliza SQLite como base de datos local.

---

## Roadmap

Esteloteca todavía se encuentra lejos de su alcance final. Entre los principales objetivos previstos se encuentran:

- Sistema multiusuario con registro, autenticación y autorización.
- Colecciones personales públicas y privadas.
- Perfiles de usuario.
- Catálogo global de perfumes compartido entre usuarios.
- Prevención de perfumes duplicados.
- Favoritos, valoraciones y preferencias personales.
- Información olfativa enriquecida.
- Integración con servicios externos.
- Recomendaciones personalizadas según preferencias y contexto.
- Integración de inteligencia artificial como asistencia para identificación, enriquecimiento y recomendaciones.
- Tests automatizados, mejoras de seguridad y mayor robustez de producción.
- Evolución futura hacia una API y posibles aplicaciones móviles.

El objetivo es alcanzar progresivamente una primera versión web completa y estable sin perder la mantenibilidad de la arquitectura.

---

## Versionado

Esteloteca utiliza versionado semántico:

```text
MAJOR.MINOR.PATCH
```

Por ejemplo:

```text
v0.3.0
v0.3.1
v0.4.0
v1.0.0
```

Las versiones en desarrollo utilizan el sufijo `-dev`.

Los principales hitos del proyecto se documentan mediante:

- [`CHANGELOG.md`](CHANGELOG.md)
- Tags de Git
- GitHub Releases

---

## Sobre el proyecto

Esteloteca forma parte de mi portfolio y de mi proceso de formación como desarrollador.

El objetivo no es únicamente incorporar funcionalidades, sino utilizar el proyecto para aplicar progresivamente conceptos de desarrollo de software como:

- Arquitectura y separación de responsabilidades.
- Persistencia y modelado de datos.
- Migraciones de base de datos.
- Control de versiones.
- Entornos de desarrollo y producción.
- Despliegue.
- Refactorización.
- Testing.
- Seguridad.
- Mantenimiento y evolución incremental.