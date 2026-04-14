# Unified Scoreboard Bugfix Design

## Overview

El marcador de puntajes muestra datos distintos en cada dispositivo porque `LeaderboardManager` persiste y lee los puntajes exclusivamente en `localStorage`, que es local al navegador y al dispositivo. El servidor actual (`python -m http.server 8080`) solo sirve archivos estáticos y no puede almacenar datos compartidos.

La solución reemplaza el servidor estático de Python con un servidor HTTP mínimo escrito en Python que, además de servir los archivos estáticos, expone una API REST simple (`GET /api/scores` y `POST /api/scores` y `DELETE /api/scores`) que lee y escribe los puntajes en un archivo `scores.json` en el servidor. El cliente (`LeaderboardManager`) se adapta para comunicarse con esta API en lugar de usar `localStorage`.

## Glossary

- **Bug_Condition (C)**: La condición que activa el bug — cuando dos dispositivos distintos leen el leaderboard y obtienen datos diferentes porque cada uno usa su propio `localStorage`.
- **Property (P)**: El comportamiento correcto — todos los dispositivos en la misma red deben leer y escribir en el mismo marcador compartido vía HTTP.
- **Preservation**: El flujo de juego existente (guardar mote, calificar al top 10, reiniciar marcadores con contraseña, mostrar resultados) debe continuar funcionando exactamente igual.
- **LeaderboardManager**: El módulo IIFE en `index.html` que encapsula toda la lógica de persistencia del leaderboard.
- **renderMenuScoreboard**: Función en `index.html` que renderiza el scoreboard decorativo del menú principal (`#menu-scoreboard`).
- **scores.json**: Archivo JSON en el servidor que actúa como base de datos compartida del leaderboard.
- **server.py**: Nuevo servidor Python que reemplaza `python -m http.server 8080`, sirviendo archivos estáticos y la API de scores.
- **API de scores**: Tres endpoints HTTP: `GET /api/scores`, `POST /api/scores`, `DELETE /api/scores`.

## Bug Details

### Bug Condition

El bug se manifiesta cuando dos o más dispositivos acceden al leaderboard. Cada dispositivo lee y escribe en su propio `localStorage`, completamente aislado del resto. No existe ningún mecanismo de sincronización entre dispositivos.

**Formal Specification:**
```
FUNCTION isBugCondition(context)
  INPUT: context = { deviceA, deviceB, network }
  OUTPUT: boolean

  RETURN deviceA.localStorage['memorama_leaderboard'] != deviceB.localStorage['memorama_leaderboard']
         AND deviceA.network == deviceB.network
         AND expectedSharedLeaderboard(deviceA, deviceB) == true
END FUNCTION
```

### Examples

- **Desktop registra puntaje, mobile abre leaderboard**: Desktop guarda en su `localStorage`, mobile lee su propio `localStorage` vacío → marcadores distintos.
- **Mobile registra puntaje, desktop abre leaderboard**: Mobile guarda en su `localStorage`, desktop no ve ese puntaje → marcadores distintos.
- **Admin reinicia desde desktop**: Solo borra el `localStorage` del desktop; mobile y otros dispositivos conservan sus marcadores → estado inconsistente.
- **Menú principal en mobile**: `renderMenuScoreboard` lee `localStorage` del teléfono → muestra datos distintos al desktop.

## Expected Behavior

### Preservation Requirements

**Unchanged Behaviors:**
- El flujo de solicitar mote al jugador cuando califica al top 10 debe continuar igual.
- La lógica de `qualifies(score)` (top 10) debe continuar funcionando.
- La pantalla de resultados con posición, puntaje, hits y tiempo restante debe continuar igual.
- La tabla del leaderboard completo (posición, mote, puntaje, fecha) debe continuar mostrándose igual.
- El reinicio de marcadores con contraseña (`!Talentland`) debe continuar funcionando.
- El scoreboard decorativo del menú (`#menu-scoreboard`) debe continuar renderizándose.
- Si el servidor no está disponible, el juego debe continuar funcionando (marcador vacío o degradado).

**Scope:**
Todo lo que no involucre leer o escribir puntajes en el leaderboard debe quedar completamente sin cambios. Esto incluye:
- Lógica del tablero de cartas, temporizador, motor de puntaje.
- Audio, animaciones, partículas, estilos visuales.
- Navegación entre pantallas.
- Modal de mote (solo cambia el destino de persistencia, no la UI).

## Hypothesized Root Cause

1. **Almacenamiento local no compartido**: `LeaderboardManager._load()` y `_save()` usan `localStorage` que es exclusivo de cada navegador/dispositivo. No existe ningún mecanismo de sincronización.

2. **Servidor sin capacidad de API**: `python -m http.server` solo sirve archivos estáticos. No puede recibir `POST` ni persistir datos del lado del servidor.

3. **`renderMenuScoreboard` lee `localStorage` directamente**: La función en el bloque de inicialización lee `localStorage.getItem('memorama_leaderboard')` en lugar de pasar por `LeaderboardManager`, lo que crea un segundo punto de acoplamiento al almacenamiento local.

4. **Sin fallback de red**: `LeaderboardManager` no tiene lógica para comunicarse con un servidor HTTP; toda la lógica asume almacenamiento síncrono local.

## Correctness Properties

Property 1: Bug Condition - Marcador Compartido Entre Dispositivos

_For any_ par de dispositivos en la misma red donde el bug condition se cumple (un dispositivo registra un puntaje y otro dispositivo consulta el leaderboard), el sistema corregido SHALL retornar el mismo conjunto de entradas del leaderboard en ambos dispositivos, reflejando todos los puntajes registrados desde cualquier dispositivo.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

Property 2: Preservation - Comportamiento Sin Cambios Para Flujos Existentes

_For any_ acción del usuario que no involucre leer o escribir el leaderboard (jugar una partida, navegar entre pantallas, usar audio, ver animaciones), el sistema corregido SHALL producir exactamente el mismo resultado que el sistema original, preservando toda la funcionalidad existente.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

## Fix Implementation

### Changes Required

**Archivo nuevo**: `server.py`

Servidor HTTP Python que reemplaza `python -m http.server 8080`. Extiende `SimpleHTTPRequestHandler` para interceptar rutas `/api/scores` y delegar el resto al handler estático.

**Endpoints:**
- `GET /api/scores` → lee `scores.json`, retorna `[]` si no existe. Response: `200 application/json`.
- `POST /api/scores` → recibe body JSON con el array completo de entradas, escribe `scores.json`. Response: `200 application/json`.
- `DELETE /api/scores` → escribe `scores.json` con `[]`. Response: `200 application/json`.
- Cualquier otra ruta → delegada al handler estático de Python (sirve `index.html`, assets, etc.).

**Cabeceras CORS**: Incluir `Access-Control-Allow-Origin: *` en todas las respuestas de la API para permitir peticiones desde cualquier origen en la red local.

```
FUNCTION handleRequest(method, path, body)
  IF path == '/api/scores' THEN
    IF method == 'GET' THEN
      entries = readFile('scores.json') OR []
      RETURN 200, entries
    ELSE IF method == 'POST' THEN
      writeFile('scores.json', body)
      RETURN 200, { ok: true }
    ELSE IF method == 'DELETE' THEN
      writeFile('scores.json', [])
      RETURN 200, { ok: true }
    ELSE IF method == 'OPTIONS' THEN
      RETURN 200  // preflight CORS
    END IF
  ELSE
    DELEGATE to SimpleHTTPRequestHandler
  END IF
END FUNCTION
```

---

**Archivo modificado**: `index.html` — `LeaderboardManager`

Reemplazar la implementación síncrona basada en `localStorage` por una implementación asíncrona basada en `fetch`. Dado que la API es asíncrona, los métodos públicos que antes eran síncronos deben retornar Promises.

**Cambios específicos:**

1. **`_load()` → `_loadAsync()`**: `fetch('/api/scores')` con fallback a `[]` en caso de error de red.

2. **`_save(entries)` → `_saveAsync(entries)`**: `fetch('/api/scores', { method: 'POST', body: JSON.stringify(entries) })` con manejo de error silencioso.

3. **`getAll()` → async**: Retorna `Promise<Entry[]>`.

4. **`qualifies(score)` → async**: Retorna `Promise<boolean>`.

5. **`insert(entry)` → async**: Retorna `Promise<number>` (posición 1-based).

6. **`clear(password)` → async**: Valida contraseña en cliente, luego llama `fetch('/api/scores', { method: 'DELETE' })`. Retorna `Promise<boolean>`.

7. **`getRank(score)` → async**: Retorna `Promise<number|null>`.

8. **`renderMenuScoreboard()`**: Cambiar para llamar `LeaderboardManager.getAll().then(entries => ...)` en lugar de leer `localStorage` directamente.

9. **Todos los call sites**: Actualizar para usar `await` o `.then()`:
   - `Renderer.renderLeaderboard(await LeaderboardManager.getAll())`
   - `if (await LeaderboardManager.qualifies(score))`
   - `const rank = await LeaderboardManager.insert(entry)`
   - `const ok = await LeaderboardManager.clear(password)`
   - `const rank = await LeaderboardManager.getRank(score)`

---

**Archivos modificados**: `start.bat`, `start.sh`, `restart-server.bat`

Reemplazar `python -m http.server %PORT%` por `python server.py` (o `python3 server.py`).

---

**Archivo nuevo**: `scores.json` (generado automáticamente por `server.py` en primera escritura, no necesita crearse manualmente).

### Fallback de Red (Req 3.5)

Cuando `fetch` falla (servidor no disponible), `_loadAsync()` retorna `[]` y `_saveAsync()` falla silenciosamente. El juego continúa funcionando con marcador vacío. No se bloquea ninguna pantalla.

## Testing Strategy

### Validation Approach

La estrategia sigue dos fases: primero confirmar el bug en el código sin corregir (exploratory), luego verificar que el fix funciona y no introduce regresiones (fix checking + preservation checking).

### Exploratory Bug Condition Checking

**Goal**: Demostrar que dos instancias del `LeaderboardManager` original con `localStorage` aislados retornan datos distintos después de que una inserta una entrada.

**Test Plan**: Simular dos "dispositivos" usando dos instancias de `localStorage` mock independientes. Insertar una entrada en el dispositivo A y verificar que el dispositivo B no la ve.

**Test Cases**:
1. **Aislamiento de localStorage**: Dispositivo A inserta `{ mote: 'AAA', score: 100 }`, dispositivo B llama `getAll()` → retorna `[]` (falla en código corregido, confirma bug en original).
2. **Reinicio no propagado**: Dispositivo A llama `clear('!Talentland')`, dispositivo B llama `getAll()` → sigue retornando entradas previas.
3. **Menú scoreboard desincronizado**: `renderMenuScoreboard` en dispositivo B muestra `[]` aunque dispositivo A tenga entradas.

**Expected Counterexamples**:
- `getAll()` en dispositivo B retorna `[]` cuando dispositivo A tiene entradas → confirma aislamiento de `localStorage`.

### Fix Checking

**Goal**: Verificar que después del fix, todos los dispositivos leen el mismo marcador compartido.

**Pseudocode:**
```
FOR ALL (deviceA, deviceB) WHERE isBugCondition(deviceA, deviceB) DO
  deviceA.LeaderboardManager.insert({ mote: 'TEST', score: 999, date: now })
  result = deviceB.LeaderboardManager.getAll()
  ASSERT result.some(e => e.mote == 'TEST' AND e.score == 999)
END FOR
```

### Preservation Checking

**Goal**: Verificar que para todas las acciones que no involucran el leaderboard, el comportamiento es idéntico al original.

**Pseudocode:**
```
FOR ALL action WHERE NOT isBugCondition(action) DO
  ASSERT original_behavior(action) == fixed_behavior(action)
END FOR
```

**Testing Approach**: Tests unitarios para la lógica de negocio del leaderboard (qualifies, insert ordering, clear con contraseña incorrecta) usando un servidor mock. Property-based tests para verificar que el ordenamiento y el límite de 10 entradas se mantienen con entradas aleatorias.

**Test Cases**:
1. **qualifies con top lleno**: Insertar 10 entradas, verificar que `qualifies(score_menor)` retorna `false`.
2. **insert mantiene orden DESC**: Insertar entradas en orden aleatorio, verificar que `getAll()` retorna orden descendente.
3. **clear con contraseña incorrecta**: Verificar que `clear('wrong')` retorna `false` y no borra datos.
4. **Fallback de red**: Con servidor no disponible, `getAll()` retorna `[]` sin lanzar excepción.

### Unit Tests

- Test `GET /api/scores` retorna `[]` cuando `scores.json` no existe.
- Test `POST /api/scores` escribe correctamente y `GET` posterior retorna los mismos datos.
- Test `DELETE /api/scores` vacía el marcador.
- Test `LeaderboardManager.insert()` mantiene máximo 10 entradas y orden DESC.
- Test `LeaderboardManager.clear()` con contraseña correcta e incorrecta.
- Test `LeaderboardManager.qualifies()` en top lleno y top con espacio.

### Property-Based Tests

- Para cualquier lista de N entradas (N > 10) insertadas en orden aleatorio, `getAll()` retorna exactamente 10 entradas ordenadas DESC por score.
- Para cualquier score S, `qualifies(S)` retorna `true` si y solo si `getAll().length < 10 OR S > min(getAll().scores)`.
- Para cualquier acción que no sea insert/clear, el estado del leaderboard no cambia.

### Integration Tests

- Test end-to-end: iniciar `server.py`, insertar puntaje desde cliente A (fetch), leer desde cliente B (fetch) → mismo resultado.
- Test reinicio: insertar entradas, llamar `DELETE /api/scores`, verificar que `GET /api/scores` retorna `[]`.
- Test fallback: detener servidor, llamar `LeaderboardManager.getAll()` → retorna `[]` sin error visible al usuario.
- Test `renderMenuScoreboard`: después de insertar entradas vía API, navegar al menú → scoreboard decorativo muestra las entradas correctas.
