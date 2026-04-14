# Implementation Plan: mobile-share-image

## Overview

Cambios mínimos en CSS y JS para habilitar el botón "COMPARTIR" en mobile, más property-based tests con fast-check para las 4 propiedades del design.

## Tasks

- [x] 1. Remover restricción CSS de `#btn-share`
  - En `index.html`, eliminar la regla `#btn-share { display: none; }` y el bloque `@media (min-width: 1024px)` que sobreescribe ese display
  - Reemplazar por una única regla base: `#btn-share { display: inline-flex; align-items: center; justify-content: center; }`
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 2. Ajustar cálculo de `previewW` en el handler de `#btn-share`
  - En `index.html`, localizar `const previewW = 270;` dentro del handler click de `#btn-share`
  - Cambiar a `const previewW = Math.min(270, window.innerWidth - 48);`
  - _Requirements: 2.2, 5.1_

- [x] 3. Añadir tamaño mínimo táctil a botones del modal en mobile
  - En `index.html`, añadir media query `@media (max-width: 1023px)` con regla `min-height: 44px; min-width: 44px` para `.modal-buttons button` y `.modal-body button`
  - _Requirements: 5.2_

- [x] 4. Checkpoint — verificar cambios visuales
  - Confirmar que `#btn-share` es visible en el DOM sin restricción de viewport
  - Confirmar que el cálculo de `previewW` usa `Math.min`
  - Confirmar que la media query de botones táctiles está presente
  - Asegurar que no hay errores de sintaxis en el CSS/JS modificado

- [x] 5. Escribir property-based tests con fast-check
  - [x] 5.1 Property 1 — `#btn-share` visible en cualquier viewport
    - Usar `fc.integer({ min: 320, max: 1920 })` para generar anchos de viewport
    - Verificar que el computed style de `#btn-share` no sea `display: none`
    - Tag: `Feature: mobile-share-image, Property 1: btn-share visible en cualquier viewport`
    - **Validates: Requirements 1.2**

  - [x] 5.2 Property 2 — `ShareEngine.generate` produce canvas 1080×1920 para cualquier `shareData` válido
    - Usar `fc.record` con `mote` (string), `score` (nat), `rank` (integer 1–100), `hits` (nat max 8), `timeLeft` (integer 0–60)
    - Verificar `canvas.width === 1080 && canvas.height === 1920`
    - Tag: `Feature: mobile-share-image, Property 2: ShareEngine.generate produce canvas correcto`
    - **Validates: Requirements 2.1**

  - [x] 5.3 Property 3 — preview no excede el ancho del viewport
    - Usar `fc.integer({ min: 320, max: 1023 })` para generar anchos de viewport mobile
    - Verificar `Math.min(270, vw - 48) <= vw` para cada `vw`
    - Tag: `Feature: mobile-share-image, Property 3: Preview no excede viewport`
    - **Validates: Requirements 2.2, 5.1**

  - [x] 5.4 Property 4 — `#btn-share-native` vuelve a habilitarse tras `shareNative`
    - Usar `fc.boolean()` para simular éxito o `AbortError`
    - Mock de `navigator.share` según el valor booleano
    - Verificar `btn.disabled === false` y `btn.textContent === '↗ COMPARTIR'` al resolver
    - Tag: `Feature: mobile-share-image, Property 4: btn-share-native re-habilitado tras shareNative`
    - **Validates: Requirements 4.3, 4.4**

- [x] 6. Checkpoint final — Ensure all tests pass
  - Ejecutar los tests en `memorama.test.html` y confirmar que las 4 propiedades pasan con 100 iteraciones cada una
  - Asegurar que no hay regresiones en los tests existentes
  - Preguntar al usuario si hay dudas antes de cerrar.
