# Documento de Requisitos de Bugfix

## Introducción

El marcador de puntajes (leaderboard / high scores) muestra datos diferentes en desktop y en mobile, cuando ambos dispositivos deberían ver exactamente el mismo marcador compartido. La causa raíz es que `LeaderboardManager` almacena y lee los puntajes exclusivamente en `localStorage`, que es un almacenamiento **local al navegador y al dispositivo**. Cada dispositivo (PC, teléfono) tiene su propio `localStorage` completamente aislado, por lo que los puntajes registrados en desktop nunca llegan a mobile y viceversa. El juego corre sobre un servidor HTTP local (`python -m http.server 8080`) que sirve el archivo estático `index.html`, pero no persiste ningún dato del lado del servidor. Para que el marcador sea compartido entre todos los dispositivos de la red, los puntajes deben almacenarse en el servidor y ser accesibles vía HTTP desde cualquier cliente.

---

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN un jugador en desktop registra un puntaje y otro jugador en mobile abre el leaderboard THEN el sistema muestra marcadores distintos porque cada dispositivo lee su propio `localStorage` local

1.2 WHEN un jugador en mobile registra un puntaje y luego abre el leaderboard en desktop THEN el sistema no muestra el puntaje del jugador mobile porque `localStorage` no se comparte entre dispositivos

1.3 WHEN el administrador reinicia los marcadores desde desktop THEN el sistema solo borra el `localStorage` del navegador desktop, dejando intactos los marcadores en mobile y en cualquier otro dispositivo

1.4 WHEN el menú principal se carga en mobile THEN el sistema muestra el scoreboard decorativo (`#menu-scoreboard`) con los datos del `localStorage` del teléfono, que difieren de los datos del desktop

### Expected Behavior (Correct)

2.1 WHEN un jugador en desktop registra un puntaje y otro jugador en mobile abre el leaderboard THEN el sistema SHALL mostrar el mismo marcador compartido incluyendo el puntaje recién registrado desde desktop

2.2 WHEN un jugador en mobile registra un puntaje y luego abre el leaderboard en desktop THEN el sistema SHALL mostrar el puntaje del jugador mobile en la posición correcta del marcador compartido

2.3 WHEN el administrador reinicia los marcadores desde cualquier dispositivo THEN el sistema SHALL borrar el marcador compartido de forma que todos los dispositivos vean el marcador vacío

2.4 WHEN el menú principal se carga en cualquier dispositivo THEN el sistema SHALL mostrar el scoreboard decorativo (`#menu-scoreboard`) con los mismos datos del marcador compartido

### Unchanged Behavior (Regression Prevention)

3.1 WHEN un jugador completa una partida y califica para el top 10 THEN el sistema SHALL CONTINUE TO solicitar el mote del jugador y guardar la entrada con mote, puntaje y fecha

3.2 WHEN un jugador completa una partida sin calificar para el top 10 THEN el sistema SHALL CONTINUE TO mostrar la pantalla de resultados sin solicitar mote ni guardar entrada

3.3 WHEN el leaderboard tiene 10 entradas y llega un puntaje mayor al mínimo THEN el sistema SHALL CONTINUE TO desplazar la entrada de menor puntaje y mantener solo las 10 mejores

3.4 WHEN el jugador accede a la pantalla de Leaderboard completa THEN el sistema SHALL CONTINUE TO mostrar la tabla con posición, mote, puntaje y fecha de hasta 10 entradas

3.5 WHEN el servidor local no está disponible o hay un error de red THEN el sistema SHALL CONTINUE TO permitir jugar, mostrando el marcador vacío o el último estado conocido sin bloquear la experiencia de juego
