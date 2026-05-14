# Carpeta `static`

Contiene los recursos frontend del dashboard UAV.

## Estructura

- `css/`: estilos visuales del panel.
- `js/`: logica cliente para sockets, mapa, video y controles.

## Objetivo

Separar presentacion y comportamiento del backend, manteniendo una UI operativa para monitoreo tecnico en tiempo real.

## Carga de recursos

El template principal `templates/index.html` referencia:

- `static/css/dashboard.css`
- `static/js/dashboard.js`

Archivos historicos (`styles.css`, `main.js`) se conservan para referencia del prototipo inicial, pero el flujo activo usa `dashboard.*`.
