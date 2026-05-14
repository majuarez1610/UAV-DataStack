# Carpeta `tests`

Pruebas unitarias e integracion ligera del backend.

## Archivos

- `test_api.py`: validaciones de endpoints criticos y autenticacion.
- `test_repositories.py`: pruebas de persistencia en repositorios.

## Estrategia actual

- Se crea app en modo `testing`.
- Se usa base en memoria para aislar escenarios.
- Se valida que rutas protegidas exijan token.
- Se valida insercion y consulta basica de mision/telemetria.

## Ejecucion

```powershell
pytest -q
```

## Cobertura pendiente recomendada

- rutas de control (`/api/uav/*`),
- autenticacion (token expirado/token invalido),
- estado de video y manejo de errores,
- eventos socket de control y telemetria,
- providers (simulado/dronekit) con mocks.
