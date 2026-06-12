---
name: social-publishing
description: Adaptar el editorial a cada red social (tono y límites) y publicarlo en todas a la vez vía upload-post, con la imagen que acompaña cada post. Usar al final del ciclo, en paralelo o después de publicar en el blog.
---

# Distribución en redes sociales (upload-post)

## Objetivo
Llevar el editorial a todas las redes configuradas, con una variante adaptada a
cada plataforma y la imagen editorial, en una sola corrida.

## Cuándo usar
- Al final del ciclo, junto con `blog-publishing`.

## Entradas
- Editorial aprobado (`title`, `dek`, `seo_description`, `tags`).
- Imagen hero (ruta).
- Credenciales upload-post (`UPLOADPOST_API_KEY`, `UPLOADPOST_USER`) y
  `SOCIAL_PLATFORMS`.

## Procedimiento
1. **Adaptar** una variante por plataforma respetando tono y límites:
   - instagram: gancho visual + 3-5 hashtags.
   - linkedin: profesional, foco en el dato y la implicancia.
   - facebook: informativo y cercano.
   - x: ≤270 caracteres, 1-2 hashtags.
   - threads: conversacional.
   - tiktok: gancho hablado para video corto.
2. **Publicar** con upload-post (`Authorization: Apikey <KEY>`):
   - `POST /api/upload_photos` con la imagen + caption (una llamada por plataforma
     para enviar el texto específico de cada una).
   - Si no hay imagen, usar `POST /api/upload_text`.
3. Recolectar el resultado por plataforma.

## Seguridad / mejores prácticas
- **DRY_RUN**: si está activo, NO publiques; devolvé las variantes para revisar.
- No exageres ni prometas rendimientos; mantené la precisión del dato.
- Manejá errores por plataforma sin frenar las demás.

## Salida
Lista de resultados por red: `{ platform, status, response|error }`.

## Nota sobre la API
Verificá los nombres de campos vigentes en https://docs.upload-post.com/ — el
cliente en `src/editorial_team/integrations/upload_post.py` está hecho para
adaptarse rápido si cambian.
