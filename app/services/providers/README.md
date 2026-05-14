# Modulo `app/services/providers`

Define proveedores de telemetria desacoplados del resto del sistema.

## Objetivo

Permitir cambiar fuente de datos sin tocar API, frontend ni persistencia.

## Archivos

- `base.py`: contrato base `TelemetryProvider`.
- `simulated_provider.py`: proveedor sintetico para pruebas sin hardware.
- `dronekit_provider.py`: proveedor real via DroneKit/MAVLink.

## Contrato comun esperado

Cada provider debe implementar:

- `register_callback(cb)`
- `start()`
- `stop()`
- propiedad `status`

El callback recibe un `dict` de telemetria con campos homologados:

- `timestamp`
- `lat`, `lon`, `alt`
- `mode`
- `voltage`, `current`
- `speed`, `heading`
- `connection_state`
- `source`

## `SimulatedProvider`

Util para:

- desarrollo frontend,
- pruebas de persistencia,
- demo sin SITL ni dron real.

Comportamiento:

- random walk geoespacial,
- variacion de heading y velocidad,
- degradacion gradual de voltaje,
- frecuencia configurable por `interval`.

## `DroneKitProvider`

Util para:

- conexion a SITL,
- conexion a avionica real con endpoint MAVLink.

Incluye:

- reconexion automatica con backoff exponencial,
- extraccion robusta de campos de `vehicle`,
- compatibilidad con Python 3.13 para DroneKit (`collections` + `inspect`).

## Reglas para nuevos providers

- nunca bloquear indefinidamente en callback,
- encapsular reconexion en provider, no en API,
- mantener payload compatible con el contrato existente,
- reportar errores con logging pero sin romper el hilo principal.
