# Documento de Requisitos de Bugfix

## Introducción

El tablero de High Scores del Menú Principal (`#menu-scoreboard`) no se actualiza automáticamente después de que el jugador registra un nuevo puntaje. La función `renderMenuScoreboard()` se invoca una única vez durante la inicialización del menú (`initMenu()`), por lo que cualquier entrada nueva guardada en `localStorage` durante una partida no se refleja en el tablero hasta que el usuario recarga manualmente la página. Esto rompe la experiencia arcade retro, donde el jugador espera ver su nombre en el tablero inmediatamente al regresar al menú.

---

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN el jugador completa una partida, registra su mote en el top 10 y regresa al Menú Principal THEN el sistema muestra el tablero de High Scores con los datos anteriores a la partida, sin incluir el nuevo puntaje recién guardado

1.2 WHEN el jugador completa una partida sin entrar al top 10 y regresa al Menú Principal THEN el sistema muestra el tablero de High Scores con los datos anteriores a la partida, sin reflejar ningún cambio

1.3 WHEN el administrador reinicia los marcadores desde la pantalla de Leaderboard y el jugador regresa al Menú Principal THEN el sistema muestra el tablero de High Scores con las entradas antiguas en lugar de mostrarlo vacío

### Expected Behavior (Correct)

2.1 WHEN el jugador completa una partida, registra su mote en el top 10 y regresa al Menú Principal THEN el sistema SHALL releer `localStorage` y volver a renderizar el tablero de High Scores mostrando el nuevo puntaje en su posición correcta

2.2 WHEN el jugador completa una partida sin entrar al top 10 y regresa al Menú Principal THEN el sistema SHALL releer `localStorage` y volver a renderizar el tablero de High Scores mostrando los datos actuales sin cambios

2.3 WHEN el administrador reinicia los marcadores desde la pantalla de Leaderboard y el jugador regresa al Menú Principal THEN el sistema SHALL releer `localStorage` y volver a renderizar el tablero de High Scores mostrando el estado vacío actualizado

### Unchanged Behavior (Regression Prevention)

3.1 WHEN el Menú Principal se carga por primera vez al abrir la página THEN el sistema SHALL CONTINUE TO renderizar el tablero de High Scores con los datos almacenados en `localStorage` en ese momento

3.2 WHEN el tablero de High Scores no tiene entradas almacenadas THEN el sistema SHALL CONTINUE TO mostrar el mensaje "¡SIN RÉCORDS AÚN!" con la invitación a jugar

3.3 WHEN el jugador navega al Menú Principal desde cualquier pantalla THEN el sistema SHALL CONTINUE TO mostrar todas las demás secciones del menú (título, botones, preview del tablero, créditos) sin cambios visuales ni funcionales

3.4 WHEN el jugador accede a la pantalla de Leaderboard completa desde el Menú Principal THEN el sistema SHALL CONTINUE TO mostrar la tabla completa de hasta 10 entradas con posición, mote, puntaje y fecha
