# Carpeta `scripts`

Scripts auxiliares y de operacion manual fuera del flujo web principal.

## Archivo incluido

- `drone_control_menu.py`: menu de control por consola para pruebas directas con DroneKit.

## Proposito

Permitir pruebas rapidas de comandos de vuelo desde terminal cuando se requiere depuracion independiente del dashboard.

## Alcance funcional

- lectura basica de estado del vehiculo,
- cambio de modos (`STABILIZE`, `LOITER`, `AUTO`, `LAND`),
- armado/desarmado,
- override temporal de throttle en modo AUTO.

## Advertencias

- Usa conexion fija `tcp:127.0.0.1:5762` (puede requerir ajuste segun SITL).
- Es un flujo manual y no reemplaza la capa de control web.
- No tiene validacion de permisos ni auditoria en DB.

## Recomendacion

Para operacion integrada y trazable, preferir los endpoints de `app/api/control_routes.py` y la capa `ControlService`.
