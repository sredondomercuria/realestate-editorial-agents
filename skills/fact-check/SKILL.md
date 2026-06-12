---
name: fact-check
description: Verificar datos, cifras y afirmaciones de noticias de Real Estate contra fuentes independientes antes de redactar. Usar después de la curaduría y antes de escribir, o cada vez que haya que confirmar un dato numérico o una afirmación.
---

# Verificación de datos (fact-check)

## Objetivo
Confirmar o refutar cada dato clave con fuentes independientes, para que el
editorial sólo use información sólida.

## Cuándo usar
- Después de `news-research`, antes de `editorial-writing`.
- Ante cualquier cifra o afirmación que vaya a publicarse.

## Entradas
- Lista de temas seleccionados con sus `key_points`.
- `min_sources_per_claim` (por defecto 2).

## Procedimiento
1. Por cada afirmación/dato, **buscá evidencia independiente** con la herramienta
   web. Necesitás al menos `min_sources_per_claim` fuentes confiables que
   coincidan.
2. Asigná un estado:
   - `verified`: confirmada por fuentes independientes confiables.
   - `uncertain`: respaldo insuficiente o fuentes que discrepan.
   - `refuted`: la evidencia la contradice.
3. Guardá `evidence` (qué encontraste) y `sources` (URLs reales).
4. Emití una `recommendation` global:
   - `proceed`: la mayoría verificada, nada central refutado.
   - `revise`: hay `uncertain` que obligan a matizar.
   - `drop`: alguna afirmación central está `refuted`.

## Salida
`{ verdicts: [...], recommendation, summary }`.

## Criterios de calidad
- ✅ Mentalidad escéptica: el riesgo #1 son cifras infladas o inventadas.
- ✅ Fuentes independientes entre sí (no la misma agencia replicada).
- ✅ URLs reales en cada veredicto.
- ❌ No marques `verified` por intuición: exigí evidencia.

## Antipatrones
- Aceptar una cifra porque "suena razonable".
- Contar como dos fuentes a dos medios que citan la misma nota original.
