# Modulo `app/services`

Contiene la capa de negocio y runtime del backend.

## Servicios disponibles

- `telemetry_service.py`: orquesta recepcion de telemetria, persistencia y emision Socket.IO.
- `control_service.py`: encapsula comandos de arm/disarm/mode/mission_start y auditoria de eventos.
- `video_service.py`: administra captura OpenCV en segundo plano y entrega frames JPEG.
- `providers/`: fuentes de telemetria desacopladas (simulada/DroneKit).

## Principio de diseno

La API nunca deberia hablar directamente con hardware ni con SQL crudo.

El flujo correcto es:

API -> Service -> Repository/Provider -> DB/Hardware

## `TelemetryService`

Responsabilidades:

- registrar callback en provider,
- normalizar timestamps,
- persistir payload via `telemetry_repo`,
- emitir `telemetry.update` al namespace `/telemetry`.

Detalle tecnico:

- Usa `app.app_context()` cuando se ejecuta desde hilos de background.
- Convierte objetos no serializables a formato JSON seguro con `_json_safe`.

## `ControlService`

Responsabilidades:

- validar disponibilidad de `vehicle`,
- ejecutar comandos seguros sobre provider real,
- soportar fallback simulado,
- registrar auditoria en tabla `event_logs`.

Comandos actuales:

- `arm()`
- `disarm()`
- `set_mode(mode)`
- `mission_start()`

## `VideoService`

Responsabilidades:

- abrir fuente de video configurable,
- leer frames continuamente en hilo daemon,
- reintentar apertura ante fallos,
- exponer `get_frame()` y `status()`.

Robustez implementada:

- manejo de backends de captura en Windows (`CAP_DSHOW`, `CAP_MSMF`),
- reapertura automatica tras multiples fallos consecutivos,
- reportes de estado (`available`, `opened`, `last_frame_ts`).

## Criterios para nuevos servicios

- sin dependencia de `request` Flask dentro del servicio,
- con logging propio por modulo,
- entradas/salidas simples y serializables,
- pruebas unitarias enfocadas en logica y contratos.
