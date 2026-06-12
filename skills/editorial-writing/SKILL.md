---
name: editorial-writing
description: Redactar un editorial profesional de Real Estate en español a partir de noticias curadas y verificadas, con tesis clara, datos atribuidos y estructura lista para blog. Usar después del fact-check para producir o reescribir el texto.
---

# Redacción editorial profesional

## Objetivo
Escribir UN editorial cohesivo (no una lista de noticias) con autoridad,
precisión y estándar periodístico.

## Cuándo usar
- Después de `fact-check`.
- Cuando `critical-review` devuelve cambios (reescritura).

## Entradas
- Temas seleccionados (con ángulo y `key_points`).
- Veredictos del fact-check.
- (Opcional) notas de revisión del editor crítico.

## Procedimiento
1. Definí una **tesis** que hile los temas del día.
2. Redactá en Markdown:
   - Titular potente y honesto (sin clickbait).
   - Bajada (`dek`) de 1-2 frases.
   - Subtítulos `##` y párrafos legibles.
   - Sección final **Fuentes** con las URLs.
3. Reglas de datos:
   - Usá sólo datos `verified`.
   - Los `uncertain` se mencionan con cautela o se omiten.
   - **Nunca** uses datos `refuted`.
   - Atribuí cada cifra a su fuente.
4. Completá metadatos: `slug`, `tags`, `seo_description`, `sources`, y un
   `image_brief` (concepto visual de la imagen que acompaña la nota).
5. Si hay notas de revisión, **corregí cada punto** señalado.

## Salida
`{ title, slug, dek, body_markdown, tags, seo_description, sources, image_brief }`.

## Criterios de calidad
- ✅ 700-1100 palabras, tono profesional, español neutro rioplatense.
- ✅ Cada afirmación fuerte tiene fuente.
- ✅ Equilibrio y contexto; sin promesas de inversión ni consejo financiero.
- ❌ Sin relleno, sin adjetivos vacíos, sin datos sin respaldo.
