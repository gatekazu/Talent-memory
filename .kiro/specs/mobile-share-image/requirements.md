# Requirements Document

## Introduction

El juego Memorama (TALENT MEMORY) ya cuenta con un botón "COMPARTIR" en la pantalla de resultados que permite al jugador descargar o compartir una imagen con su resultado final. Sin embargo, este botón actualmente está oculto en dispositivos móviles mediante CSS (`display: none` para viewports menores a 1024px). Esta feature habilita el mismo botón de compartir/descargar imagen en la versión mobile, aprovechando la infraestructura existente de `ShareEngine` y el modal de compartir que ya funcionan en desktop.

## Glossary

- **ShareEngine**: Módulo JavaScript existente que genera la tarjeta de resultado como canvas 1080×1920px, la descarga como PNG y la comparte vía Web Share API.
- **btn-share**: Botón HTML con id `btn-share` que actualmente solo se muestra en desktop (≥1024px).
- **Pantalla de resultados**: Sección `#screen-results` que se muestra al jugador cuando termina una partida (victoria o derrota).
- **Modal de compartir**: Overlay dinámico gestionado por `ModalManager` que muestra la preview de la tarjeta y los botones de descarga/compartir nativo.
- **Web Share API**: API nativa del navegador que permite compartir archivos directamente desde el dispositivo (disponible en la mayoría de navegadores móviles modernos).
- **GameState**: Objeto que almacena el estado actual de la partida (mote del jugador, puntuación, rango, aciertos, tiempo restante).

## Requirements

### Requirement 1: Visibilidad del botón compartir en mobile

**User Story:** Como jugador en dispositivo móvil, quiero ver el botón "COMPARTIR" en la pantalla de resultados, para poder descargar o compartir mi imagen de resultado igual que en desktop.

#### Acceptance Criteria

1. WHEN la pantalla de resultados es visible en un viewport menor a 1024px, THE btn-share SHALL estar visible y accesible al usuario.
2. THE btn-share SHALL mostrarse en todos los tamaños de viewport, incluyendo dispositivos con ancho menor a 1024px.
3. WHILE la pantalla de resultados está activa en mobile, THE btn-share SHALL ocupar un espacio adecuado dentro del contenedor `.result-buttons` sin desbordarse del layout.

### Requirement 2: Funcionalidad del modal de compartir en mobile

**User Story:** Como jugador en dispositivo móvil, quiero que al pulsar el botón "COMPARTIR" se abra el mismo modal que en desktop, para poder descargar la imagen o compartirla con la Web Share API.

#### Acceptance Criteria

1. WHEN el usuario pulsa btn-share en un dispositivo móvil, THE ShareEngine SHALL generar la tarjeta de resultado con los datos actuales de GameState.
2. WHEN el modal de compartir se abre en mobile, THE ModalManager SHALL mostrar la preview de la tarjeta de resultado escalada al ancho disponible del viewport.
3. WHEN el modal de compartir está abierto en mobile, THE Modal SHALL contener el botón "⬇ DESCARGAR" que descarga la imagen PNG al dispositivo.
4. WHERE el navegador móvil soporta Web Share API con archivos, THE Modal SHALL mostrar adicionalmente el botón "↗ COMPARTIR" para compartir la imagen de forma nativa.
5. IF el navegador móvil no soporta Web Share API con archivos, THEN THE Modal SHALL mostrar únicamente el botón "⬇ DESCARGAR" sin errores.

### Requirement 3: Descarga de imagen en mobile

**User Story:** Como jugador en dispositivo móvil, quiero poder descargar la imagen de mi resultado, para guardarla en mi galería o compartirla manualmente.

#### Acceptance Criteria

1. WHEN el usuario pulsa "⬇ DESCARGAR" en el modal desde un dispositivo móvil, THE ShareEngine SHALL ejecutar `downloadPNG` generando un archivo `memorama-resultado.png`.
2. IF el navegador móvil no soporta la descarga directa mediante elemento `<a>` con atributo `download`, THEN THE ShareEngine SHALL registrar el error en consola y resolver sin lanzar una excepción no controlada.

### Requirement 4: Compartir nativo en mobile

**User Story:** Como jugador en dispositivo móvil, quiero poder compartir mi imagen de resultado directamente desde el juego usando las opciones nativas de mi dispositivo, para enviársela a mis contactos o publicarla en redes sociales.

#### Acceptance Criteria

1. WHEN el usuario pulsa "↗ COMPARTIR" en el modal desde un dispositivo móvil, THE ShareEngine SHALL invocar `shareNative` con el canvas generado.
2. WHILE la operación de compartir nativo está en progreso, THE btn-share-native SHALL estar deshabilitado y mostrar el texto "..." para indicar carga.
3. WHEN la operación de compartir nativo finaliza (con éxito o cancelación), THE btn-share-native SHALL volver a estar habilitado con el texto "↗ COMPARTIR".
4. IF el usuario cancela el diálogo nativo de compartir, THEN THE ShareEngine SHALL resolver sin lanzar una excepción no controlada.

### Requirement 5: Adaptación visual del modal en mobile

**User Story:** Como jugador en dispositivo móvil, quiero que el modal de compartir se adapte correctamente a la pantalla de mi dispositivo, para poder ver la preview y los botones sin necesidad de hacer scroll horizontal.

#### Acceptance Criteria

1. WHEN el modal de compartir se muestra en un viewport menor a 1024px, THE Modal SHALL ajustar el ancho de la preview del canvas para no exceder el ancho del viewport disponible.
2. THE Modal SHALL mostrar los botones de acción ("⬇ DESCARGAR" y "↗ COMPARTIR") en un layout que sea usable con interacción táctil (tamaño mínimo de área táctil de 44×44px).
3. WHILE el modal está abierto en mobile, THE Modal SHALL permitir scroll vertical si el contenido excede la altura del viewport.
