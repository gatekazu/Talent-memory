# High Score Board Auto-Refresh — Bugfix Design

## Overview

El tablero de High Scores del Menú Principal (`#menu-scoreboard`) no se refresca al regresar al menú después de una partida. La función `renderMenuScoreboard()` está definida dentro del IIFE `initMenu()` y solo se invoca una vez al cargar la página. La solución es exponer esa función (o una equivalente) al scope global para que `Renderer.showScreen('menu')` pueda invocarla cada vez que se navega al menú.

## Glossary

- **Bug_Condition (C)**: El usuario navega al Menú Principal (`showScreen('menu')`) después de que `initMenu()` ya se ejecutó, y `renderMenuScoreboard()` no vuelve a llamarse.
- **Property (P)**: Cada vez que la pantalla `menu` se activa, el tablero debe releer `localStorage` y re-renderizar su contenido.
- **Preservation**: El comportamiento de todas las demás pantallas, botones, animaciones y la primera carga del menú deben permanecer sin cambios.
- **renderMenuScoreboard**: Función en `index.html` (dentro de `initMenu()`) que lee `memorama_leaderboard` de `localStorage` y renderiza las filas en `#menu-scoreboard`.
- **showScreen**: Método de `Renderer` en `index.html` que oculta todas las secciones y activa la indicada.

## Bug Details

### Bug Condition

El bug se manifiesta cuando `Renderer.showScreen('menu')` es invocado desde cualquier pantalla (resultados, leaderboard, juego) después de la carga inicial. En ese momento `renderMenuScoreboard()` no es accesible fuera de `initMenu()` y no se vuelve a ejecutar.

**Formal Specification:**
```
FUNCTION isBugCondition(event)
  INPUT: event — una llamada a showScreen(name)
  OUTPUT: boolean

  RETURN name = 'menu'
         AND initMenu() ya fue ejecutado (página ya cargó)
         AND renderMenuScoreboard() NO es invocada durante showScreen
END FUNCTION
```

### Examples

- Jugador completa partida → entra al top 10 → regresa al menú → tablero muestra datos viejos (sin su nuevo puntaje).
- Admin reinicia leaderboard → regresa al menú → tablero sigue mostrando entradas antiguas.
- Jugador no entra al top 10 → regresa al menú → tablero correcto por coincidencia, pero no por diseño.

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- La primera carga del menú al abrir la página debe seguir mostrando el tablero correctamente.
- El mensaje "¡SIN RÉCORDS AÚN!" debe seguir apareciendo cuando no hay entradas.
- Todas las demás secciones del menú (título, botones, preview decorativo, créditos, partículas) deben permanecer sin cambios visuales ni funcionales.
- La pantalla de Leaderboard completa debe seguir funcionando igual.

**Scope:**
Todo input que NO sea navegar al menú (`showScreen('menu')`) debe quedar completamente sin afectar. Esto incluye:
- Clics en botones del menú
- Navegación a otras pantallas (juego, leaderboard, resultados)
- Animaciones y partículas del menú

## Hypothesized Root Cause

1. **Scope cerrado de `renderMenuScoreboard`**: La función está declarada con `function` dentro del IIFE `initMenu()`, por lo que no es accesible desde fuera. `showScreen` no tiene referencia a ella.

2. **`showScreen` no tiene hook de ciclo de vida**: El método solo cambia clases CSS; no tiene mecanismo para ejecutar lógica específica de cada pantalla al activarse.

3. **Sin evento de activación de pantalla**: No existe un evento o callback que se dispare cuando `screen-menu` se vuelve activa.

## Correctness Properties

Property 1: Bug Condition — Tablero se refresca al navegar al menú

_For any_ llamada a `Renderer.showScreen('menu')` (ya sea desde resultados, leaderboard o juego), el sistema SHALL releer `localStorage['memorama_leaderboard']` y re-renderizar el contenido de `#menu-scoreboard` con los datos actuales antes de que la pantalla sea visible.

**Validates: Requirements 2.1, 2.2, 2.3**

Property 2: Preservation — Comportamiento sin cambios para otras pantallas

_For any_ llamada a `Renderer.showScreen(name)` donde `name !== 'menu'`, el sistema SHALL producir exactamente el mismo resultado que antes del fix, sin ningún efecto secundario adicional.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4**

## Fix Implementation

### Changes Required

**File**: `index.html`

**Approach**: Exponer `renderMenuScoreboard` al scope global (o al objeto `Renderer`) para que `showScreen('menu')` pueda invocarla.

**Specific Changes**:

1. **Exponer la función al scope global**: Al final de `initMenu()`, asignar la función a `window.renderMenuScoreboard` para que sea accesible desde `Renderer`.

   ```js
   // Al final de initMenu(), después de renderMenuScoreboard():
   window.renderMenuScoreboard = renderMenuScoreboard;
   ```

2. **Invocar en `showScreen`**: Dentro de `Renderer.showScreen`, después de activar la clase `active`, si `name === 'menu'` y `window.renderMenuScoreboard` existe, invocarla.

   ```js
   showScreen(name) {
     VictoryBackground.stop();
     const screens = ['screen-menu', 'screen-game', 'screen-leaderboard', 'screen-results'];
     screens.forEach(id => {
       document.getElementById(id).classList.remove('active');
     });
     document.getElementById('screen-' + name).classList.add('active');
     GameState.screen = name;
     // Refrescar tablero al volver al menú
     if (name === 'menu' && typeof window.renderMenuScoreboard === 'function') {
       window.renderMenuScoreboard();
     }
   },
   ```

**Minimal impact**: Solo 2 cambios de 1-2 líneas cada uno. No se modifica la lógica de `renderMenuScoreboard` ni ninguna otra función.

## Testing Strategy

### Validation Approach

Primero verificar el bug en el código sin fix (exploratory), luego verificar que el fix lo resuelve (fix checking), y finalmente confirmar que no hay regresiones (preservation checking).

### Exploratory Bug Condition Checking

**Goal**: Confirmar que `renderMenuScoreboard` NO se llama al invocar `showScreen('menu')` en el código actual.

**Test Plan**: Agregar una entrada a `localStorage['memorama_leaderboard']` manualmente, llamar a `Renderer.showScreen('menu')` y verificar que `#menu-scoreboard` NO muestra la entrada nueva.

**Test Cases**:
1. **Post-partida con top 10**: Simular guardado de puntaje → llamar `showScreen('menu')` → verificar que el tablero no se actualizó (fallará en código sin fix).
2. **Reset de leaderboard**: Limpiar `localStorage` → llamar `showScreen('menu')` → verificar que el tablero sigue mostrando entradas antiguas (fallará en código sin fix).

**Expected Counterexamples**:
- `#menu-scoreboard` muestra datos desactualizados después de `showScreen('menu')`.

### Fix Checking

**Goal**: Verificar que tras el fix, cada llamada a `showScreen('menu')` re-renderiza el tablero con datos actuales.

**Pseudocode:**
```
FOR ALL event WHERE isBugCondition(event) DO
  result := showScreen_fixed('menu')
  ASSERT menuScoreboardContent = localStorage['memorama_leaderboard'] actual
END FOR
```

### Preservation Checking

**Goal**: Verificar que `showScreen` para otras pantallas no tiene efectos secundarios nuevos.

**Pseudocode:**
```
FOR ALL name WHERE name != 'menu' DO
  ASSERT showScreen_original(name) = showScreen_fixed(name)
END FOR
```

**Test Cases**:
1. **showScreen('game')**: Verificar que no llama a `renderMenuScoreboard`.
2. **showScreen('leaderboard')**: Verificar que no llama a `renderMenuScoreboard`.
3. **showScreen('results')**: Verificar que no llama a `renderMenuScoreboard`.
4. **Primera carga del menú**: Verificar que `initMenu()` sigue llamando a `renderMenuScoreboard()` directamente (sin cambios).

### Unit Tests

- Verificar que `window.renderMenuScoreboard` existe después de que `initMenu()` se ejecuta.
- Verificar que `showScreen('menu')` invoca `renderMenuScoreboard`.
- Verificar que `showScreen('game')` NO invoca `renderMenuScoreboard`.
- Verificar que el tablero muestra "¡SIN RÉCORDS AÚN!" cuando `localStorage` está vacío al navegar al menú.

### Property-Based Tests

- Para cualquier estado de `localStorage` (vacío, 1 entrada, 10 entradas), navegar al menú siempre muestra el estado actual.
- Para cualquier pantalla distinta de `menu`, `showScreen` no modifica `#menu-scoreboard`.

### Integration Tests

- Flujo completo: jugar → entrar al top 10 → registrar mote → regresar al menú → verificar que el nuevo puntaje aparece en el tablero.
- Flujo completo: admin reinicia leaderboard → regresar al menú → verificar que el tablero está vacío.
