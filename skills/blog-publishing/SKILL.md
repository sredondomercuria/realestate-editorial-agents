---
name: blog-publishing
description: Publicar el editorial aprobado en un blog WordPress vía REST API, subiendo la imagen destacada y creando el post con SEO. Usar al final del ciclo, cuando el texto y la imagen están listos.
---

# Publicación en el blog (WordPress)

## Objetivo
Publicar el editorial en el blog con su imagen destacada, metadatos SEO y estado
correcto (borrador o publicado).

## Cuándo usar
- Al final del ciclo, después de `image-generation`.

## Entradas
- Editorial aprobado (`title`, `body_markdown`, `slug`, `seo_description`, `tags`).
- Imagen hero (ruta + `alt_text`).
- Credenciales WordPress (`WORDPRESS_URL`, `WORDPRESS_USER`,
  `WORDPRESS_APP_PASSWORD`) y `WORDPRESS_STATUS`.

## Procedimiento
1. Convertí `body_markdown` a HTML.
2. Subí la imagen a la biblioteca de medios (`/wp-json/wp/v2/media`) y fijá su
   `alt_text`; guardá el `media_id` como imagen destacada.
3. Creá el post (`/wp-json/wp/v2/posts`) con título, contenido, `excerpt`
   (= SEO description), `slug`, `featured_media` y estado.
4. Devolvé `id` y `link` del post.

## Seguridad / mejores prácticas
- **Autenticación**: Application Password (no la contraseña real del usuario).
- **DRY_RUN**: si está activo, NO publiques; devolvé la previsualización.
- **Estado por defecto**: `draft` para revisión humana antes de salir en vivo.
- Nunca loguees credenciales.

## Salida
`{ status, id, link }` o, en `DRY_RUN`, una previsualización.

## Errores comunes
- 401: revisá usuario/app-password y que la REST API esté habilitada.
- 403: el usuario no tiene permisos para crear posts o subir medios.
