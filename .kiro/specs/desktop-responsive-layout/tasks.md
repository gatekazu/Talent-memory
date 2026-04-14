# Tasks: Desktop Responsive Layout

## Task List

- [x] 1. Corregir padding vertical de `#screen-game` en desktop
  - [x] 1.1 Reemplazar `padding: clamp(3rem, 5vw, 4rem) clamp(1rem, 3vw, 2rem) clamp(1rem, 2vw, 1.5rem)` por `padding: clamp(1rem, 4vh, 3.5rem) clamp(1rem, 3vw, 2rem) clamp(0.75rem, 2vh, 2rem)` en el bloque `@media (min-width: 1024px)` de `#screen-game`
  - [x] 1.2 Agregar regla `@media (min-width: 1024px) and (max-height: 699px)` para `#screen-game` con padding reducido: `padding: clamp(0.5rem, 2vh, 1rem) clamp(1rem, 2vw, 1.5rem) clamp(0.5rem, 1.5vh, 0.75rem)`
  - [x] 1.3 Verificar que `height: 100dvh` y `overflow: hidden` están presentes en el bloque desktop de `#screen-game`

- [x] 2. Agregar restricción de altura al ancho del tablero en desktop
  - [x] 2.1 Reemplazar la regla `width: min(520px, calc(100vw - clamp(120px, 12vw, 160px) - 6rem))` en `@media (min-width: 1024px)` de `#board` por la fórmula con tres restricciones: `width: min(520px, calc(100vw - clamp(120px, 12vw, 160px) - clamp(2rem, 6vw, 4rem)), calc((100vh - clamp(3rem, 8vh, 6rem)) * 0.75))`
  - [x] 2.2 Verificar que el tablero no desborda en viewport 1024×600px (boardWidth ≤ 432px)
  - [x] 2.3 Verificar que el tablero no desborda en viewport 1280×700px (boardWidth ≤ 493px)
  - [x] 2.4 Verificar que en viewport 1920×1080px el tablero sigue siendo 520px (sin cambio)

- [x] 3. Compactar `#stats-panel` en desktop con viewports bajos
  - [x] 3.1 Actualizar `gap` de `#stats-panel` en `@media (min-width: 1024px)` a `clamp(0.4rem, 1.5vh, 1.25rem)`
  - [x] 3.2 Actualizar `padding` de `#stats-panel` en `@media (min-width: 1024px)` a `clamp(0.5rem, 1.5vh, 1rem) clamp(0.75rem, 1.5vw, 1.25rem)`
  - [x] 3.3 Agregar regla `@media (min-width: 1024px) and (max-height: 699px)` para `#stats-panel` con `gap: clamp(0.25rem, 1vh, 0.5rem)` y `padding: clamp(0.35rem, 1vh, 0.6rem) clamp(0.5rem, 1vw, 0.75rem)`

- [x] 4. Validar preservación del layout mobile
  - [x] 4.1 Confirmar que ninguna regla nueva usa `@media (max-width: ...)` ni afecta viewports < 1024px
  - [x] 4.2 Probar en viewport 375×667px (iPhone SE) que el layout mobile no cambió
  - [x] 4.3 Probar en viewport 768×1024px (tablet) que el layout mobile no cambió

- [x] 5. Validar preservación de estética y animaciones
  - [x] 5.1 Confirmar que los efectos neón (`box-shadow`, `text-shadow`) siguen presentes en todos los viewports desktop
  - [x] 5.2 Confirmar que la animación flip de cartas funciona correctamente en viewport 1024×600px
  - [x] 5.3 Confirmar que `.game-border` y `.game-bg` siguen visibles en viewports desktop pequeños
