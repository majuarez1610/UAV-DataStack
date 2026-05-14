# Carpeta `templates`

Incluye las plantillas HTML renderizadas por Flask.

## Archivo principal

- `index.html`: dashboard principal de monitoreo y control UAV.

## Secciones del dashboard

- Estado de conectividad UAV y mision.
- Panel de video con stream MJPEG.
- Tarjetas de metricas operativas.
- Grafica de bateria/corriente.
- Botonera de control UAV.
- Modal de autenticacion.
- Mapa principal de trayectoria.

## Dependencias frontend cargadas desde CDN

- Leaflet
- Socket.IO client
- Chart.js

## Reglas de mantenimiento

- evitar estilos inline,
- mantener IDs estables usados por `static/js/dashboard.js`,
- cuidar accesibilidad basica de inputs y botones,
- no romper estructura de tarjetas y panel de mapa/video.
