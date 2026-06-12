# 05 · Publicación: blog (WordPress) y redes (upload-post)

El nodo `publisher` distribuye el editorial. Respeta `DRY_RUN`: si está activo,
arma todo pero **no publica** (devuelve una previsualización).

## Imágenes

Claude no genera imágenes. El flujo es:

1. El ilustrador usa Claude para escribir un **prompt visual** + `alt_text`.
2. `integrations/images.py` renderiza con el proveedor configurado (`IMAGE_PROVIDER`):
   - `gemini` (por defecto) → **Nano Banana** (`IMAGE_MODEL`): `gemini-3-pro-image`
     (Pro), `gemini-3.1-flash-image` (NB2, 4K) o `gemini-2.5-flash-image`. Requiere
     `GEMINI_API_KEY` con crédito en AI Studio.
   - `vertex` → **Vertex AI** en tu proyecto GCP. **Factura por GCP**, no por el
     prepago de AI Studio (útil si éste se queda sin crédito). Modelos: Imagen
     (`imagen-4.0-generate-001`, `us-central1`) o `gemini-2.5-flash-image` (`global`).
     En Cloud Run usa la service account (sin key); local usa
     `gcloud auth application-default login`.
   - `openai` → `gpt-image-1` (requiere `OPENAI_API_KEY`).
   - `none` → no genera; sólo guarda el prompt.
3. Si `IMAGE_HOST=cloudinary`, la imagen se sube a un CDN (`integrations/image_host.py`)
   para obtener una URL pública (`CLOUDINARY_URL`).

Para cambiar de proveedor (Stability, Replicate, Vertex, GCS...) editá esos módulos.

## Blog: WordPress REST API

**Credenciales** (te las pasa el dueño del blog):

| Variable | Cómo obtenerla |
|----------|----------------|
| `WORDPRESS_URL` | URL del sitio (ej. `https://tu-blog.com`) |
| `WORDPRESS_USER` | usuario con permiso de publicación |
| `WORDPRESS_APP_PASSWORD` | WordPress → Usuarios → Perfil → **Contraseñas de aplicación** |
| `WORDPRESS_STATUS` | `draft` (recomendado) / `publish` / `pending` |

> Usá **Application Password**, no la contraseña real. La REST API debe estar
> habilitada (lo está por defecto en WordPress moderno).

**Qué hace el cliente** (`integrations/wordpress.py`):
1. Convierte el editorial de Markdown a HTML.
2. Sube la imagen a la biblioteca (`/wp-json/wp/v2/media`) y fija su `alt_text`.
3. Crea el post (`/wp-json/wp/v2/posts`) con título, contenido, `excerpt` (SEO),
   `slug`, imagen destacada y estado.

## Redes: upload-post.com

upload-post reenvía el mismo contenido a varias redes (Instagram, LinkedIn,
Facebook, X, Threads, TikTok, etc.).

| Variable | Detalle |
|----------|---------|
| `UPLOADPOST_API_KEY` | Panel de upload-post → API |
| `UPLOADPOST_USER` | tu usuario/perfil en upload-post |
| `SOCIAL_PLATFORMS` | lista separada por comas |

**Autenticación**: header `Authorization: Apikey <KEY>`.

**Qué hace** (`integrations/upload_post.py` + `agents/social_adapter.py`):
1. El adaptador genera **una variante por plataforma** (tono y límites propios).
2. El publicador hace **una llamada por plataforma** (`/api/upload_photos`) con la
   imagen + el texto de esa red. Sin imagen, usa `/api/upload_text`.
3. Recolecta el resultado por red; si una falla, sigue con las demás.

> Los nombres de campos de upload-post pueden cambiar; verificá
> https://docs.upload-post.com/ y ajustá el cliente (está hecho para eso).

## Flujo de publicación

```
draft + images + social ──► publisher
   │                          ├─ DRY_RUN=true  → previsualización, no publica
   │                          └─ DRY_RUN=false →
   │                               ├─ WordPress: media + post (featured)
   │                               └─ upload-post: 1 post por red, con imagen
   └─► publication: { blog, social[], errors[] }
```

## Probar sin publicar

```bash
make dry-run
cat output/<fecha>/state.json   # mirá 'publication' para ver qué se publicaría
```

## Siguiente
→ [06-scheduling.md](06-scheduling.md)
