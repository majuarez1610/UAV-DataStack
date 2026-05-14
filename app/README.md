# Modulo `app`

Este modulo contiene el nucleo backend de UAV-DataStack.

## Objetivo

Encapsular toda la logica de servidor Flask en una arquitectura modular, separando:

- configuracion,
- inicializacion de extensiones,
- rutas HTTP,
- sockets,
- servicios de dominio,
- persistencia.

## Componentes principales

- `__init__.py`: Application Factory (`create_app`) y registro central.
- `config.py`: clases de configuracion por entorno.
- `extensions.py`: instancias globales de extensiones Flask.
- `models.py`: modelos SQLAlchemy.
- `api/`: Blueprints REST.
- `services/`: capa de negocio y runtime.
- `repositories/`: acceso a DB orientado a operaciones.
- `sockets/`: eventos Socket.IO.
- `utils/`: utilidades transversales (auth/validacion).

## Flujo de inicializacion

1. `create_app()` selecciona config por `FLASK_CONFIG`.
2. Inicializa `db`, `cors`, `socketio`.
3. Registra blueprints de API y control.
4. Registra handlers de Socket.IO.
5. Ejecuta `db.create_all()` dentro de app context.
6. Crea singletons de runtime (`VideoService`, `ControlService`).
7. Expone ruta raiz `/` para dashboard.

## Reglas de mantenimiento

- Evitar logica de negocio en rutas HTTP.
- Mantener persistencia en `repositories`.
- Evitar variables globales no encapsuladas.
- Cualquier nueva integracion de hardware debe pasar por `services/providers`.

## Buenas practicas al extender este modulo

- Crear blueprints nuevos por dominio funcional.
- Definir validaciones de payload explicitas.
- Gestionar errores con respuestas JSON consistentes.
- Agregar pruebas en `tests/` por cada endpoint nuevo.
