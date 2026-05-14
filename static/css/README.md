# Carpeta `static/css`

Define los estilos del dashboard.

## Archivos

- `dashboard.css`: hoja activa para la interfaz actual.
- `styles.css`: estilos legacy del prototipo inicial.

## `dashboard.css`

Incluye:

- variables CSS para paleta base,
- layout responsive de sidebar + mapa,
- estilos de estado (`online`, `waiting`, `active`),
- modal de autenticacion,
- panel de video con placeholder,
- controles de accion con estados `disabled`.

## Convenciones de estilo

- centralizar colores en variables,
- evitar inline styles en templates,
- mantener contrastes altos para operacion en campo/lab,
- no duplicar reglas entre `styles.css` y `dashboard.css`.
