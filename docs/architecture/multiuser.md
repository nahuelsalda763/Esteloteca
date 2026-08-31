# Arquitectura multiusuario de Esteloteca

**Versión de diseño:** `v0.4.0-dev`  
**Parte III — Etapa 01**

Este documento define la arquitectura objetivo para transformar Esteloteca desde una colección individual hacia una aplicación multiusuario.

La implementación será incremental para preservar el funcionamiento actual de la aplicación y los datos existentes.

---

## Objetivos

La arquitectura multiusuario debe permitir:

- Registrar usuarios.
- Autenticar usuarios de forma segura.
- Mantener sesiones.
- Separar los datos de cada usuario.
- Impedir modificaciones sobre colecciones ajenas.
- Crear colecciones públicas y privadas.
- Permitir perfiles públicos.
- Preparar la aplicación para un catálogo global de perfumes.
- Mantener compatibilidad con la evolución futura hacia una API y aplicaciones móviles.

---

## Entidades principales

La arquitectura objetivo estará compuesta por cuatro conceptos principales:

```text
Usuario
   ↓
Colección
   ↓
Entrada de colección
   ↓
Perfume global
```

La separación completa se realizará de forma progresiva.

---

## Usuario

La entidad `User` representará una cuenta registrada en Esteloteca.

Campos previstos:

```text
id
username
email
password_hash
is_active
created_at
```

### Reglas principales

- `id` será la clave primaria.
- `username` será único.
- `email` será único.
- Las contraseñas nunca se almacenarán en texto plano.
- La base de datos almacenará únicamente el hash de la contraseña.
- Un usuario podrá ser propietario de una o más colecciones.
- Las operaciones de escritura requerirán un usuario autenticado.

---

## Colección

La entidad `Collection` representará una colección perteneciente a un usuario.

Campos previstos:

```text
id
owner_id
name
description
is_public
created_at
updated_at
```

Relación:

```text
User 1 ────── N Collection
```

Un usuario podrá tener varias colecciones.

Inicialmente podremos trabajar con una colección principal por usuario, pero la arquitectura no quedará limitada a una única colección.

### Visibilidad

Una colección podrá ser:

```text
privada
o
pública
```

Una colección privada solo podrá ser consultada por su propietario.

Una colección pública podrá ser visualizada por otros usuarios, pero únicamente su propietario podrá modificarla.

---

## Perfume durante la transición multiusuario

Actualmente la tabla `perfumes` representa directamente los perfumes cargados en la colección.

Durante la primera fase multiusuario mantendremos esta estructura para evitar una migración demasiado grande.

La relación temporal será:

```text
User
  ↓
Collection
  ↓
Perfume actual
```

Cada perfume existente pasará progresivamente a pertenecer a una colección.

Esto permitirá implementar primero:

- usuarios;
- autenticación;
- sesiones;
- propiedad;
- autorización;
- privacidad;

sin modificar al mismo tiempo toda la arquitectura del catálogo.

---

## Catálogo global futuro

En una etapa posterior se separará el perfume como entidad global de la información específica de cada colección.

La arquitectura objetivo será:

```text
User
  ↓
Collection
  ↓
CollectionItem
  ↓
Perfume
```

### Perfume

Contendrá información compartida:

```text
marca
nombre
concentración
familia olfativa
notas
acordes
año de lanzamiento
información general
```

### CollectionItem

Representará la relación entre un perfume y una colección.

Podrá contener información personal como:

```text
tamaño
cantidad
favorito
valoración
comentario personal
información de compra
```

De esta forma, distintos usuarios podrán tener el mismo perfume sin duplicar toda su información global.

---

## Relaciones objetivo

```text
User
 │
 │ 1:N
 ▼
Collection
 │
 │ 1:N
 ▼
CollectionItem
 │
 │ N:1
 ▼
Perfume
```

Esto permitirá que:

- un usuario tenga varias colecciones;
- una colección tenga muchos perfumes;
- un mismo perfume pueda formar parte de muchas colecciones;
- la información general del perfume se almacene una sola vez.

---

## Autenticación

Esteloteca utilizará autenticación basada en sesión para la aplicación web.

Después de iniciar sesión se almacenará únicamente el identificador necesario para reconocer al usuario.

Conceptualmente:

```text
Login correcto
     ↓
Sesión
     ↓
user_id
     ↓
Usuario autenticado
```

No se almacenarán contraseñas ni información sensible dentro de la sesión.

La clave utilizada para firmar las sesiones deberá obtenerse mediante una variable de entorno y nunca almacenarse directamente en el repositorio.

---

## Contraseñas

Las contraseñas se almacenarán únicamente mediante hashes seguros.

El flujo será:

```text
Contraseña ingresada
        ↓
Hash seguro
        ↓
password_hash
        ↓
Base de datos
```

Para iniciar sesión:

```text
Contraseña ingresada
        ↓
Verificación contra el hash
        ↓
Correcta / Incorrecta
```

La contraseña original nunca podrá recuperarse desde la base de datos.

---

## Autorización

Autenticación y autorización se tratarán como conceptos distintos.

```text
Autenticación
¿Quién es el usuario?

Autorización
¿Puede realizar esta acción?
```

No será suficiente con que un usuario conozca el ID de un perfume o una colección.

Toda operación privada deberá comprobar en el servidor que el recurso pertenece al usuario autenticado.

Ejemplo:

```text
Usuario autenticado
        ↓
Colección solicitada
        ↓
¿owner_id == user.id?
       / \
     sí   no
     ↓     ↓
 permitir rechazar
```

---

## Migración de los perfumes existentes

Los perfumes actuales no se eliminarán durante la incorporación del sistema multiusuario.

La migración de propiedad se realizará de forma controlada.

La estrategia prevista será:

```text
1. Crear usuarios y colecciones.
2. Incorporar temporalmente la relación con la colección.
3. Asociar los perfumes existentes a una colección válida.
4. Verificar que ningún perfume quede sin propietario.
5. Hacer obligatoria la relación.
```

Esto evita introducir restricciones obligatorias antes de haber migrado correctamente los datos existentes.

---

## Seguridad prevista

La arquitectura deberá incorporar progresivamente:

- Hash seguro de contraseñas.
- Cookies de sesión seguras.
- Protección de rutas privadas.
- Verificación de propiedad de recursos.
- Protección CSRF en formularios.
- Validación de entradas.
- Gestión segura de secretos mediante variables de entorno.
- Prevención de acceso a recursos de otros usuarios.
- Manejo apropiado de errores de autenticación y autorización.

Estas medidas se implementarán de forma incremental durante las siguientes etapas.

---

## Orden de implementación

La Parte III seguirá aproximadamente este orden:

```text
Etapa 01 — Diseño de arquitectura multiusuario
Etapa 02 — Modelo User
Etapa 03 — Registro de usuarios
Etapa 04 — Hash seguro de contraseñas
Etapa 05 — Login, logout y sesiones
Etapa 06 — Protección de rutas
Etapa 07 — Propiedad de colecciones
Etapa 08 — Autorización
Etapa 09 — Perfil de usuario
Etapa 10 — Colecciones públicas y privadas
Etapa 11 - Vista pública de colección y bienvenida
Etapa 12 - Catálogo global de perfumes
Etapa 13 - Separación definitiva entre Perfume y CollectionItem
```

Durante la Etapa 12, CatalogPerfume representa temporalmente la identidad global compartida mientras Perfume continúa representando una entrada concreta dentro de una colección. La etapa 13 realizara la separación definitiva hacia CollectionItem + Perfume global, una vez validado el catalogo y perservados los datos existentes.


---

## Principio de desarrollo

La transición multiusuario se realizará de forma incremental.

Cada migración deberá:

1. preservar los datos existentes;
2. poder verificarse antes de continuar;
3. mantener sincronizados los modelos ORM y Alembic;
4. probarse primero en `staging`;
5. evitar cambios directos sobre `production`.

La prioridad será mantener una arquitectura comprensible y extensible sin introducir complejidad innecesaria antes de que sea requerida.