# Design Document — mobile-share-image

## Overview

La feature habilita el botón "COMPARTIR" (`#btn-share`) en la pantalla de resultados para todos los viewports, incluyendo dispositivos móviles. Actualmente el botón está oculto en viewports < 1024px mediante una regla CSS explícita. La solución es mínima: eliminar esa restricción y ajustar el modal de compartir para que la preview del canvas se adapte al ancho disponible en mobile.

Toda la lógica de negocio (`ShareEngine`, `ModalManager`, `GameState`) ya existe y funciona correctamente en desktop. No se requieren cambios en JavaScript salvo el cálculo del ancho de la preview del canvas dentro del handler de `btn-share`.

### Decisiones de diseño

- **Cambio mínimo**: Solo se modifica CSS y el cálculo del `previewW` en el handler existente. No se refactoriza `ShareEngine` ni `ModalManager`.
- **Preview responsiva**: El ancho de la preview se calcula dinámicamente con `Math.min(270, window.innerWidth - 48)` para respetar el padding del modal en cualquier viewport.
- **Sin feature detection adicional**: La detección de Web Share API (`_canShareFiles()`) ya existe y funciona igual en mobile que en desktop.

---

## Architecture

El sistema ya tiene una arquitectura de módulos IIFE dentro de un único `index.html`. No se añaden nuevos módulos.

```
index.html
├── CSS (inline <style>)
│   └── #btn-share — CAMBIO: remover restricción display:none / @media ≥1024px
├── HTML
│   └── #screen-results > .result-buttons > #btn-share  (sin cambios)
└── JavaScript (inline <script>)
    └── handler click #btn-share
        └── previewW — CAMBIO: cálculo responsivo
            ├── ShareEngine.generate(shareData)   (sin cambios)
            ├── ShareEngine.generateQR(url, canvas) (sin cambios)
            ├── ShareEngine.downloadPNG(canvas)    (sin cambios)
            ├── ShareEngine.shareNative(canvas)    (sin cambios)
            └── ModalManager.show(config)          (sin cambios)
```

---

## Components and Interfaces

### CSS — `#btn-share`

**Antes:**
```css
#btn-share {
  display: none;
}
@media (min-width: 1024px) {
  #btn-share {
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }
}
```

**Después:**
```css
#btn-share {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
```

La regla `@media (min-width: 1024px)` se elimina por completo ya que el estado base pasa a ser visible.

### JavaScript — handler `#btn-share` (previewW)

**Antes:**
```js
const previewW = 270;
```

**Después:**
```js
const previewW = Math.min(270, window.innerWidth - 48);
```

El valor `48` corresponde al padding horizontal del modal (`2rem` = ~32px) más el borde (`2×2px`) más margen de seguridad. Esto garantiza que la preview nunca exceda el ancho del viewport.

### CSS — `.modal-box` (scroll vertical)

El modal ya tiene `max-height: 90vh` y `overflow-y: auto` definidos en el CSS existente. No se requiere cambio.

### CSS — botones táctiles en mobile

Los botones del modal heredan los estilos base de `button` que ya tienen `padding: 0.75em 1.5em`. En mobile con `font-size: clamp(0.5rem, 1.5vw, 0.75rem)` el área táctil resultante puede ser menor a 44px. Se añade una media query para garantizar el mínimo táctil:

```css
@media (max-width: 1023px) {
  .modal-buttons button,
  .modal-body button {
    min-height: 44px;
    min-width: 44px;
  }
}
```

---

## Data Models

No se introducen nuevos modelos de datos. Los datos relevantes son los mismos que usa el handler existente:

```js
// shareData — construido desde GameState en el handler de btn-share
{
  mote:     string,   // GameState.playerMote || 'JUGADOR'
  score:    number,   // GameState.score
  rank:     number,   // LeaderboardManager.getRank(GameState.score)
  hits:     number,   // ScoreEngine.getHits()
  timeLeft: number,   // TimerEngine.getTime()
}
```

---

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

Del prework se identificaron las siguientes propiedades candidatas:

- **1.2**: Para cualquier viewport width, `btn-share` debe ser visible.
- **2.1**: Para cualquier `shareData` válido, `ShareEngine.generate()` retorna un canvas 1080×1920.
- **2.2 / 5.1**: Para cualquier viewport < 1024px, el ancho de la preview ≤ ancho del viewport. (2.2 y 5.1 son idénticas — se consolidan en una sola propiedad.)
- **4.3**: Para cualquier resultado de `shareNative` (éxito o cancelación), el botón vuelve a estar habilitado.

Las propiedades 2.2 y 5.1 son redundantes; se mantiene una sola. El resto son independientes y aportan valor único.

---

### Property 1: btn-share visible en cualquier viewport

*For any* viewport width entre 320px y 1920px, el elemento `#btn-share` no debe tener `display: none` en sus estilos computados.

**Validates: Requirements 1.2**

---

### Property 2: ShareEngine.generate produce canvas correcto para cualquier shareData

*For any* objeto `shareData` con campos válidos (`mote` string no vacío, `score` número ≥ 0, `rank` número ≥ 1, `hits` número ≥ 0, `timeLeft` número entre 0 y 60), `ShareEngine.generate(shareData)` debe retornar un `HTMLCanvasElement` con `width === 1080` y `height === 1920`.

**Validates: Requirements 2.1**

---

### Property 3: Preview del canvas no excede el ancho del viewport

*For any* viewport width `vw` entre 320px y 1023px, el ancho calculado de la preview (`Math.min(270, vw - 48)`) debe ser menor o igual a `vw`.

**Validates: Requirements 2.2, 5.1**

---

### Property 4: btn-share-native vuelve a habilitarse tras shareNative

*For any* resultado de `ShareEngine.shareNative()` — ya sea resolución exitosa o rechazo con `AbortError` (cancelación del usuario) — el botón `#btn-share-native` debe terminar habilitado (`disabled === false`) con el texto `"↗ COMPARTIR"`.

**Validates: Requirements 4.3, 4.4**

---

## Error Handling

| Escenario | Comportamiento esperado |
|---|---|
| `downloadPNG` falla (browser no soporta `<a download>`) | `console.warn` + resolve silencioso. Ya implementado en `ShareEngine.downloadPNG`. |
| `shareNative` rechazado con `AbortError` (usuario cancela) | Resolve silencioso. Ya implementado en `ShareEngine.shareNative`. |
| `shareNative` rechazado con otro error | `console.warn` + resolve silencioso. Ya implementado. |
| Web Share API no disponible | Botón "↗ COMPARTIR" no se renderiza. Ya implementado via `_canShareFiles()`. |
| `ShareEngine.generate` falla (canvas API no disponible) | Error propagado al handler; el modal no se abre. No se requiere cambio. |

No se introducen nuevos caminos de error. Los existentes ya cubren los casos de mobile.

---

## Testing Strategy

### Enfoque dual

- **Unit tests (ejemplo)**: verifican comportamientos específicos y casos de borde.
- **Property-based tests**: verifican propiedades universales sobre rangos de inputs.

La librería de PBT elegida es **fast-check** (JavaScript, MIT), compatible con el entorno de test existente (`memorama.test.html`).

Cada property test debe ejecutarse con mínimo **100 iteraciones**.

Tag format: `Feature: mobile-share-image, Property {N}: {texto}`

### Tests unitarios (ejemplo)

| Test | Criterio |
|---|---|
| `btn-share` existe en el DOM | Req 1.1 |
| Modal contiene botón "⬇ DESCARGAR" tras abrir | Req 2.3 |
| Modal muestra "↗ COMPARTIR" si `navigator.canShare` retorna true | Req 2.4 |
| Modal no muestra "↗ COMPARTIR" si `navigator.canShare` retorna false | Req 2.5 |
| `downloadPNG` crea `<a>` con `download="memorama-resultado.png"` | Req 3.1 |
| `downloadPNG` llama `console.warn` si `link.click()` lanza | Req 3.2 |
| `shareNative` llama `navigator.share` con un `File` PNG | Req 4.1 |
| `btn-share-native` se deshabilita durante `shareNative` | Req 4.2 |
| `shareNative` resuelve sin throw si usuario cancela (AbortError) | Req 4.4 |

### Property-based tests

```
// Feature: mobile-share-image, Property 1: btn-share visible en cualquier viewport
fc.assert(fc.property(
  fc.integer({ min: 320, max: 1920 }),
  (vw) => {
    // Simular viewport y verificar computed style
    // btn-share display !== 'none'
  }
), { numRuns: 100 });

// Feature: mobile-share-image, Property 2: ShareEngine.generate produce canvas correcto
fc.assert(fc.property(
  fc.record({
    mote:     fc.string({ minLength: 1, maxLength: 20 }),
    score:    fc.nat(),
    rank:     fc.integer({ min: 1, max: 100 }),
    hits:     fc.nat({ max: 8 }),
    timeLeft: fc.integer({ min: 0, max: 60 }),
  }),
  async (shareData) => {
    const canvas = await ShareEngine.generate(shareData);
    return canvas.width === 1080 && canvas.height === 1920;
  }
), { numRuns: 100 });

// Feature: mobile-share-image, Property 3: Preview no excede viewport
fc.assert(fc.property(
  fc.integer({ min: 320, max: 1023 }),
  (vw) => {
    const previewW = Math.min(270, vw - 48);
    return previewW <= vw;
  }
), { numRuns: 100 });

// Feature: mobile-share-image, Property 4: btn-share-native re-habilitado tras shareNative
fc.assert(fc.property(
  fc.boolean(), // true = éxito, false = AbortError
  async (succeeds) => {
    // Mock navigator.share
    // Verificar que btn.disabled === false y btn.textContent === '↗ COMPARTIR' al final
  }
), { numRuns: 100 });
```
