---
name: news-research
description: Buscar, filtrar y curar las noticias más relevantes y recientes de Real Estate de una región (por defecto Argentina y Latam) para alimentar un editorial. Usar al inicio del ciclo editorial o cuando se necesite un panorama de novedades del sector inmobiliario.
---

# Investigación y curaduría de noticias de Real Estate

## Objetivo
Producir una lista corta y curada de noticias accionables sobre el mercado
inmobiliario, cada una con su ángulo editorial y datos verificables.

## Cuándo usar
- Al arrancar el ciclo editorial diario.
- Cuando alguien pide "qué está pasando en el mercado inmobiliario".

## Entradas
- `region` (ej.: "Argentina y Latinoamérica").
- `fecha` actual.
- Ventana temporal (por defecto: últimos 7 días).

## Procedimiento
1. **Buscar** con la herramienta de búsqueda web. Cubrí estos subtemas: precios de
   venta y alquiler, créditos hipotecarios, desarrollos y obra nueva, inversión,
   regulación/impuestos, dólar e impacto en ladrillos, y tendencias.
2. **Filtrar**: quedate con fuentes primarias y medios reputados (diarios
   económicos, cámaras inmobiliarias, organismos oficiales, portales del sector).
   Descartá rumores sin fuente y contenido promocional.
3. **Curar**: seleccioná las N mejores (por defecto 4) priorizando impacto,
   novedad, disponibilidad de datos verificables y diversidad temática.
4. Para cada noticia elegida definí:
   - `title`, `angle` (ángulo editorial), `why_it_matters`,
   - `key_points`: 3-5 datos concretos a verificar y desarrollar,
   - `primary_source` (URL) y `related_sources`.

## Salida
Una lista de noticias seleccionadas con el formato anterior, lista para pasar a
`fact-check`.

## Criterios de calidad
- ✅ Cada noticia tiene al menos una URL real (nunca inventes fuentes).
- ✅ Diversidad: no repetir el mismo subtema.
- ✅ Los `key_points` son afirmaciones verificables, no opiniones.
- ❌ Nada de clickbait ni contenido publicitario.

## Antipatrones
- Inventar cifras o URLs.
- Seleccionar por volumen en vez de por relevancia/datos.
