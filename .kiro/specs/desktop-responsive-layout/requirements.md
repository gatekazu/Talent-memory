# Documento de Requisitos: Desktop Responsive Layout

## Introducción

Esta feature corrige el layout responsivo del juego Memorama Arcade Retro para que funcione correctamente en ventanas de escritorio pequeñas (sin pantalla completa). Actualmente en mobile se ve bien, pero en desktop con ventanas más pequeñas (ej. 800×600, 1024×600, 1280×700) el tablero se desborda o las cartas quedan cortadas. Todos los cambios son exclusivamente CSS en `index.html`.

---

## Requisitos

### Requisito 1: Tablero siempre visible en desktop sin scroll

**User Story:** Como jugador en desktop, quiero que el tablero 4×4 y el panel de estadísticas siempre quepan en el viewport visible sin necesidad de hacer scroll, para poder jugar en cualquier tamaño de ventana.

#### Criterios de Aceptación

1. WHEN el juego está en pantalla de juego (`#screen-game`) en cualquier viewport con `width >= 1024px` y `height >= 400px`, THE tablero (`#board`) y el panel de estadísticas (`#stats-panel`) SHALL ser completamente visibles dentro del área del viewport sin scroll vertical ni horizontal.

2. THE `#screen-game` SHALL tener `height: 100dvh` y `overflow: hidden` en viewports `>= 1024px` de ancho, para contener todo el contenido sin desbordamiento.

3. WHEN el viewport desktop tiene `height < 700px`, THE padding vertical de `#screen-game` SHALL reducirse automáticamente usando `clamp()` para maximizar el espacio disponible para el tablero.

---

### Requisito 2: Escalado proporcional del tablero por altura disponible

**User Story:** Como jugador en desktop, quiero que el tablero escale proporcionalmente al espacio disponible en pantalla, para que las cartas nunca queden cortadas por los bordes del viewport.

#### Criterios de Aceptación

1. THE ancho de `#board` en desktop SHALL calcularse como el mínimo de tres restricciones: el máximo absoluto (520px), el ancho disponible descontando el panel lateral y los paddings, y el alto disponible multiplicado por `0.75` (inversa del aspect-ratio 3/4 de las cartas).

2. THE fórmula CSS SHALL ser:
   ```css
   width: min(
     520px,
     calc(100vw - clamp(120px, 12vw, 160px) - clamp(2rem, 6vw, 4rem)),
     calc((100vh - clamp(3rem, 8vh, 6rem)) * 0.75)
   );
   ```

3. FOR any viewport with `width >= 1024px` and `height >= 400px`, THE `#board.offsetHeight` SHALL be less than or equal to `window.innerHeight` minus the total vertical padding of `#screen-game`.

4. THE aspect-ratio `3/4` de las cartas SHALL mantenerse intacto — no se modifica la propiedad `aspect-ratio` de `.card`.

---

### Requisito 3: Preservación del layout desktop en pantallas grandes

**User Story:** Como jugador en desktop con pantalla grande (≥ 1440px de ancho o ≥ 900px de alto), quiero que el layout no cambie respecto al comportamiento actual, para que la experiencia visual no se vea afectada.

#### Criterios de Aceptación

1. FOR any viewport with `width >= 1440px` AND `height >= 900px`, THE `#board` SHALL have `width = 520px` — idéntico al comportamiento original.

2. THE layout horizontal (panel lateral izquierdo + tablero centrado) SHALL mantenerse intacto para todos los viewports `>= 1024px` de ancho.

3. THE `#stats-panel` SHALL mantener su posición lateral con `width: clamp(120px, 12vw, 160px)` en todos los viewports desktop.

---

### Requisito 4: Preservación del layout mobile sin cambios

**User Story:** Como jugador en mobile, quiero que el layout mobile existente no se vea afectado por los cambios de desktop, para que la experiencia en móvil siga funcionando correctamente.

#### Criterios de Aceptación

1. FOR any viewport with `width < 1024px`, THE layout SHALL be identical to the current behavior — ninguna regla CSS nueva SHALL aplicar a viewports mobile.

2. THE `#stats-panel` en mobile SHALL seguir mostrándose en fila horizontal encima del tablero, con `flex-direction: row` y `max-width: 480px`.

3. THE `#board` en mobile SHALL seguir usando las reglas existentes: `width: min(calc(100vw - 1rem), calc((100dvh - 160px) * 4/3))`.

---

### Requisito 5: Panel de estadísticas adaptativo en desktop

**User Story:** Como jugador en desktop con ventana pequeña, quiero que el panel de estadísticas se compacte verticalmente para no consumir espacio innecesario, para que el tablero tenga más espacio disponible.

#### Criterios de Aceptación

1. THE `gap` interno de `#stats-panel` en desktop SHALL usar `clamp(0.4rem, 1.5vh, 1.25rem)` para reducirse automáticamente en viewports bajos.

2. WHEN el viewport desktop tiene `height < 700px`, THE `gap` de `#stats-panel` SHALL reducirse a `clamp(0.25rem, 1vh, 0.5rem)` y el `padding` a `clamp(0.35rem, 1vh, 0.6rem)`.

3. THE contenido del panel (tiempo, aciertos, racha, botones) SHALL seguir siendo legible en todos los tamaños — `font-size` de `.stat-value` no SHALL reducirse por debajo de `0.9rem`.

---

### Requisito 6: Compatibilidad con navegadores modernos

**User Story:** Como jugador, quiero que el juego funcione correctamente en Chrome, Firefox, Edge y Safari modernos, para no tener problemas de compatibilidad.

#### Criterios de Aceptación

1. THE solución CSS SHALL usar únicamente propiedades con soporte en Chrome 79+, Firefox 75+, Safari 13.1+ y Edge 79+: `clamp()`, `min()`, `max()`, `100dvh`, `@media (max-height: ...)`.

2. WHERE `100dvh` no esté soportado, THE layout SHALL degradar graciosamente usando `100vh` como fallback — el contenido puede requerir scroll mínimo pero no se desbordará horizontalmente.

3. THE animación CSS 3D flip de las cartas (`.card-inner` con `rotateY`) SHALL funcionar exactamente igual que antes en todos los navegadores y tamaños de ventana.

---

### Requisito 7: Estética neón arcade retro preservada

**User Story:** Como jugador, quiero que los efectos visuales neón (bordes, sombras, animaciones) se mantengan intactos en todos los tamaños de ventana, para que la experiencia visual sea coherente.

#### Criterios de Aceptación

1. THE efectos `text-shadow` y `box-shadow` neón SHALL mantenerse en todos los elementos en todos los tamaños de ventana.

2. THE borde neón pulsante de `#screen-game` (`.game-border`) SHALL seguir visible y animado en todos los viewports desktop.

3. THE grid de puntos animado (`.game-bg`) SHALL seguir visible en todos los viewports desktop.

4. NO se SHALL modificar ningún `@keyframes`, `animation`, `transition` ni `transform` existente.
