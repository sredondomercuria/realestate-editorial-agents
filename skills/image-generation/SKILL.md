---
name: image-generation
description: Crear el prompt visual profesional y el alt-text para generar una imagen editorial que acompañe el post y sus variantes en redes. Usar tras aprobar el editorial, antes de publicar.
---

# Imagen editorial que acompaña cada post

## Objetivo
Producir una imagen sobria y profesional (y su alt-text accesible) que represente
el editorial, para usar como imagen destacada del blog y en las redes.

## Cuándo usar
- Después de `critical-review` (editorial aprobado).

## Entradas
- `title`, `dek` e `image_brief` del editorial.

## Procedimiento
1. Escribí **un prompt en inglés** para el modelo de imágenes que produzca una
   foto/ilustración editorial realista. Incluí: encuadre, iluminación, paleta y
   mood. Sin texto incrustado, sin logos, sin marcas de agua.
2. Definí `negative_prompt` (texto, logos, deformaciones, baja calidad).
3. Escribí `alt_text` en español (descripción para accesibilidad) y un `caption`
   breve (epígrafe).
4. Generá la imagen con el proveedor configurado (`IMAGE_PROVIDER`). Si es `none`,
   sólo se guarda el prompt/brief para generarla luego.

## Salida
`{ prompt, negative_prompt, alt_text, caption, style }` + archivo de imagen (si se
generó).

## Criterios de calidad
- ✅ Coherente con el tema (real estate, no genérico).
- ✅ Profesional y sobria; nada de "AI slop" ni estética cliché.
- ✅ `alt_text` descriptivo y útil para lectores de pantalla.
- ❌ Nada de texto dentro de la imagen, logos ni marcas registradas.

## Nota
Anthropic no genera imágenes: esta skill usa Claude para el prompt y un proveedor
externo (gpt-image-1 u otro) para el render. El proveedor está aislado en
`src/editorial_team/integrations/images.py` y es reemplazable.
