# Documento de Requisitos de Bugfix

## Introducción

El juego Memorama Arcade Retro presenta cinco bugs confirmados:

1. **Victoria prematura**: el flujo de victoria se dispara al encontrar 4 pares en lugar de los 8 requeridos.
2. **Layout no responsivo**: fuera de pantalla completa, los elementos se desbordan de la vista, especialmente en mobile.
3. **Emojis descentrados en las cartas**: los símbolos emoji del frente de las cartas no están centrados visualmente.
4. **QR ilegible en mobile**: el código QR generado no puede ser escaneado desde un dispositivo móvil, posiblemente por problemas de contraste o tamaño.
5. **Contenido no cabe en pantalla mobile**: en versión mobile los elementos requieren scroll excesivo; todo debe ser visible sin scroll o con scroll mínimo.

---

## Bug Analysis

### Current Behavior (Defect)

1.1 WHEN el jugador encuentra exactamente 4 pares de cartas en el tablero THEN el sistema muestra la pantalla de victoria y detiene el temporizador como si se hubieran encontrado todos los pares

1.2 WHEN `BoardEngine.isComplete()` es evaluado con 4 pares emparejados THEN el sistema retorna `true` de forma incorrecta, disparando el flujo de victoria antes de tiempo

1.3 WHEN el juego se visualiza en un navegador sin estar en modo pantalla completa (ventana de tamaño normal) THEN el sistema muestra los elementos desbordándose fuera del área visible, requiriendo scroll horizontal o quedando elementos cortados

1.4 WHEN el juego se visualiza en un dispositivo móvil (viewport ≤ 768px) THEN el sistema muestra los elementos del tablero y el panel de estadísticas con tamaños que no se adaptan al viewport, causando desbordamiento o scroll excesivo

1.5 WHEN una carta está en estado `flipped` o `matched` mostrando su símbolo emoji en el frente THEN el sistema muestra el emoji desplazado o descentrado respecto al área de la carta, no alineado correctamente en el centro visual

1.6 WHEN el jugador genera el código QR en la pantalla de resultados y lo intenta escanear desde un dispositivo móvil THEN el sistema muestra un QR que no puede ser leído por la cámara del móvil, posiblemente por bajo contraste, tamaño insuficiente o módulos demasiado pequeños

1.7 WHEN el juego se visualiza en un dispositivo móvil (viewport ≤ 768px) THEN el sistema requiere scroll vertical significativo para ver todos los elementos del tablero, panel de estadísticas y controles simultáneamente en la misma pantalla

### Expected Behavior (Correct)

2.1 WHEN el jugador encuentra exactamente 4 pares de cartas en el tablero THEN el sistema SHALL continuar la partida sin mostrar la pantalla de victoria ni detener el temporizador

2.2 WHEN `BoardEngine.isComplete()` es evaluado con 4 pares emparejados THEN el sistema SHALL retornar `false`, ya que aún quedan 4 pares sin encontrar en el tablero

2.3 WHEN el juego se visualiza en un navegador sin estar en modo pantalla completa THEN el sistema SHALL adaptar el layout para que todos los elementos quepan dentro del área visible sin desbordamiento ni scroll horizontal

2.4 WHEN el juego se visualiza en un dispositivo móvil (viewport ≤ 768px) THEN el sistema SHALL escalar y reorganizar los elementos (tablero, panel de estadísticas, controles) para que se ajusten al viewport disponible sin desbordamiento

2.5 WHEN una carta está en estado `flipped` o `matched` mostrando su símbolo emoji THEN el sistema SHALL mostrar el emoji perfectamente centrado horizontal y verticalmente dentro del área de la carta

2.6 WHEN el jugador genera el código QR en la pantalla de resultados THEN el sistema SHALL generar un QR con contraste suficiente (módulos oscuros sobre fondo claro) y tamaño de módulo adecuado para ser escaneado correctamente desde la cámara de un dispositivo móvil

2.7 WHEN el juego se visualiza en un dispositivo móvil (viewport ≤ 768px) THEN el sistema SHALL mostrar todos los elementos esenciales (tablero, estadísticas y controles) dentro de la pantalla visible sin requerir scroll, o con scroll mínimo solo para elementos secundarios

### Unchanged Behavior (Regression Prevention)

3.1 WHEN el jugador encuentra los 8 pares del tablero (todos los pares) THEN el sistema SHALL CONTINUE TO mostrar la pantalla de victoria, detener el temporizador y calcular el puntaje correctamente

3.2 WHEN el temporizador llega a 0 segundos sin que el jugador haya encontrado todos los pares THEN el sistema SHALL CONTINUE TO mostrar la pantalla de Game Over con el puntaje calculado hasta ese momento

3.3 WHEN el jugador encuentra entre 1 y 7 pares (sin completar el tablero) THEN el sistema SHALL CONTINUE TO mantener la partida activa, actualizando aciertos, racha y tiempo restante sin disparar victoria

3.4 WHEN el juego se visualiza en escritorio (viewport ≥ 1024px) en pantalla completa THEN el sistema SHALL CONTINUE TO mostrar el layout horizontal con el panel de estadísticas lateral y el tablero centrado con estética retro neón

3.5 WHEN una carta está en estado `down` (boca abajo) THEN el sistema SHALL CONTINUE TO mostrar el reverso con el logo de Talent Land correctamente centrado y proporcional

3.6 WHEN el jugador descarga la tarjeta de resultado como PNG THEN el sistema SHALL CONTINUE TO generar la imagen Canvas 1080×1920px con todos los elementos (logo, puntaje, ranking, créditos) correctamente posicionados

3.7 WHEN el jugador utiliza la opción de compartir nativo (Web Share API) THEN el sistema SHALL CONTINUE TO invocar `navigator.share()` con la imagen generada si el navegador lo soporta
