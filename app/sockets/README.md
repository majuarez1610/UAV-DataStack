# Modulo `app/sockets`

Gestiona la capa de tiempo real con Flask-SocketIO.

## Archivo principal

- `handlers.py`: registro de eventos Socket.IO y control de conexion por namespace.

## Namespaces implementados

- `/telemetry` (publico): clientes de dashboard reciben datos en vivo.
- `/control` (protegido): clientes autorizados envian comandos operativos.

## Eventos definidos

### Namespace `/telemetry`

- `connect`
- `disconnect`

Los datos de telemetria se emiten desde `TelemetryService` con el evento:

- `telemetry.update`

### Namespace `/control`

- `connect(auth)` valida token (`ACCESS_TOKEN`).
- `control.command` recibe accion de control.
- `control.ack` confirma resultado al cliente.

## Modelo de seguridad

- Namespace de control bloquea conexiones no autorizadas.
- Comandos se delegan a `ControlService`.
- Logs de intentos no autorizados quedan registrados.

## Recomendaciones de evolucion

- agregar esquema de validacion para payload de `control.command`,
- incorporar auditoria estructurada por usuario/sesion,
- separar permisos por tipo de comando critico.
