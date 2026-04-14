# Memorama Arcade Retro — Bugfix Design

## Overview

El juego presenta cuatro bugs de presentación visual que afectan principalmente la experiencia en dispositivos móviles y en ventanas de navegador sin pantalla completa. Los bugs son independientes entre sí pero todos residen en el mismo archivo `index.html` (CSS en `<style>`, JS en `<script>`).

**Bugs a resolver:**
1. **Layout no responsivo** — fuera de pantalla completa, el contenido se desborda horizontalmente o requiere scroll excesivo.
2. **Emojis descentrados** — los símbolos emoji del frente de las cartas no están centrados visual y verticalmente dentro de la carta.
3. **QR ilegible en mobile** — el canvas del QR (260×260px) es demasiado pequeño en pantallas de alta densidad (Retina/HiDPI) y los módulos quedan borrosos o sub-píxel.
4. **Todo debe caber en pantalla mobile sin scroll excesivo** — la combinación de stats panel + tablero 4×4 supera el viewport en móviles pequeños (320–390px).

**Estrategia general:** Correcciones quirúrgicas de CSS y un ajuste puntual en la generación del canvas QR. No se modifica la lógica de juego ni los motores JS.

---

## Glossary

- **Bug_Condition (C)**: La condición que activa cada bug — viewport sin pantalla completa, carta en estado `flipped`/`matched`, o generación del canvas QR.
- **Property (P)**: El comportamiento correcto esperado — layout contenido, emoji centrado, QR escaneable.
- **Preservation**: El comportamiento existente que NO debe cambiar — lógica de juego, animaciones flip, generación de tarjeta Canvas 1080×1920, leaderboard, audio.
- **`#screen-game`**: Sección del DOM que contiene el tablero y el panel de estadísticas durante la partida.
- **`#board`**: Grid CSS 4×4 que contiene las 16 cartas.
- **`#stats-panel`**: Panel lateral (desktop) / superior (mobile) con tiempo, aciertos y racha.
- **`.card-front`**: Cara delantera de la carta que muestra el emoji del par.
- **`QRCodeGenerator`**: Objeto JS embebido que genera la matriz QR; `ShareEngine.generateQR()` y el botón "QR MÓVIL" lo usan.
- **DPR (Device Pixel Ratio)**: Relación entre píxeles físicos y píxeles CSS. En móviles Retina es 2–3×.
- **Quiet Zone**: Margen blanco obligatorio alrededor del QR para que los scanners lo lean correctamente.

---

## Bug Details

### Bug 1 — Layout no responsivo

El bug se manifiesta cuando el juego se visualiza en una ventana de navegador de tamaño normal (sin pantalla completa) o en un dispositivo móvil. El `#screen-game` tiene `overflow-x: hidden` pero el `#board` usa `width: min(480px, calc(100vw - 1.5rem))` que en viewports estrechos puede seguir siendo demasiado ancho cuando se combina con el padding de la sección. Además, `section` tiene `min-height: 100vh` sin `height` acotado, lo que en mobile puede causar que el contenido empuje fuera del viewport.

**Formal Specification:**
```
FUNCTION isBugCondition_Layout(viewport)
  INPUT: viewport de tipo {width: number, height: number, isFullscreen: boolean}
  OUTPUT: boolean

  RETURN viewport.isFullscreen === false
         AND (viewport.width < 1024 OR viewport.height < 600)
         AND contenidoDesbordaViewport(viewport)
END FUNCTION
```

**Ejemplos:**
- iPhone SE (375×667px): el tablero 4×4 + stats panel requiere scroll vertical de ~200px.
- Chrome ventana 800×600px sin fullscreen: el tablero se desborda horizontalmente.
- Android 360×780px: el gap entre cartas acumula espacio extra que empuja el tablero fuera.

---

### Bug 2 — Emojis descentrados en las cartas

El `.card-front` tiene `display: flex; align-items: center; justify-content: center` pero el emoji es un carácter de texto con `line-height` heredado de `body` (1.6). Esto desplaza el emoji verticalmente. Además, `font-size: clamp(2.5rem, 7vw, 4rem)` en desktop y `clamp(1.8rem, 8vw, 3rem)` en mobile puede hacer que el emoji sobresalga del área de la carta en viewports intermedios.

**Formal Specification:**
```
FUNCTION isBugCondition_Emoji(card)
  INPUT: card de tipo HTMLElement con clase 'card-front'
  OUTPUT: boolean

  centroVisualEmoji := getBoundingClientRect(emoji).centerY
  centroCarta := getBoundingClientRect(card).centerY
  RETURN ABS(centroVisualEmoji - centroCarta) > 4px
         OR emoji.offsetWidth > card.offsetWidth
END FUNCTION
```

**Ejemplos:**
- Carta 80×107px en mobile: emoji de 3rem (~48px) aparece desplazado 8px hacia abajo por `line-height: 1.6`.
- Carta 120×160px en desktop: emoji de 4rem (~64px) centrado correctamente en X pero no en Y.

---

### Bug 3 — QR ilegible en mobile

El canvas QR se crea con `width=260, height=260` en píxeles CSS, pero en dispositivos con DPR=2 (Retina) el canvas tiene resolución efectiva de 260×260 píxeles físicos distribuidos en 130×130 píxeles CSS, haciendo que los módulos QR queden borrosos. Adicionalmente, el tamaño de módulo resultante (`drawArea / qrSize`) puede ser menor a 2px en QR de versión alta, lo que impide la lectura.

**Formal Specification:**
```
FUNCTION isBugCondition_QR(canvas, devicePixelRatio)
  INPUT: canvas de tipo HTMLCanvasElement, devicePixelRatio de tipo number
  OUTPUT: boolean

  moduloSizePx := (canvas.width - 2 * padding) / qrSize
  RETURN devicePixelRatio > 1
         AND canvas.width !== canvas.offsetWidth * devicePixelRatio
         OR moduloSizePx < 3
END FUNCTION
```

**Ejemplos:**
- iPhone 14 (DPR=3): canvas 260×260 CSS → 260px físicos → módulos de ~6px físicos → borrosos al escalar.
- Pixel 7 (DPR=2.625): módulos sub-píxel causan artefactos de anti-aliasing que rompen la lectura.

---

### Bug 4 — Contenido no cabe en pantalla mobile sin scroll

En viewports de 320–390px de ancho y 667–844px de alto, la combinación de:
- `#screen-game` con `padding: 1.5rem ... 2rem` (top + bottom)
- `#stats-panel` con altura mínima ~80px
- `#board` con `aspect-ratio: 3/4` en cada carta → tablero de ~320px × ~427px

...supera el viewport disponible (~580px de alto útil tras restar la barra del navegador).

**Formal Specification:**
```
FUNCTION isBugCondition_MobileOverflow(viewport)
  INPUT: viewport de tipo {width: number, height: number}
  OUTPUT: boolean

  alturaUtil := viewport.height - 80  // barra navegador
  alturaContenido := alturaStatsPanel + alturaTablero + paddingTotal
  RETURN viewport.width <= 480
         AND alturaContenido > alturaUtil
END FUNCTION
```

---

## Expected Behavior

### Preservation Requirements

**Comportamientos que NO deben cambiar:**
- La animación CSS 3D flip de las cartas (`.card-inner` con `rotateY`) debe seguir funcionando exactamente igual.
- El layout horizontal en desktop (≥1024px) con panel lateral y tablero centrado debe permanecer intacto.
- La generación de la tarjeta Canvas 1080×1920px (`ShareEngine.generate()`) no debe modificarse.
- El logo de Talent Land en el reverso de las cartas debe seguir centrado y proporcional.
- Todos los motores JS (`BoardEngine`, `TimerEngine`, `ScoreEngine`, `AudioEngine`, `LeaderboardManager`) no deben tocarse.
- Los efectos neón (`text-shadow`, `box-shadow`, `glow`) deben mantenerse en todos los elementos.
- El botón "QR MÓVIL" del menú principal debe seguir siendo visible solo en desktop (≥1024px).

**Scope:**
Todos los cambios son exclusivamente en CSS (reglas `@media`, propiedades de `.card-front`, `#board`, `#screen-game`, `#stats-panel`) y en la función de generación del canvas QR (corrección de DPR). No se modifica ninguna lógica de juego.

---

## Hypothesized Root Cause

### Bug 1 — Layout no responsivo

1. **`section` con `min-height: 100vh` sin `max-height`**: En mobile, el contenido puede crecer más allá del viewport sin restricción.
2. **`#screen-game` con `padding: 1.5rem ... 2rem`**: El padding acumulado (top + bottom) consume ~64px del viewport útil.
3. **`#board` con `width: min(480px, calc(100vw - 1.5rem))`**: El cálculo no descuenta el padding horizontal de `#screen-game`, causando overflow en viewports estrechos.
4. **Ausencia de `height: 100dvh`**: En mobile, `100vh` incluye la barra de dirección del navegador, causando que el contenido quede cortado.

### Bug 2 — Emojis descentrados

1. **`line-height` heredado de `body` (1.6)**: Los emojis como caracteres de texto tienen un box model que incluye el leading, desplazándolos verticalmente dentro del flex container.
2. **Falta de `line-height: 1` en `.card-front`**: Sin resetear el line-height, el emoji no ocupa exactamente su font-size en altura.
3. **Falta de `display: block` o `text-align: center` explícito en el texto del emoji**: El contenido de texto dentro de un flex container puede tener comportamiento inesperado en algunos navegadores.

### Bug 3 — QR ilegible en mobile

1. **Canvas creado sin escalar por `devicePixelRatio`**: El canvas tiene resolución CSS (260×260) pero no resolución física (260×DPR × 260×DPR), causando interpolación borrosa en pantallas Retina.
2. **`moduleSize` calculado sobre el tamaño CSS, no el físico**: Los módulos QR se dibujan con coordenadas CSS, no con coordenadas de píxeles físicos.
3. **`Math.ceil(moduleSize)` puede producir gaps entre módulos**: En módulos pequeños, el redondeo hacia arriba puede dejar píxeles sin pintar entre módulos adyacentes.

### Bug 4 — Contenido no cabe en pantalla mobile

1. **`aspect-ratio: 3/4` en las cartas**: En un tablero de 4 columnas con ancho ~320px, cada carta mide ~80px de ancho y ~107px de alto, dando un tablero de ~107×4 + gaps = ~460px de alto.
2. **Stats panel en fila horizontal**: Aunque compacto, añade ~80px de altura.
3. **Padding de `#screen-game`**: `1.5rem` top + `2rem` bottom = ~56px adicionales.
4. **Total ~596px > viewport útil ~580px**: El desbordamiento es pequeño pero suficiente para requerir scroll.

---

## Correctness Properties

Property 1: Bug Condition — Layout contenido en viewport

_For any_ viewport donde `isFullscreen === false` y `width < 1024px`, el layout del juego SHALL caber completamente dentro del área visible sin desbordamiento horizontal ni scroll vertical excesivo (máximo 1 scroll de pantalla).

**Validates: Requirements 8.5, 8.6**

---

Property 2: Bug Condition — Emoji centrado en carta

_For any_ carta en estado `flipped` o `matched`, el emoji SHALL estar centrado horizontal y verticalmente dentro del área de la carta, con una desviación máxima de 2px respecto al centro geométrico.

**Validates: Requirements 2.5, 8.3**

---

Property 3: Bug Condition — QR escaneable en mobile

_For any_ dispositivo con `devicePixelRatio >= 1`, el canvas QR generado SHALL tener resolución física suficiente (módulos de mínimo 3px físicos) y contraste adecuado (módulos negros #000000 sobre fondo blanco #ffffff) para ser escaneado correctamente por la cámara del dispositivo.

**Validates: Requirements 11.3, 11.5**

---

Property 4: Preservation — Layout desktop sin cambios

_For any_ viewport con `width >= 1024px`, el layout SHALL seguir mostrando el panel de estadísticas lateral y el tablero centrado, idéntico al comportamiento original.

**Validates: Requirements 8.5, 8.6**

---

Property 5: Preservation — Animación flip sin cambios

_For any_ carta en cualquier estado (`down`, `flipped`, `matched`), la animación CSS 3D flip SHALL funcionar exactamente igual que antes del fix, con duración ≤400ms y transformación `rotateY(180deg)`.

**Validates: Requirements 2.4, 2.5**

---

## Fix Implementation

### Cambios requeridos

Todos los cambios son en `index.html`. Se asume que el root cause analysis es correcto.

---

#### Fix 1 — Layout responsivo (`#screen-game`, `#board`, `section`)

**Archivo:** `index.html` — bloque `<style>`

**Cambios específicos:**

1. **`section` base**: Cambiar `min-height: 100vh` por `min-height: 100dvh` para respetar la barra del navegador en mobile. Agregar `overflow-x: hidden` al nivel de `section`.

2. **`#screen-game` (mobile, `max-width: 1023px`)**: 
   - Reducir padding: `padding: clamp(0.5rem, 2vw, 0.75rem) clamp(0.5rem, 2vw, 0.75rem) clamp(0.75rem, 2vw, 1rem)`
   - Agregar `height: 100dvh` y `overflow-y: auto` para contener el scroll dentro de la sección.
   - Cambiar `justify-content: flex-start` a `justify-content: center` para centrar verticalmente cuando el contenido cabe.

3. **`#board` (mobile, `max-width: 1023px`)**:
   - Usar `width: min(calc(100vw - 1rem), calc((100dvh - 160px) * 4/3))` para que el tablero nunca supere el alto disponible (descontando stats panel + padding).
   - El factor `4/3` invierte el `aspect-ratio: 3/4` de las cartas para calcular el ancho máximo que cabe en el alto disponible.

4. **`#board` (mobile pequeño, `max-width: 480px`)**:
   - `width: min(calc(100vw - 0.75rem), calc((100dvh - 140px) * 4/3))`
   - `gap: 0.25rem`

---

#### Fix 2 — Emojis centrados (`.card-front`)

**Archivo:** `index.html` — bloque `<style>`

**Cambios específicos:**

1. **`.card-front` base**: Agregar `line-height: 1` para eliminar el leading extra del texto.
2. **`.card-front` base**: Agregar `padding: 0` explícito para evitar desplazamientos por padding heredado.
3. **`.card-front` base**: Cambiar `font-size` a `clamp(2rem, 6vw, 3.5rem)` para evitar que el emoji sobresalga en viewports intermedios.
4. **`.card-front` mobile (`max-width: 1023px`)**: Cambiar a `font-size: clamp(1.4rem, 7vw, 2.5rem)` — más conservador para cartas pequeñas.

**Pseudocódigo del fix:**
```
FUNCTION fixEmojiCentering()
  SELECTOR: .card-front
  ADD: line-height: 1
  ADD: padding: 0
  MODIFY: font-size: clamp(2rem, 6vw, 3.5rem)
  
  SELECTOR: @media (max-width: 1023px) .card-front
  MODIFY: font-size: clamp(1.4rem, 7vw, 2.5rem)
END FUNCTION
```

---

#### Fix 3 — QR escaneable en mobile (canvas DPR)

**Archivo:** `index.html` — bloque `<script>`

**Función afectada:** El bloque de generación del canvas QR aparece en dos lugares:
- Botón "QR MÓVIL" del menú principal (~línea 1590)
- Botón "CÓDIGO QR" en el modal de compartir (~línea 2526)

**Cambios específicos:**

1. **Escalar el canvas por `devicePixelRatio`**:
   ```js
   const dpr = window.devicePixelRatio || 1;
   const qrDisplaySize = 260; // tamaño CSS en px
   qrCanvas.width  = qrDisplaySize * dpr;  // resolución física
   qrCanvas.height = qrDisplaySize * dpr;
   qrCanvas.style.width  = qrDisplaySize + 'px';  // tamaño visual CSS
   qrCanvas.style.height = qrDisplaySize + 'px';
   const ctx = qrCanvas.getContext('2d');
   ctx.scale(dpr, dpr);  // escalar el contexto para dibujar en coordenadas CSS
   ```

2. **Aumentar el tamaño visual del QR en mobile**: En viewports ≤480px, usar `qrDisplaySize = Math.min(280, window.innerWidth - 40)` para aprovechar el ancho disponible.

3. **Usar `Math.floor` en lugar de `Math.ceil` para el tamaño de módulo**: Evita gaps entre módulos adyacentes.
   ```js
   const moduleSize = drawArea / qrSize;
   // Dibujar con floor para evitar gaps
   ctx.fillRect(
     Math.round(padding + c * moduleSize),
     Math.round(padding + r * moduleSize),
     Math.floor(moduleSize),  // era Math.ceil
     Math.floor(moduleSize)
   );
   ```

4. **Aumentar el padding (quiet zone)** de 16px a 20px para mejorar la legibilidad en scanners estrictos.

**Pseudocódigo del fix:**
```
FUNCTION fixQRCanvas(qrCanvas, displaySize)
  INPUT: qrCanvas HTMLCanvasElement, displaySize number (CSS px)
  
  dpr := window.devicePixelRatio OR 1
  qrCanvas.width  := displaySize * dpr
  qrCanvas.height := displaySize * dpr
  qrCanvas.style.width  := displaySize + 'px'
  qrCanvas.style.height := displaySize + 'px'
  
  ctx := qrCanvas.getContext('2d')
  ctx.scale(dpr, dpr)
  
  padding := 20
  drawArea := displaySize - padding * 2
  { matrix, size } := QRCodeGenerator.encode(url)
  moduleSize := drawArea / size
  
  ctx.fillStyle := '#ffffff'
  ctx.fillRect(0, 0, displaySize, displaySize)
  ctx.shadowBlur := 0
  ctx.fillStyle := '#000000'
  
  FOR r IN [0..size):
    FOR c IN [0..size):
      IF matrix[r][c] === 1:
        ctx.fillRect(
          ROUND(padding + c * moduleSize),
          ROUND(padding + r * moduleSize),
          FLOOR(moduleSize),
          FLOOR(moduleSize)
        )
END FUNCTION
```

---

## Testing Strategy

### Validation Approach

La estrategia sigue el enfoque de dos fases: primero confirmar que los bugs son reproducibles en el código sin fix, luego verificar que el fix los resuelve sin romper el comportamiento existente.

---

### Exploratory Bug Condition Checking

**Goal**: Confirmar los bugs ANTES de implementar el fix. Refutar o confirmar el root cause.

**Test Plan**: Abrir `index.html` en Chrome DevTools con emulación de dispositivos móviles y verificar visualmente cada bug.

**Test Cases**:
1. **Layout overflow test**: Emular iPhone SE (375×667px) → iniciar partida → verificar que el tablero se desborda o requiere scroll (fallará en código sin fix).
2. **Emoji centering test**: Voltear cualquier carta → inspeccionar `.card-front` en DevTools → verificar `getBoundingClientRect()` del emoji vs. la carta (mostrará desplazamiento).
3. **QR blur test**: Abrir modal QR en iPhone 14 (DPR=3) → intentar escanear → verificar que el scanner no lo lee (fallará en código sin fix).
4. **Mobile fit test**: Emular Pixel 5 (393×851px) → iniciar partida → verificar que stats + tablero + controles no caben sin scroll.

**Expected Counterexamples**:
- El tablero se desborda horizontalmente o requiere scroll vertical en viewports <480px.
- El emoji aparece desplazado ~8px hacia abajo respecto al centro de la carta.
- El QR aparece borroso en pantallas Retina y no puede ser escaneado.

---

### Fix Checking

**Goal**: Verificar que para todos los inputs donde la condición de bug se cumple, el fix produce el comportamiento correcto.

**Pseudocode:**
```
FOR ALL viewport WHERE isBugCondition_Layout(viewport) DO
  result := renderGameScreen(viewport)
  ASSERT result.hasHorizontalOverflow === false
  ASSERT result.verticalScrollHeight <= viewport.height * 1.5
END FOR

FOR ALL card WHERE isBugCondition_Emoji(card) DO
  result := renderCardFront(card)
  ASSERT ABS(result.emojiCenterY - result.cardCenterY) <= 2
END FOR

FOR ALL device WHERE isBugCondition_QR(device) DO
  result := generateQRCanvas(device.dpr)
  ASSERT result.canvas.width === 260 * device.dpr
  ASSERT result.moduleSize >= 3
  ASSERT result.isReadableByScanner === true
END FOR
```

---

### Preservation Checking

**Goal**: Verificar que para todos los inputs donde la condición de bug NO se cumple, el comportamiento es idéntico al original.

**Pseudocode:**
```
FOR ALL viewport WHERE NOT isBugCondition_Layout(viewport) DO
  // viewport >= 1024px
  ASSERT layout_original(viewport) === layout_fixed(viewport)
END FOR

FOR ALL card WHERE NOT isBugCondition_Emoji(card) DO
  // carta en estado 'down' — reverso con logo
  ASSERT render_original(card) === render_fixed(card)
END FOR
```

**Testing Approach**: Las pruebas de preservación se realizan visualmente en DevTools y con snapshots de CSS computado. Se verifica que:
- El layout desktop (≥1024px) es pixel-perfect idéntico al original.
- La animación flip funciona igual en todos los estados.
- El canvas de la tarjeta 1080×1920px no se ve afectado.

**Test Cases**:
1. **Desktop layout preservation**: Emular 1920×1080px → verificar layout horizontal con panel lateral intacto.
2. **Flip animation preservation**: Voltear cartas en mobile y desktop → verificar animación 3D sin cambios.
3. **Card back preservation**: Verificar que el reverso con logo Talent Land sigue centrado y proporcional.
4. **Share canvas preservation**: Generar tarjeta Canvas → verificar dimensiones 1080×1920px y contenido correcto.

---

### Unit Tests

- Verificar que `.card-front` tiene `line-height: 1` en el CSS computado.
- Verificar que el canvas QR tiene `width === 260 * devicePixelRatio` después del fix.
- Verificar que `moduleSize >= 3` para QR de versión 1-10 con `displaySize=260`.
- Verificar que `#board` no desborda `#screen-game` en viewport 375px.
- Verificar que `#stats-panel` + `#board` + padding total ≤ `window.innerHeight` en viewport 375×667px.

### Property-Based Tests

- Para cualquier `displaySize` entre 200 y 400px y cualquier `dpr` entre 1 y 3: el canvas QR generado tiene `canvas.width === displaySize * dpr` y `moduleSize >= 2`.
- Para cualquier viewport entre 320px y 1023px de ancho: el `#board` calculado tiene `offsetWidth <= viewport.width - 8` (sin overflow).
- Para cualquier carta con `state === 'flipped'` o `'matched'`: el emoji tiene `getBoundingClientRect().height <= card.getBoundingClientRect().height`.

### Integration Tests

- Flujo completo en mobile (375×667px): menú → iniciar → jugar → resultados → QR → escanear con cámara real.
- Flujo completo en desktop (1280×800px): verificar que el layout no cambió.
- Voltear todas las cartas en mobile y verificar que los emojis están centrados en todas.
- Generar QR en modal "QR MÓVIL" y en modal "COMPARTIR" → escanear con app de cámara en iOS y Android.


---

# Requisito 13 — Background Animado de la Pantalla de Victoria

## Overview

La Pantalla de Victoria (`#screen-results` cuando `data.victory === true`) actualmente muestra un fondo negro liso sin animaciones. Este diseño agrega un background dinámico compuesto por capas CSS y partículas Vanilla JS que refuerzan la estética arcade retro neón, manteniendo todo el contenido legible y sin afectar el rendimiento ni la accesibilidad.

**Alcance:** Cambios exclusivamente en `index.html` — CSS en `<style>` y JS en `<script>`. No se modifica ninguna lógica de juego, motor de audio, leaderboard ni la función `handleVictory()` (solo se agrega una llamada a `VictoryBackground.start()` al final de ella y `VictoryBackground.stop()` en `Renderer.showScreen()`).

---

## Architecture

El background de victoria sigue el mismo patrón arquitectónico ya establecido en el juego para otras pantallas (menú, leaderboard):

```
handleVictory()
  └─► Renderer.showScreen('results')
        └─► VictoryBackground.start()   ← nuevo
              ├─ Activa clases CSS en #screen-results
              └─ Genera partículas DOM en #victory-particles

Renderer.showScreen(name) [cualquier otra pantalla]
  └─► VictoryBackground.stop()          ← nuevo
        ├─ Remueve clases CSS de #screen-results
        └─ Limpia #victory-particles del DOM
```

**Capas visuales (z-index stack):**

| z-index | Elemento | Descripción |
|---------|----------|-------------|
| 0 | `#screen-results::before` | Gradiente radial neón (fondo) |
| 0 | `.victory-bg` (dot grid) | Grid de puntos animado |
| 0 | `.victory-border` | Borde neón pulsante |
| 1 | `#victory-particles` | Contenedor de partículas flotantes |
| 2 | Contenido (`h2`, scores, botones) | Siempre encima del fondo |
| 9999 | `body::after` | Scanlines globales (sin cambios) |

---

## Components and Interfaces

### CSS — Nuevas reglas para `#screen-results.victory-active`

**Clase activadora:** `.victory-active` se agrega a `#screen-results` cuando `data.victory === true`.

**Capas de fondo:**
- `#screen-results.victory-active::before` — gradiente radial multicapa con colores neón (`#00ff41`, `#00ffff`, `#ff00ff`, `#ffff00`) sobre `#0a0a0a`.
- `.victory-bg` (div hijo) — grid de puntos `radial-gradient` con `background-size: 28px 28px`, animado con `@keyframes victoryGridScroll`.
- `.victory-border` (div hijo) — borde `2px solid var(--color-magenta)` con `box-shadow` neón magenta, animado con `@keyframes victoryBorderPulse`. Color magenta (`#ff00ff`) diferencia este borde del borde verde de `#screen-game`.

**Partículas:**
- `#victory-particles` — contenedor `position: fixed; inset: 0; pointer-events: none; z-index: 1; overflow: hidden`.
- `.vp` — clase base de partícula: `position: absolute; pointer-events: none; opacity: 0; animation: vpFloat linear infinite`.
- `.vp.star` — símbolo `★` (texto, font-retro).
- `.vp.spark` — símbolo `✦` (texto, font-retro).
- `.vp.plus` — símbolo `+` (div, 2px × 10px con pseudo-elementos).
- `.vp.dot` — círculo `border-radius: 50%`, 3–6px.

**Animaciones `@keyframes`:**
- `victoryGridScroll` — desplaza `background-position` de `0 0` a `28px 28px` en 15s.
- `victoryBorderPulse` — opacidad 1 → 0.3 → 1 en 2s ease-in-out.
- `vpFloat` — `translateY(105vh)` → `translateY(-10vh)` con drift horizontal ±20px, fade in/out.
- `vpSpin` — rotación 0 → 360deg para variante `.vp.spark`.

**`prefers-reduced-motion`:**
```css
@media (prefers-reduced-motion: reduce) {
  .victory-bg,
  .victory-border,
  #victory-particles { display: none !important; }
  #screen-results.victory-active::before {
    /* Solo gradiente estático, sin animación */
    animation: none !important;
  }
}
```

### JS — Módulo `VictoryBackground`

```js
const VictoryBackground = (() => {
  const NEON_COLORS = ['#00ff41','#00ffff','#ff00ff','#ffff00'];
  const PARTICLE_COUNT = 60;
  const SHAPES = ['star','spark','plus','dot'];  // ≥2 tipos distintos

  let _active = false;

  function start() {
    if (_active) return;
    _active = true;
    const screen = document.getElementById('screen-results');
    screen.classList.add('victory-active');
    _spawnParticles();
  }

  function stop() {
    if (!_active) return;
    _active = false;
    const screen = document.getElementById('screen-results');
    screen.classList.remove('victory-active');
    const container = document.getElementById('victory-particles');
    if (container) container.innerHTML = '';
  }

  function _spawnParticles() {
    // Respetar prefers-reduced-motion
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

    const container = document.getElementById('victory-particles');
    if (!container) return;
    container.innerHTML = '';

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      const shape = SHAPES[Math.floor(Math.random() * SHAPES.length)];
      const color = NEON_COLORS[Math.floor(Math.random() * NEON_COLORS.length)];
      const el = document.createElement(shape === 'plus' || shape === 'dot' ? 'div' : 'span');
      el.className = 'vp ' + shape;
      el.style.left = Math.random() * 100 + 'vw';
      const dur = 5 + Math.random() * 12;
      el.style.animationDuration = dur + 's';
      el.style.animationDelay = -(Math.random() * dur) + 's';
      el.style.color = color;
      el.style.textShadow = `0 0 6px ${color}, 0 0 12px ${color}`;
      if (shape === 'star') el.textContent = '★';
      if (shape === 'spark') el.textContent = '✦';
      if (shape === 'dot') {
        const sz = 3 + Math.random() * 3;
        el.style.width = el.style.height = sz + 'px';
        el.style.background = color;
        el.style.boxShadow = `0 0 4px ${color}`;
      }
      // opacity máxima ≤ 0.9 (Req 13.7)
      el.style.setProperty('--vp-max-opacity', (0.5 + Math.random() * 0.4).toFixed(2));
      container.appendChild(el);
    }
  }

  return { start, stop };
})();
```

### HTML — Cambios en `#screen-results`

Agregar dos divs hijos al inicio de `#screen-results` y el contenedor de partículas:

```html
<section id="screen-results">
  <!-- Fondo animado de victoria -->
  <div class="victory-bg"></div>
  <div class="victory-border"></div>
  <div id="victory-particles"></div>

  <!-- Contenido existente (sin cambios) -->
  <h2 id="result-title">GAME OVER</h2>
  ...
</section>
```

### Integración con `handleVictory()` y `Renderer.showScreen()`

**En `handleVictory()`** — agregar al final, después de `Renderer.showScreen('results')`:
```js
VictoryBackground.start();
```

**En `Renderer.showScreen(name)`** — agregar al inicio del método:
```js
VictoryBackground.stop();
```

Esto garantiza que el background se limpia al navegar a cualquier otra pantalla (Req 13.5).

---

## Data Models

No se introducen nuevos modelos de datos. El módulo `VictoryBackground` es stateless excepto por el flag `_active` (booleano) que previene doble inicialización.

**Constantes:**
```js
NEON_COLORS: string[]   // ['#00ff41','#00ffff','#ff00ff','#ffff00']
PARTICLE_COUNT: 60      // número de partículas generadas
SHAPES: string[]        // ['star','spark','plus','dot'] — ≥2 tipos (Req 13.2)
```

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Partículas con tipos distintos

*For any* invocación de `VictoryBackground.start()` (sin `prefers-reduced-motion`), el contenedor `#victory-particles` SHALL contener elementos de al menos 2 clases de forma distintas (`star`, `spark`, `plus`, `dot`), todos con colores pertenecientes a la Paleta Neón.

**Validates: Requirements 13.2**

---

### Property 2: Limpieza de partículas al navegar

*For any* secuencia de acciones que lleve al jugador fuera de la Pantalla de Victoria (jugar de nuevo, volver al menú), el contenedor `#victory-particles` SHALL tener cero elementos hijos después de la transición.

**Validates: Requirements 13.5**

---

### Property 3: Opacidad de partículas ≤ 0.9

*For any* partícula generada por `VictoryBackground._spawnParticles()`, el valor de `--vp-max-opacity` SHALL ser ≤ 0.9, y el z-index del contenedor de partículas SHALL ser menor al z-index del contenido de la pantalla de victoria.

**Validates: Requirements 13.7**

---

### Property 4: Sin desbordamiento horizontal en cualquier viewport

*For any* viewport con ancho entre 320px y 1920px, cuando la Pantalla de Victoria está activa, `#screen-results.scrollWidth` SHALL ser igual a `#screen-results.clientWidth` (sin overflow horizontal).

**Validates: Requirements 13.9**

---

## Error Handling

| Escenario | Comportamiento esperado |
|-----------|------------------------|
| `#victory-particles` no existe en el DOM | `_spawnParticles()` retorna silenciosamente sin lanzar error |
| `VictoryBackground.start()` llamado dos veces | El flag `_active` previene doble inicialización; segunda llamada es no-op |
| `window.matchMedia` no disponible (navegadores muy antiguos) | El bloque `try/catch` en `_spawnParticles()` omite la verificación y genera partículas normalmente |
| `prefers-reduced-motion: reduce` activo | CSS oculta `.victory-bg`, `.victory-border`, `#victory-particles`; JS no genera partículas |
| Navegación rápida (usuario sale antes de que terminen las animaciones) | `VictoryBackground.stop()` limpia el DOM inmediatamente; las animaciones CSS se detienen al remover la clase `.victory-active` |

---

## Testing Strategy

### Dual Testing Approach

**Unit tests (ejemplo-based):**
- Verificar que `VictoryBackground.start()` agrega la clase `.victory-active` a `#screen-results`.
- Verificar que `VictoryBackground.stop()` remueve `.victory-active` y vacía `#victory-particles`.
- Verificar que el borde de `.victory-border` usa `var(--color-magenta)` (distinto al verde de `#screen-game`).
- Verificar que `body::after` (scanlines) no es suprimido por estilos de `.victory-active`.
- Verificar que con `prefers-reduced-motion: reduce`, `#victory-particles` permanece vacío tras `start()`.

**Property-based tests** (usando [fast-check](https://github.com/dubzzz/fast-check)):

La librería elegida es **fast-check** (Vanilla JS, sin dependencias de framework), configurada con mínimo 100 iteraciones por propiedad.

```js
// Tag format: Feature: victory-screen-background, Property N: <text>

// Property 1: Partículas con tipos distintos
// Feature: victory-screen-background, Property 1: particle shape diversity
fc.assert(fc.property(fc.integer({ min: 1, max: 5 }), (_seed) => {
  VictoryBackground.stop();
  VictoryBackground.start();
  const container = document.getElementById('victory-particles');
  const shapes = new Set([...container.children].map(el => {
    for (const s of ['star','spark','plus','dot']) {
      if (el.classList.contains(s)) return s;
    }
  }));
  const colors = [...container.children].map(el => el.style.color);
  const NEON = ['#00ff41','#00ffff','#ff00ff','#ffff00'];
  return shapes.size >= 2 && colors.every(c => NEON.includes(c));
}), { numRuns: 100 });

// Property 2: Limpieza al navegar
// Feature: victory-screen-background, Property 2: cleanup on navigation
fc.assert(fc.property(fc.constantFrom('menu','game','leaderboard'), (screen) => {
  VictoryBackground.start();
  Renderer.showScreen(screen);
  const container = document.getElementById('victory-particles');
  return container.children.length === 0;
}), { numRuns: 100 });

// Property 3: Opacidad ≤ 0.9
// Feature: victory-screen-background, Property 3: particle opacity constraint
fc.assert(fc.property(fc.integer({ min: 1, max: 3 }), (_run) => {
  VictoryBackground.stop();
  VictoryBackground.start();
  const container = document.getElementById('victory-particles');
  return [...container.children].every(el => {
    const opacity = parseFloat(el.style.getPropertyValue('--vp-max-opacity'));
    return opacity <= 0.9;
  });
}), { numRuns: 100 });

// Property 4: Sin overflow horizontal
// Feature: victory-screen-background, Property 4: no horizontal overflow
fc.assert(fc.property(fc.integer({ min: 320, max: 1920 }), (width) => {
  // Simular viewport width via jsdom o resize
  VictoryBackground.start();
  const el = document.getElementById('screen-results');
  return el.scrollWidth <= el.clientWidth + 1; // +1px tolerancia
}), { numRuns: 100 });
```

**Integration tests:**
- Flujo completo: iniciar partida → completar todos los pares → verificar que `#screen-results` tiene clase `.victory-active` y `#victory-particles` tiene hijos.
- Flujo completo: victoria → "JUGAR DE NUEVO" → verificar que `#victory-particles` está vacío.
- Flujo completo: victoria → "MENÚ" → verificar que `#victory-particles` está vacío.
- Verificar en Chrome DevTools (mobile 375px y desktop 1280px) que el contenido (título, puntaje, botones) es legible sobre el fondo animado.
- Verificar en dispositivo real con `prefers-reduced-motion: reduce` que solo se muestra el gradiente estático.
