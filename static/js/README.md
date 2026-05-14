# Carpeta `static/js`

Contiene la logica cliente del dashboard y scripts legacy.

## Archivos

- `dashboard.js`: script activo con sockets, mapa, charts, login y control UAV.
- `main.js`: script legacy del prototipo anterior.

## Responsabilidades de `dashboard.js`

- Conexion Socket.IO namespace `/telemetry`.
- Actualizacion en vivo de:
  - posicion y trayectoria en Leaflet,
  - valores de altitud/modo/voltaje/corriente,
  - grafica historica en Chart.js.
- Gestion de autenticacion:
  - login via `/api/auth/login`,
  - almacenamiento de token en `localStorage`.
- Integracion de video:
  - consulta de `/api/video/status`,
  - carga de `/video_feed?access_token=...`,
  - fallback visual si no hay camara/frames.
- Acciones de control:
  - `arm`, `disarm`, `mode`, `mission_start`.

## Buenas practicas para evoluciones

- evitar logica de negocio extensa en cliente,
- centralizar llamadas HTTP autenticadas,
- mantener feedback visual claro en errores y exito,
- agregar pruebas E2E cuando se incorporen nuevos comandos.
