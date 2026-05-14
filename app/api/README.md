# Modulo `app/api`

Contiene los blueprints REST de la plataforma.

## Archivos

- `routes.py`: endpoints de estado general, misiones, telemetria y estado de video.
- `auth_routes.py`: registro/login de usuarios y emision de token firmado.
- `control_routes.py`: comandos de control UAV protegidos por token.
- `video_routes.py`: endpoint de stream MJPEG protegido.

## Contrato de respuesta

Los endpoints devuelven JSON con estructura consistente:

- Exito: `{"ok": true, ...}`
- Error: `{"ok": false, "error"|"message": "..."}`

## Seguridad aplicada

- Endpoints de control y mision usan `@require_token`.
- `/video_feed` tambien requiere autenticacion.
- Login usa `SECRET_KEY` para firma de token temporal.

## Endpoints actuales

### Estado y consulta

- `GET /api/system/status`
- `GET /api/telemetry/latest`
- `GET /api/missions`
- `GET /api/video/status`

### Misiones

- `POST /api/missions/start`
- `POST /api/missions/stop`

### Control

- `POST /api/uav/arm`
- `POST /api/uav/disarm`
- `POST /api/uav/mode`
- `POST /api/uav/mission_start`

### Autenticacion

- `POST /api/auth/register`
- `POST /api/auth/login`

### Video

- `GET /video_feed`

## Recomendaciones de evolucion

- Centralizar manejo de errores con blueprint-level handlers.
- Agregar validacion de payload con schema formal (pydantic/marshmallow).
- Implementar rate limiting especifico para rutas criticas de control.
- Exponer historial por mision (`/api/missions/<id>/telemetry`, `/samples`).
