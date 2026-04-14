# Documento de Requisitos

## Introducción

Memorama Arcade Retro es un juego de memoria estilo 8-bit ambientado en la estética arcade de los años 80. El jugador debe encontrar pares de cartas en un tablero, gestionando un banco de tiempo dinámico que aumenta con los aciertos y disminuye con los errores. El juego incluye un leaderboard local persistente con los 10 mejores puntajes, sonidos generados por Web Audio API y una interfaz completamente retro con fuentes y colores neón. Todo el juego se entrega en un único archivo HTML autocontenido.

---

## Glosario

- **Juego**: La aplicación completa de Memorama Arcade Retro.
- **Pantalla de Victoria**: La instancia de `#screen-results` cuando `data.victory === true`, que muestra "¡VICTORIA!", puntaje, ranking, aciertos, tiempo restante y botones de acción.
- **Background de Victoria**: El fondo animado y dinámico exclusivo de la Pantalla de Victoria, compuesto por capas CSS y partículas JS que refuerzan la estética arcade retro neón.
- **Partícula de Victoria**: Elemento DOM generado dinámicamente (estrella, símbolo retro, destello) que flota o cae sobre el fondo de la Pantalla de Victoria.
- **Paleta Neón**: Conjunto de colores `#00ff41` (verde), `#00ffff` (cyan), `#ff00ff` (magenta), `#ffff00` (amarillo) usados en toda la interfaz del Juego.
- **Tablero**: La cuadrícula de cartas boca abajo que el jugador debe resolver.
- **Carta**: Elemento visual con un reverso (logo Talent Land) y un frente (símbolo o imagen del par).
- **Par**: Dos cartas con el mismo símbolo en el frente.
- **Flip**: Animación CSS 3D que voltea una carta de reverso a frente o viceversa.
- **Banco de Tiempo**: Contador de segundos que se incrementa con aciertos y decrementa con errores.
- **Acierto**: Evento que ocurre cuando el jugador voltea dos cartas con el mismo símbolo.
- **Error**: Evento que ocurre cuando el jugador voltea dos cartas con símbolos distintos.
- **Racha**: Número de aciertos consecutivos sin errores.
- **Puntaje**: Valor numérico calculado al finalizar la partida: `(Aciertos × 100) + (Tiempo Restante × 50)`.
- **Mote**: Alias de hasta 4 caracteres que el jugador ingresa al entrar al top 10.
- **Leaderboard**: Tabla de los 10 mejores puntajes almacenada en localStorage.
- **Motor de Audio**: Módulo basado en Web Audio API que genera sonidos de bits en tiempo real.
- **Modal Retro**: Ventana de diálogo construida en el DOM con estética 8-bit, sin usar `prompt()` nativo.
- **Menú Principal**: Pantalla de inicio con opciones para comenzar el juego y ver el leaderboard.
- **Panel de Estadísticas**: Área lateral visible durante la partida que muestra Tiempo, Aciertos y Racha.
- **Tarjeta de Resultado**: Imagen generada con Canvas API al finalizar la partida, con estética retro, que muestra el puntaje, posición en el leaderboard y créditos del evento.
- **Compartir en Stories**: Funcionalidad que permite al jugador descargar o compartir la Tarjeta de Resultado como imagen para redes sociales (formato vertical 9:16).
- **Botón Salir**: Control visible durante la partida que permite al jugador iniciar el flujo de abandono de la partida en curso.
- **Modal de Confirmación de Salida**: Modal Retro que advierte al jugador que abandonar la partida descartará el puntaje actual y solicita confirmación explícita.

---

## Requisitos

### Requisito 1: Menú Principal

**User Story:** Como jugador, quiero ver un menú de inicio con estética retro, para poder comenzar una partida o consultar el leaderboard antes de jugar.

#### Criterios de Aceptación

1. THE Juego SHALL mostrar el Menú Principal al cargar la página por primera vez.
2. THE Menú Principal SHALL mostrar el título "MEMORAMA ARCADE" con la fuente "Press Start 2P" y colores neón sobre fondo oscuro.
3. THE Menú Principal SHALL presentar un botón "INICIAR JUEGO" y un botón "LEADERBOARD".
4. WHEN el jugador hace clic en "INICIAR JUEGO", THE Juego SHALL ocultar el Menú Principal y mostrar el Tablero con el Panel de Estadísticas.
5. WHEN el jugador hace clic en "LEADERBOARD", THE Juego SHALL mostrar la pantalla del Leaderboard con los puntajes almacenados.

---

### Requisito 2: Tablero de Cartas

**User Story:** Como jugador, quiero ver un tablero de cartas boca abajo, para poder seleccionarlas e intentar encontrar pares.

#### Criterios de Aceptación

1. THE Tablero SHALL contener un número par de Cartas, distribuidas en una cuadrícula de 4×4 (16 cartas, 8 pares) como configuración base.
2. THE Juego SHALL distribuir las Cartas en posiciones aleatorias al inicio de cada partida.
3. THE Carta SHALL mostrar el reverso con el SVG embebido del logo de Talent Land mientras no haya sido volteada ni emparejada.
4. WHEN el jugador hace clic en una Carta boca abajo, THE Carta SHALL ejecutar la animación de Flip mostrando el frente con su símbolo.
5. THE Flip SHALL ser una animación CSS 3D con duración de 400ms o menos.
6. WHILE dos Cartas están volteadas y en proceso de evaluación, THE Tablero SHALL ignorar clics adicionales sobre otras Cartas.
7. WHEN un Par es encontrado, THE Juego SHALL mantener ambas Cartas visibles con el frente hacia arriba de forma permanente.
8. IF el jugador intenta hacer clic en una Carta ya emparejada, THEN THE Tablero SHALL ignorar dicho clic.

---

### Requisito 3: Mecánica del Banco de Tiempo

**User Story:** Como jugador, quiero que el tiempo sea un recurso dinámico que gestiono con mis decisiones, para que el juego sea más desafiante y estratégico.

#### Criterios de Aceptación

1. THE Banco de Tiempo SHALL iniciar con 60 segundos al comenzar una partida.
2. THE Banco de Tiempo SHALL decrementar en 1 segundo cada segundo transcurrido durante la partida.
3. WHEN ocurre un Acierto, THE Banco de Tiempo SHALL incrementarse en 3 segundos.
4. WHEN ocurre un Error, THE Banco de Tiempo SHALL decrementarse en 2 segundos adicionales al decremento natural.
5. IF el Banco de Tiempo llega a 0 segundos, THEN THE Juego SHALL detener la partida y mostrar la pantalla de Game Over.
6. WHEN el jugador completa todos los pares del Tablero, THE Juego SHALL detener el Banco de Tiempo y mostrar la pantalla de victoria.
7. THE Panel de Estadísticas SHALL mostrar el valor actual del Banco de Tiempo actualizado cada segundo.

---

### Requisito 4: Sistema de Puntaje

**User Story:** Como jugador, quiero obtener un puntaje al finalizar la partida, para poder comparar mi desempeño con otros jugadores.

#### Criterios de Aceptación

1. WHEN la partida finaliza, THE Juego SHALL calcular el Puntaje usando la fórmula: `Puntaje = (Aciertos × 100) + (Tiempo Restante × 50)`.
2. THE Panel de Estadísticas SHALL mostrar el contador de Aciertos actualizado en tiempo real durante la partida.
3. THE Panel de Estadísticas SHALL mostrar la Racha actual actualizada en tiempo real durante la partida.
4. WHEN ocurre un Error, THE Juego SHALL reiniciar el contador de Racha a 0.
5. WHEN ocurre un Acierto, THE Juego SHALL incrementar el contador de Racha en 1.
6. WHEN la partida finaliza, THE Juego SHALL mostrar el Puntaje final en la pantalla de resultado.

---

### Requisito 5: Leaderboard Local

**User Story:** Como jugador, quiero que mis mejores puntajes se guarden localmente, para poder ver mi progreso y competir contra mis marcas anteriores.

#### Criterios de Aceptación

1. THE Leaderboard SHALL almacenar hasta 10 entradas en localStorage, cada una con Mote, Puntaje y fecha de la partida.
2. WHEN la partida finaliza y el Puntaje es mayor al décimo lugar del Leaderboard (o el Leaderboard tiene menos de 10 entradas), THE Juego SHALL mostrar un Modal Retro solicitando al jugador que ingrese su Mote.
3. THE Mote SHALL aceptar un máximo de 4 caracteres alfanuméricos.
4. WHEN el jugador confirma su Mote, THE Juego SHALL insertar la nueva entrada en el Leaderboard ordenado de mayor a menor Puntaje.
5. IF el Leaderboard ya contiene 10 entradas y la nueva entrada supera a la décima, THEN THE Juego SHALL eliminar la entrada de menor Puntaje para dar lugar a la nueva.
6. THE Leaderboard SHALL mostrar las entradas con fuente "Press Start 2P" en formato de tabla con columnas: Posición, Mote, Puntaje y Fecha.
7. WHEN el jugador accede al Leaderboard desde el Menú Principal, THE Juego SHALL leer y mostrar las entradas almacenadas en localStorage.

---

### Requisito 6: Reinicio de Marcadores Protegido

**User Story:** Como administrador del evento, quiero poder limpiar el leaderboard con una contraseña, para reiniciar la competencia entre participantes.

#### Criterios de Aceptación

1. THE Leaderboard SHALL mostrar un botón "REINICIAR MARCADORES".
2. WHEN el jugador hace clic en "REINICIAR MARCADORES", THE Juego SHALL mostrar un Modal Retro con un campo de texto para ingresar la contraseña.
3. THE Modal Retro SHALL construirse en el DOM con estética 8-bit y NO SHALL usar `prompt()`, `alert()` ni `confirm()` nativos del navegador.
4. WHEN el jugador ingresa la contraseña correcta `!Talentland` y confirma, THE Juego SHALL eliminar todas las entradas del Leaderboard en localStorage y mostrar el Leaderboard vacío.
5. IF el jugador ingresa una contraseña incorrecta, THEN THE Juego SHALL mostrar un mensaje de error "CONTRASEÑA INCORRECTA" dentro del Modal Retro sin cerrarlo.
6. WHEN el jugador cancela el Modal Retro, THE Juego SHALL cerrar el modal sin realizar cambios en el Leaderboard.

---

### Requisito 7: Motor de Audio con Web Audio API

**User Story:** Como jugador, quiero escuchar efectos de sonido retro durante el juego, para que la experiencia sea más inmersiva y fiel al estilo arcade.

#### Criterios de Aceptación

1. THE Motor de Audio SHALL generar todos los sonidos usando exclusivamente la Web Audio API, sin archivos de audio externos.
2. WHEN ocurre un Acierto, THE Motor de Audio SHALL reproducir un sonido de tono ascendente estilo 8-bit con duración máxima de 500ms.
3. WHEN ocurre un Error, THE Motor de Audio SHALL reproducir un sonido de tono descendente o disonante estilo 8-bit con duración máxima de 500ms.
4. WHEN el Banco de Tiempo llega a 0, THE Motor de Audio SHALL reproducir una secuencia de sonido de Game Over estilo 8-bit.
5. WHEN el jugador completa todos los pares, THE Motor de Audio SHALL reproducir una secuencia de victoria estilo 8-bit.
6. WHERE el navegador no soporte Web Audio API, THE Juego SHALL continuar funcionando sin audio sin mostrar errores al usuario.

---

### Requisito 8: Estética Visual Retro

**User Story:** Como jugador, quiero que toda la interfaz tenga una estética arcade de los años 80, para que la experiencia sea visualmente coherente y atractiva.

#### Criterios de Aceptación

1. THE Juego SHALL usar la fuente "Press Start 2P" de Google Fonts en todos los textos visibles.
2. THE Juego SHALL usar una paleta de colores neón (verde, cian, magenta, amarillo) sobre fondo oscuro (#0a0a0a o similar) en todos los elementos de la interfaz.
3. THE Carta SHALL mostrar el SVG embebido del logo de Talent Land en el reverso, con dimensiones proporcionales al tamaño de la carta.
4. THE Juego SHALL aplicar efectos de resplandor (CSS `text-shadow` y `box-shadow`) a los elementos de texto y bordes para simular el efecto neón.
5. THE Juego SHALL ser responsive y funcionar correctamente en resoluciones de escritorio (mínimo 1024px de ancho) y en dispositivos móviles (mínimo 320px de ancho).
6. THE Panel de Estadísticas SHALL ubicarse de forma lateral al Tablero en pantallas de escritorio y de forma apilada (encima o debajo) en pantallas móviles.

---

### Requisito 9: Estructura Técnica del Proyecto

**User Story:** Como desarrollador, quiero que el juego esté contenido en un único archivo HTML autocontenido, para facilitar su distribución y ejecución sin dependencias de servidor.

#### Criterios de Aceptación

1. THE Juego SHALL estar contenido en un único archivo `index.html` que incluya todo el CSS en etiquetas `<style>` y todo el JavaScript en etiquetas `<script>`.
2. THE Juego SHALL cargar la fuente "Press Start 2P" desde Google Fonts mediante un `<link>` en el `<head>`.
3. THE Juego SHALL funcionar correctamente al abrir el archivo `index.html` directamente en un navegador moderno (Chrome, Firefox, Edge) sin necesidad de servidor web.
4. THE SVG del logo de Talent Land SHALL estar embebido directamente en el código HTML o JavaScript, sin requerir archivos externos.
5. THE Juego SHALL usar únicamente JavaScript puro (Vanilla JS) sin frameworks ni librerías externas, a excepción de la fuente de Google Fonts.

---

### Requisito 10: Pantalla de Resultados con Posición en Leaderboard

**User Story:** Como jugador, quiero ver mi posición final en el leaderboard junto con mi puntaje al terminar la partida, para saber exactamente cómo quedé en la competencia.

#### Criterios de Aceptación

1. WHEN la partida finaliza (por victoria o Game Over), THE Juego SHALL mostrar una pantalla de resultados con estética retro antes de cualquier otro modal.
2. THE Pantalla de Resultados SHALL mostrar: el Puntaje final, el número de Aciertos, el tiempo restante (si aplica) y la posición obtenida en el Leaderboard (ej. "#3 EN EL RANKING").
3. IF el Puntaje no entra en el top 10, THE Pantalla de Resultados SHALL mostrar el mensaje "FUERA DEL TOP 10" en lugar de la posición.
4. THE Pantalla de Resultados SHALL mostrar los créditos del evento: "TALENT LAND 2026", "POWERED BY KIRO AWS" y "AUTOR: KAZU SHIRAKI" con fuente "Press Start 2P" y colores neón.
5. THE Pantalla de Resultados SHALL presentar un botón "COMPARTIR" y un botón "JUGAR DE NUEVO".

---

### Requisito 11: Tarjeta de Resultado Compartible (Stories)

**User Story:** Como jugador, quiero generar y compartir una imagen de mi resultado en formato Stories, para presumir mi puntaje en redes sociales.

#### Criterios de Aceptación

1. WHEN el jugador hace clic en "COMPARTIR", THE Juego SHALL generar una Tarjeta de Resultado usando la Canvas API con dimensiones 1080×1920px (formato vertical 9:16 para Stories).
2. THE Tarjeta de Resultado SHALL incluir en el canvas:
   - Fondo oscuro (#0a0a0a) con bordes y detalles en colores neón estilo 8-bit.
   - El logo de Talent Land (SVG embebido renderizado en canvas) en la parte superior.
   - El título "MEMORAMA ARCADE" con fuente "Press Start 2P" y efecto neón.
   - El Mote del jugador (si fue registrado) o "JUGADOR" como nombre.
   - El Puntaje final destacado en grande.
   - La posición en el Leaderboard (ej. "#1 EN EL RANKING" o "FUERA DEL TOP 10").
   - Los créditos: "TALENT LAND 2026", "POWERED BY KIRO AWS", "AUTOR: KAZU SHIRAKI".
3. THE Juego SHALL ofrecer al jugador tres opciones para compartir/guardar la Tarjeta:
   - **Descargar imagen**: Genera un archivo PNG descargable directamente desde el navegador.
   - **Compartir nativo**: IF el navegador soporta la Web Share API con archivos, THE Juego SHALL invocar `navigator.share()` con la imagen para compartir directamente a apps (Instagram Stories, WhatsApp, etc.).
   - **Código QR**: THE Juego SHALL generar un QR que apunte a la URL del juego (o una URL configurable), permitiendo que otros jugadores accedan escaneando.
4. IF el navegador no soporta la Web Share API, THE Juego SHALL mostrar únicamente las opciones de descarga y QR sin mostrar errores.
5. THE Tarjeta de Resultado SHALL generarse completamente en el cliente usando Canvas API y una librería QR embebida (o algoritmo QR puro en JS), sin llamadas a servidores externos.
6. THE Juego SHALL mostrar un preview de la Tarjeta de Resultado dentro de un Modal Retro antes de que el jugador elija cómo compartirla.

---

### Requisito 12: Salir durante la Partida

**User Story:** Como jugador, quiero tener la opción de salir de la partida en curso, para poder regresar al Menú Principal cuando lo desee, sabiendo que perderé el puntaje actual.

#### Criterios de Aceptación

1. WHILE una partida está en curso, THE Juego SHALL mostrar un Botón Salir visible en la pantalla del Tablero.
2. WHEN el jugador hace clic en el Botón Salir, THE Juego SHALL pausar el Banco de Tiempo y mostrar el Modal de Confirmación de Salida sin cerrar la partida.
3. THE Modal de Confirmación de Salida SHALL mostrar el mensaje de advertencia: "Si sales ahora, no podrás guardar tu marcador actual." seguido de la pregunta "¿Estás seguro?".
4. THE Modal de Confirmación de Salida SHALL presentar dos opciones: un botón "CONTINUAR" para reanudar la partida y un botón "SALIR" para abandonarla.
5. WHEN el jugador hace clic en "CONTINUAR" dentro del Modal de Confirmación de Salida, THE Juego SHALL cerrar el modal y reanudar el Banco de Tiempo desde el valor en que fue pausado.
6. WHEN el jugador hace clic en "SALIR" dentro del Modal de Confirmación de Salida, THE Juego SHALL detener el Banco de Tiempo, descartar el puntaje actual y mostrar el Menú Principal.
7. IF el jugador cierra el Modal de Confirmación de Salida sin seleccionar ninguna opción (por ejemplo, presionando Escape), THEN THE Juego SHALL tratar la acción como "CONTINUAR" y reanudar el Banco de Tiempo.
8. THE Modal de Confirmación de Salida SHALL construirse en el DOM con estética 8-bit y NO SHALL usar `prompt()`, `alert()` ni `confirm()` nativos del navegador.

---

### Requisito 13: Background Animado de la Pantalla de Victoria

**User Story:** Como jugador, quiero que la pantalla de victoria tenga un fondo animado y dinámico con estética arcade retro, para que la celebración visual sea coherente con el resto del juego y refuerce la sensación de logro.

#### Criterios de Aceptación

1. WHEN la Pantalla de Victoria se muestra (`data.victory === true`), THE Background de Victoria SHALL reemplazar el fondo negro liso con un fondo animado compuesto por al menos dos capas: un gradiente radial neón y un grid de puntos animado, usando colores de la Paleta Neón.

2. WHEN la Pantalla de Victoria se muestra, THE Background de Victoria SHALL generar Partículas de Victoria que floten o caigan sobre el fondo, usando al menos dos tipos distintos de formas (por ejemplo: estrellas, símbolos `★`, `✦`, `+`, destellos) en colores de la Paleta Neón.

3. THE Background de Victoria SHALL incluir un borde neón pulsante alrededor de la pantalla, usando un color distinto al borde de la pantalla de juego (`#screen-game`), para diferenciar visualmente el estado de victoria.

4. WHILE la Pantalla de Victoria está activa, THE Background de Victoria SHALL mantener todas las animaciones en ejecución continua sin pausas ni parpadeos abruptos.

5. WHEN la Pantalla de Victoria se oculta (el jugador navega a otra pantalla), THE Background de Victoria SHALL detener y limpiar todas las Partículas de Victoria del DOM para evitar acumulación de elementos.

6. THE Background de Victoria SHALL ser implementado exclusivamente con CSS (animaciones, gradientes, `@keyframes`) y JavaScript puro (Vanilla JS) para la generación de partículas, sin librerías externas adicionales.

7. THE Background de Victoria SHALL mantener legible todo el contenido de la Pantalla de Victoria (título "¡VICTORIA!", puntaje, ranking, aciertos, tiempo, botones y créditos), asegurando que las animaciones del fondo no interfieran visualmente con el texto ni los controles (z-index correcto, opacidad de partículas ≤ 0.9).

8. IF el dispositivo tiene `prefers-reduced-motion: reduce`, THEN THE Background de Victoria SHALL mostrar únicamente el gradiente estático y el borde neón, sin Partículas de Victoria ni animaciones de movimiento.

9. THE Background de Victoria SHALL funcionar correctamente en resoluciones de escritorio (mínimo 1024px de ancho) y en dispositivos móviles (mínimo 320px de ancho), sin causar desbordamiento horizontal ni scroll adicional en la Pantalla de Victoria.

10. WHEN la Pantalla de Victoria se muestra, THE Background de Victoria SHALL aplicar un efecto de scanlines (líneas horizontales semitransparentes) consistente con el efecto global del `body::after`, para mantener la coherencia visual con el resto del Juego.
