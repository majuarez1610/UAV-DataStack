# Modulo `app/utils`

Incluye utilidades transversales usadas por multiples capas.

## Archivos

- `auth.py`: decorador `require_token` y helper de emision de token de usuario.
- `validators.py`: validadores simples reutilizables.

## `auth.py`

### `require_token`

Valida autenticacion en dos modos:

1. Token estatico configurado en `ACCESS_TOKEN`.
2. Token firmado con `SECRET_KEY` usando `itsdangerous`.

Entrada aceptada:

- Header `Authorization: Bearer <token>`.
- Query param `access_token` (util para stream MJPEG).

Respuestas de error:

- `401 Unauthorized` si falta o es invalido.
- `401 Token expired` para token firmado vencido.

### `generate_user_token`

Genera token firmado para consumo de dashboard/API.

## `validators.py`

Actualmente incluye `is_float(x)` para validaciones basicas.

## Recomendaciones

- Migrar validaciones a esquemas por endpoint para mayor consistencia.
- Incluir funciones de sanitizacion para payloads textuales.
- Agregar pruebas unitarias especificas de autenticacion y expiracion.
