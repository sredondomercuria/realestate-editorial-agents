---
name: critical-review
description: Revisión crítica y adversarial de un editorial antes de publicar: revalida los datos centrales con búsquedas independientes y controla sourcing, sesgo, claridad y riesgo legal. Usar como control de calidad final; puede devolver el texto a redacción.
---

# Revalidación crítica y control de calidad

## Objetivo
Ser la última línea de defensa antes de publicar. Revalidar los datos clave de
forma independiente y aprobar o devolver el texto con cambios accionables.

## Cuándo usar
- Después de `editorial-writing`, antes de `image-generation`/publicación.

## Entradas
- Borrador del editorial.
- Veredictos del fact-check.

## Procedimiento
1. **Revalidación independiente**: tomá las 2-3 cifras/afirmaciones más
   importantes y verificalas de nuevo con búsquedas web, sin confiar en el
   fact-check previo. Anotá la URL que respalda cada una.
2. **Evaluación por dimensiones**:
   - `factual`: datos sin respaldo, contradichos o mal atribuidos.
   - `sourcing`: ¿cada cifra tiene fuente confiable citada?
   - `clarity`: ¿la tesis se entiende?
   - `bias`: sesgo, lenguaje promocional, conclusiones no sustentadas.
   - `legal`: promesas de rendimiento, consejo financiero, difamación.
   - `style`: estándar profesional y guía de estilo.
3. Asigná `score` (0-100) y un `verdict`:
   - `needs_revision` si hay **cualquier** issue `high` o varios `medium`.
   - `approved` en caso contrario.
4. Para cada issue, incluí un `fix` concreto para el redactor.

## Salida
`{ verdict, score, issues: [{severity, type, detail, fix}], notes }`.

## Criterios de calidad
- ✅ Mirada adversarial: buscá el error, no confirmes el acierto.
- ✅ Es preferible una revisión extra a publicar con un error.
- ✅ Los `fix` son accionables (qué cambiar y cómo).

## Límite de iteraciones
Para evitar bucles infinitos, el workflow limita las reescrituras
(`MAX_REVISIONS`). Si se agotan, se publica la mejor versión disponible y se deja
constancia de los issues remanentes.
