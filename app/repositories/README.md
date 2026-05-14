# Modulo `app/repositories`

Implementa la capa de acceso a datos para reducir acoplamiento entre API/servicios y SQLAlchemy.

## Archivos

- `mission_repo.py`: operaciones de creacion, cierre y listado de misiones.
- `telemetry_repo.py`: guardado y consulta de telemetria.

## Objetivo tecnico

- centralizar consultas frecuentes,
- mantener semantica de dominio,
- facilitar pruebas unitarias,
- evitar SQL disperso en rutas.

## Operaciones actuales

### `mission_repo`

- `create_mission(name: str) -> int`
- `end_mission(mission_id: int) -> bool`
- `list_missions() -> list[Mission]`

### `telemetry_repo`

- `save_telemetry(mission_id, data: dict) -> int`
- `latest(limit=10) -> list[Telemetry]`

## Convenciones

- Usar `db.session.commit()` por unidad de operacion simple.
- Retornar objetos o ids claros para consumo en API.
- En futuras mejoras, evaluar manejo de rollback explicito para errores de escritura.

## Siguientes extensiones recomendadas

- consultas por rango de fechas,
- telemetria por `mission_id`,
- repositorio de `WaterSample` y `EventLog`,
- paginacion para endpoints historicos.
