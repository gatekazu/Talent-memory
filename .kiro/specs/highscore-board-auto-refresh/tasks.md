# High Score Board Auto-Refresh — Tasks

## Tasks

- [x] 1. Exponer `renderMenuScoreboard` al scope global en `initMenu()`
  - [x] 1.1 Al final de `initMenu()`, después de la llamada a `renderMenuScoreboard()`, agregar `window.renderMenuScoreboard = renderMenuScoreboard;`
  - [x] 1.2 Verificar que `window.renderMenuScoreboard` es accesible desde la consola del navegador después del cambio

- [x] 2. Invocar `renderMenuScoreboard` en `Renderer.showScreen` al navegar al menú
  - [x] 2.1 En `Renderer.showScreen`, después de `GameState.screen = name;`, agregar la llamada condicional: `if (name === 'menu' && typeof window.renderMenuScoreboard === 'function') { window.renderMenuScoreboard(); }`

- [-] 3. Verificar el fix manualmente en el navegador
  - [x] 3.1 Jugar una partida, entrar al top 10, registrar mote y verificar que el tablero del menú muestra el nuevo puntaje al regresar
  - [ ] 3.2 Abrir la pantalla de Leaderboard, reiniciar marcadores y verificar que el tablero del menú aparece vacío al regresar
  - [ ] 3.3 Verificar que la primera carga del menú sigue funcionando correctamente (sin regresiones)
  - [ ] 3.4 Verificar que navegar a otras pantallas (juego, leaderboard, resultados) no tiene efectos secundarios en el tablero del menú
