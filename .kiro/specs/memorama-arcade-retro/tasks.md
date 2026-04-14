# Plan de Implementación: Bugfix Memorama Arcade Retro

## Resumen

Correcciones quirúrgicas de CSS y un ajuste puntual en la generación del canvas QR para resolver cuatro bugs de presentación visual que afectan la experiencia en dispositivos móviles y ventanas sin pantalla completa. Todos los cambios son en `index.html` (CSS en `<style>`, JS en `<script>`). No se modifica ninguna lógica de juego.

**Bugs a resolver:**
1. Layout no responsivo (CSS responsive/mobile)
2. Emojis descentrados en las cartas (CSS line-height fix)
3. QR ilegible en mobile (canvas DPR scaling)
4. Todo debe caber en pantalla mobile sin scroll excesivo

---

## Tareas

- [x] 1. Escribir prueba de condición de bug — exploración
  - **Property 1: Bug Condition** - Layout, Emoji y QR en mobile
  - **CRÍTICO**: Esta prueba DEBE FALLAR en el código sin fix — la falla confirma que los bugs existen
  - **NO intentar corregir la prueba ni el código cuando falle**
  - **NOTA**: Esta prueba codifica el comportamiento esperado — validará el fix cuando pase tras la implementación
  - **OBJETIVO**: Exponer contraejemplos que demuestren que los bugs existen
  - **Enfoque PBT acotado**: Para bugs deterministas, acotar la propiedad a los casos concretos de falla para garantizar reproducibilidad
  - Abrir `index.html` en Chrome DevTools con emulación de dispositivos móviles y verificar visualmente:
    - **Bug 1 — Layout**: Emular iPhone SE (375×667px) → iniciar partida → verificar que el tablero se desborda o requiere scroll excesivo
    - **Bug 2 — Emoji**: Voltear cualquier carta → inspeccionar `.card-front` en DevTools → verificar `getBoundingClientRect()` del emoji vs. la carta (mostrará desplazamiento ~8px)
    - **Bug 3 — QR**: Abrir modal QR en iPhone 14 (DPR=3) → intentar escanear → verificar que el scanner no lo lee
    - **Bug 4 — Mobile fit**: Emular Pixel 5 (393×851px) → iniciar partida → verificar que stats + tablero + controles no caben sin scroll
  - Contraejemplos esperados a documentar:
    - El tablero se desborda horizontalmente o requiere scroll vertical en viewports <480px
    - El emoji aparece desplazado ~8px hacia abajo respecto al centro de la carta
    - El QR aparece borroso en pantallas Retina y no puede ser escaneado
    - Stats panel + tablero + padding total > viewport.height en 375×667px
  - Ejecutar en código SIN fix — **RESULTADO ESPERADO**: Bugs visibles (confirma que existen)
  - Marcar tarea completa cuando las pruebas estén escritas, ejecutadas y los bugs documentados
  - _Requirements: 1.3, 1.4, 1.5, 1.6, 1.7_

- [x] 2. Escribir pruebas de preservación (ANTES de implementar el fix)
  - **Property 2: Preservation** - Comportamiento desktop y animaciones sin cambios
  - **IMPORTANTE**: Seguir metodología observation-first
  - Observar comportamiento en código SIN fix para inputs no afectados por los bugs:
    - Observar: layout desktop (1920×1080px) muestra panel lateral + tablero centrado correctamente
    - Observar: animación flip 3D funciona en todos los estados (`down`, `flipped`, `matched`)
    - Observar: reverso de carta muestra logo Talent Land centrado y proporcional
    - Observar: canvas tarjeta 1080×1920px genera correctamente con todos los elementos
    - Observar: QR en desktop (DPR=1) es escaneable sin problemas
  - Escribir pruebas de preservación capturando los patrones observados (desde Preservation Requirements en design.md):
    - Para cualquier viewport ≥1024px: layout horizontal con panel lateral intacto
    - Para cualquier carta en estado `down`: reverso con logo centrado y proporcional
    - Para cualquier carta en cualquier estado: animación flip ≤400ms con `rotateY(180deg)` sin cambios
    - Canvas tarjeta: dimensiones 1080×1920px y contenido correcto
  - Ejecutar pruebas en código SIN fix
  - **RESULTADO ESPERADO**: Pruebas PASAN (confirma comportamiento base a preservar)
  - Marcar tarea completa cuando las pruebas estén escritas, ejecutadas y pasando en código sin fix
  - _Requirements: 3.4, 3.5, 3.6, 3.7_

- [x] 3. Fix de los cuatro bugs en `index.html`

  - [x] 3.1 Fix 1 — Layout responsivo: corregir `section`, `#screen-game` y `#board`
    - En `section` base: cambiar `min-height: 100vh` por `min-height: 100dvh`; agregar `overflow-x: hidden`
    - En `#screen-game` (mobile `max-width: 1023px`): reducir padding a `clamp(0.5rem, 2vw, 0.75rem)`; agregar `height: 100dvh` y `overflow-y: auto`; cambiar `justify-content` a `center`
    - En `#board` (mobile `max-width: 1023px`): usar `width: min(calc(100vw - 1rem), calc((100dvh - 160px) * 4/3))` para que el tablero nunca supere el alto disponible
    - En `#board` (mobile pequeño `max-width: 480px`): `width: min(calc(100vw - 0.75rem), calc((100dvh - 140px) * 4/3))`; `gap: 0.25rem`
    - _Bug_Condition: isBugCondition_Layout(viewport) donde viewport.isFullscreen === false AND viewport.width < 1024_
    - _Expected_Behavior: layout contenido sin desbordamiento horizontal ni scroll vertical excesivo_
    - _Preservation: layout desktop ≥1024px idéntico al original_
    - _Requirements: 1.3, 1.4, 2.3, 2.4, 2.7, 3.4_

  - [x] 3.2 Fix 2 — Emojis centrados: corregir `.card-front`
    - En `.card-front` base: agregar `line-height: 1` para eliminar el leading extra del texto
    - En `.card-front` base: agregar `padding: 0` explícito
    - En `.card-front` base: cambiar `font-size` a `clamp(2rem, 6vw, 3.5rem)`
    - En `.card-front` mobile (`max-width: 1023px`): cambiar a `font-size: clamp(1.4rem, 7vw, 2.5rem)`
    - _Bug_Condition: isBugCondition_Emoji(card) donde ABS(emojiCenterY - cardCenterY) > 4px_
    - _Expected_Behavior: emoji centrado horizontal y verticalmente con desviación máxima de 2px_
    - _Preservation: carta en estado `down` con reverso logo Talent Land sin cambios_
    - _Requirements: 1.5, 2.5, 3.5_

  - [x] 3.3 Fix 3 — QR escaneable en mobile: escalar canvas por DPR
    - Localizar los dos bloques de generación del canvas QR en `index.html`:
      - Botón "QR MÓVIL" del menú principal (~línea 1590)
      - Botón "CÓDIGO QR" en el modal de compartir (~línea 2526)
    - En ambos bloques aplicar el fix DPR:
      ```js
      const dpr = window.devicePixelRatio || 1;
      const qrDisplaySize = window.innerWidth <= 480
        ? Math.min(280, window.innerWidth - 40)
        : 260;
      qrCanvas.width  = qrDisplaySize * dpr;
      qrCanvas.height = qrDisplaySize * dpr;
      qrCanvas.style.width  = qrDisplaySize + 'px';
      qrCanvas.style.height = qrDisplaySize + 'px';
      const ctx = qrCanvas.getContext('2d');
      ctx.scale(dpr, dpr);
      ```
    - Cambiar `padding` de 16px a 20px (quiet zone)
    - Cambiar `Math.ceil(moduleSize)` por `Math.floor(moduleSize)` en el `fillRect` del módulo QR
    - Usar `Math.round` para las coordenadas x/y del `fillRect`
    - _Bug_Condition: isBugCondition_QR(canvas, dpr) donde dpr > 1 AND canvas.width !== canvas.offsetWidth * dpr_
    - _Expected_Behavior: canvas.width === displaySize * dpr; moduleSize >= 3px físicos; QR escaneable_
    - _Preservation: QR en desktop DPR=1 sigue funcionando; canvas tarjeta 1080×1920px sin cambios_
    - _Requirements: 1.6, 2.6, 3.6, 3.7_

  - [x] 3.4 Verificar que la prueba de condición de bug ahora pasa
    - **Property 1: Expected Behavior** - Layout, Emoji y QR corregidos
    - **IMPORTANTE**: Re-ejecutar las MISMAS pruebas de la tarea 1 — NO escribir nuevas pruebas
    - Las pruebas de la tarea 1 codifican el comportamiento esperado
    - Cuando estas pruebas pasen, confirman que el comportamiento esperado se cumple
    - Re-ejecutar en Chrome DevTools con emulación mobile:
      - iPhone SE (375×667px): tablero cabe sin scroll excesivo ✓
      - Carta volteada: emoji centrado con desviación ≤2px ✓
      - iPhone 14 (DPR=3): QR escaneable con cámara ✓
      - Pixel 5 (393×851px): stats + tablero + controles caben en pantalla ✓
    - **RESULTADO ESPERADO**: Pruebas PASAN (confirma que los bugs están resueltos)
    - _Requirements: 2.3, 2.4, 2.5, 2.6, 2.7_

  - [x] 3.5 Verificar que las pruebas de preservación siguen pasando
    - **Property 2: Preservation** - Comportamiento desktop y animaciones sin regresiones
    - **IMPORTANTE**: Re-ejecutar las MISMAS pruebas de la tarea 2 — NO escribir nuevas pruebas
    - Re-ejecutar en Chrome DevTools con viewport desktop:
      - 1920×1080px: layout horizontal con panel lateral intacto ✓
      - Animación flip 3D en todos los estados sin cambios ✓
      - Reverso de carta con logo Talent Land centrado ✓
      - Canvas tarjeta 1080×1920px generado correctamente ✓
    - **RESULTADO ESPERADO**: Pruebas PASAN (confirma que no hay regresiones)

- [x] 4. Checkpoint — Verificar que todas las pruebas pasan
  - Asegurarse de que todas las pruebas pasan. Consultar al usuario si surgen dudas.
  - Verificación final en múltiples viewports:
    - Mobile pequeño: 320×568px (iPhone SE 1st gen)
    - Mobile estándar: 375×667px (iPhone SE 3rd gen)
    - Mobile grande: 393×851px (Pixel 5)
    - Tablet: 768×1024px (iPad)
    - Desktop: 1280×800px, 1920×1080px
  - Confirmar que el archivo `index.html` funciona al abrirse directamente en Chrome, Firefox y Edge
  - Confirmar que el QR es escaneable en iOS y Android con la cámara nativa

---

# Plan de Implementación: Background Animado de la Pantalla de Victoria (Requisito 13)

## Resumen

Implementar el background dinámico de la Pantalla de Victoria en `index.html`: capas CSS animadas (gradiente radial neón, grid de puntos, borde magenta pulsante, scanlines), partículas Vanilla JS (`VictoryBackground` module), y la integración con `handleVictory()` y `Renderer.showScreen()`. Sin modificar lógica de juego, motores JS ni tareas previas.

---

## Tareas

- [x] 5. Agregar estructura HTML en `#screen-results`
  - Insertar al inicio de `<section id="screen-results">` los tres divs de fondo:
    ```html
    <div class="victory-bg"></div>
    <div class="victory-border"></div>
    <div id="victory-particles"></div>
    ```
  - Verificar que el contenido existente (`h2`, scores, botones, créditos) queda después de estos divs
  - _Requirements: 13.1, 13.3_

- [x] 6. Agregar estilos CSS para el background de victoria
  - [x] 6.1 Estilos base de `.victory-active` y capas de fondo
    - Agregar regla `#screen-results.victory-active::before` con gradiente radial multicapa neón (`#00ff41`, `#00ffff`, `#ff00ff`, `#ffff00`) sobre `#0a0a0a`
    - Agregar regla `.victory-bg`: `position: absolute; inset: 0; background-image: radial-gradient(circle, rgba(0,255,65,0.12) 1px, transparent 1px); background-size: 28px 28px; pointer-events: none; z-index: 0; animation: victoryGridScroll 15s linear infinite`
    - Agregar regla `.victory-border`: `position: absolute; inset: 8px; border: 2px solid var(--color-magenta); box-shadow: var(--glow-magenta), inset var(--glow-magenta); pointer-events: none; z-index: 0; animation: victoryBorderPulse 2s ease-in-out infinite`
    - Agregar `@keyframes victoryGridScroll`: `0% { background-position: 0 0; } 100% { background-position: 28px 28px; }`
    - Agregar `@keyframes victoryBorderPulse`: `0%, 100% { opacity: 1; } 50% { opacity: 0.3; }`
    - _Requirements: 13.1, 13.3, 13.4_

  - [x] 6.2 Estilos de partículas y animaciones de movimiento
    - Agregar regla `#victory-particles`: `position: fixed; inset: 0; pointer-events: none; z-index: 1; overflow: hidden`
    - Agregar regla `.vp`: `position: absolute; pointer-events: none; opacity: 0; animation: vpFloat linear infinite; font-family: var(--font-retro)`
    - Agregar regla `.vp.plus`: `width: 2px; height: 10px; border-radius: 1px` con pseudo-elementos `::before` para la barra horizontal
    - Agregar regla `.vp.dot`: `border-radius: 50%`
    - Agregar `@keyframes vpFloat`: `0% { transform: translateY(105vh) translateX(0); opacity: 0; } 8% { opacity: var(--vp-max-opacity, 0.8); } 92% { opacity: calc(var(--vp-max-opacity, 0.8) * 0.5); } 100% { transform: translateY(-10vh) translateX(20px); opacity: 0; }`
    - Agregar `@keyframes vpSpin`: `0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); }`
    - Asegurar z-index del contenido: `#screen-results.victory-active > *:not(.victory-bg):not(.victory-border):not(#victory-particles) { position: relative; z-index: 2; }`
    - _Requirements: 13.2, 13.7_

  - [x] 6.3 Regla `prefers-reduced-motion` y responsive
    - Agregar bloque `@media (prefers-reduced-motion: reduce)` que oculta `.victory-bg`, `.victory-border`, `#victory-particles` con `display: none !important` y aplica `animation: none !important` al `::before` de `.victory-active`
    - Verificar que `#screen-results` mantiene `overflow-x: hidden` y `max-width: 600px` para no causar desbordamiento horizontal en ningún viewport (320px–1920px)
    - _Requirements: 13.8, 13.9_

- [x] 7. Implementar el módulo JS `VictoryBackground`
  - [x] 7.1 Crear el módulo IIFE `VictoryBackground` con `start()` y `stop()`
    - Declarar constantes: `NEON_COLORS = ['#00ff41','#00ffff','#ff00ff','#ffff00']`, `PARTICLE_COUNT = 60`, `SHAPES = ['star','spark','plus','dot']`
    - Implementar `start()`: verificar `_active`, setear `_active = true`, agregar clase `victory-active` a `#screen-results`, llamar `_spawnParticles()`
    - Implementar `stop()`: verificar `_active`, setear `_active = false`, remover clase `victory-active`, vaciar `innerHTML` de `#victory-particles`
    - Implementar `_spawnParticles()`: respetar `prefers-reduced-motion`; generar 60 partículas con forma aleatoria de `SHAPES`, color aleatorio de `NEON_COLORS`, `left` aleatorio en `vw`, duración 5–17s, delay negativo aleatorio, `--vp-max-opacity` entre 0.5 y 0.9
    - Para `.vp.star`: `textContent = '★'`; para `.vp.spark`: `textContent = '✦'`; para `.vp.dot`: asignar `width`, `height` (3–6px), `background`, `boxShadow`
    - _Requirements: 13.2, 13.5, 13.6, 13.7, 13.8_

  - [x] 7.2 Escribir property test — Property 1: diversidad de formas de partículas
    - **Property 1: Partículas con tipos distintos**
    - **Validates: Requirements 13.2**
    - Usar fast-check: `fc.assert(fc.property(fc.integer({ min: 1, max: 5 }), (_seed) => { ... shapes.size >= 2 && colors.every(c => NEON.includes(c)) }))`
    - Verificar que `#victory-particles` contiene elementos de al menos 2 clases distintas (`star`, `spark`, `plus`, `dot`) y todos con colores de la Paleta Neón

  - [x] 7.3 Escribir property test — Property 2: limpieza al navegar
    - **Property 2: Limpieza de partículas al navegar**
    - **Validates: Requirements 13.5**
    - Usar fast-check: `fc.assert(fc.property(fc.constantFrom('menu','game','leaderboard'), (screen) => { VictoryBackground.start(); Renderer.showScreen(screen); return container.children.length === 0; }))`
    - Verificar que tras `Renderer.showScreen()` el contenedor `#victory-particles` tiene cero hijos

  - [x] 7.4 Escribir property test — Property 3: opacidad de partículas ≤ 0.9
    - **Property 3: Opacidad ≤ 0.9**
    - **Validates: Requirements 13.7**
    - Usar fast-check: `fc.assert(fc.property(fc.integer({ min: 1, max: 3 }), (_run) => { ... return [...container.children].every(el => parseFloat(el.style.getPropertyValue('--vp-max-opacity')) <= 0.9); }))`
    - Verificar que `--vp-max-opacity` de cada partícula es ≤ 0.9

  - [x] 7.5 Escribir property test — Property 4: sin overflow horizontal
    - **Property 4: Sin desbordamiento horizontal en cualquier viewport**
    - **Validates: Requirements 13.9**
    - Usar fast-check: `fc.assert(fc.property(fc.integer({ min: 320, max: 1920 }), (width) => { VictoryBackground.start(); const el = document.getElementById('screen-results'); return el.scrollWidth <= el.clientWidth + 1; }))`
    - Verificar que `scrollWidth <= clientWidth + 1` para viewports entre 320px y 1920px

- [x] 8. Integrar `VictoryBackground` con el flujo del juego
  - [x] 8.1 Llamar `VictoryBackground.start()` en `handleVictory()`
    - Localizar la función `handleVictory()` en el bloque `<script>` de `index.html`
    - Agregar `VictoryBackground.start();` al final de la función, después de `Renderer.showScreen('results')`
    - _Requirements: 13.1, 13.4_

  - [x] 8.2 Llamar `VictoryBackground.stop()` en `Renderer.showScreen()`
    - Localizar el método `showScreen(name)` dentro del objeto/módulo `Renderer`
    - Agregar `VictoryBackground.stop();` al inicio del método, antes de ocultar/mostrar secciones
    - Verificar que esto garantiza limpieza al navegar a cualquier pantalla (menú, juego, leaderboard)
    - _Requirements: 13.5_

- [x] 9. Checkpoint — Verificar implementación completa del background de victoria
  - Asegurarse de que todas las pruebas pasan. Consultar al usuario si surgen dudas.
  - Verificar en Chrome DevTools:
    - Mobile (375×667px): Pantalla de Victoria muestra gradiente + grid + borde magenta + partículas sin scroll horizontal
    - Desktop (1280×800px): Pantalla de Victoria muestra todas las capas; contenido (título, puntaje, botones) legible sobre el fondo
    - Con `prefers-reduced-motion: reduce`: solo gradiente estático y borde, sin partículas ni animaciones de movimiento
    - Navegar a otra pantalla: `#victory-particles` vacío, clase `.victory-active` removida
  - Confirmar que el borde magenta de la Pantalla de Victoria es visualmente distinto al borde verde de `#screen-game`
  - Confirmar que los scanlines globales (`body::after`) siguen visibles sobre el background de victoria
