Quiero que actúes como un arquitecto de software senior, ingeniero backend/frontend, especialista en sistemas UAV, seguridad de aplicaciones web y refactorización de proyectos Python/Flask.

Voy a darte un proyecto llamado UAV-DataStack. Necesito que lo refactorices, fortalezcas y completes de forma profesional, manteniendo la idea original del sistema pero llevándolo a un estado mucho más sólido, seguro, mantenible y presentable.

IMPORTANTE:
- No quiero una respuesta superficial ni solo recomendaciones.
- Quiero cambios reales sobre el código.
- Quiero que inspecciones primero toda la estructura del proyecto antes de modificar.
- Quiero que hagas una refactorización integral, pero sin romper innecesariamente la funcionalidad existente.
- Si alguna parte actual está incompleta o desacoplada, intégrala correctamente.
- Si detectas errores de arquitectura, seguridad, persistencia, UX o acoplamiento, corrígelos.
- Trabaja con criterio de producción, aunque el proyecto siga siendo un prototipo académico/técnico.
- No inventes el stack: parte del stack existente y mejora sobre él.

========================
1. CONTEXTO DEL PROYECTO
========================

El proyecto actual es una plataforma web para monitoreo de un UAV que combina:
- Backend en Python con Flask
- Comunicación en tiempo real con Flask-SocketIO
- Integración con DroneKit / pymavlink / MAVLink
- Visualización geográfica en frontend con Leaflet + OpenStreetMap
- Gráficas en frontend con Chart.js
- Captura de video con OpenCV
- Base de datos local SQLite
- Un script separado para control del dron por consola

La idea general del sistema es:
- conectarse a un dron real o simulador,
- recibir telemetría en tiempo real,
- mostrar posición, trayectoria, altitud, modo de vuelo y variables eléctricas,
- exponer video,
- registrar misiones,
- guardar telemetría histórica,
- y guardar muestras de calidad de agua.

========================
2. ESTADO ACTUAL DETECTADO
========================

Basándote en el repositorio, parte de estos problemas ya existen y deben corregirse:

1) La base de datos está diseñada, pero no está integrada al flujo principal del backend.
2) El frontend muestra botones de control, pero hoy son solo visuales o hacen console.log, no ejecutan control real.
3) El backend expone video, pero el frontend no lo integra correctamente en la UI.
4) Hay desacoplamiento entre el script de control del dron y la app web.
5) Hay uso de variables globales y un diseño poco modular.
6) La configuración está hardcodeada.
7) Hay posibles inconsistencias de puertos/strings de conexión del UAV entre archivos.
8) Hay CSS/estructura visual mejorable y parte del estilo puede estar inline o mal organizado.
9) No hay una API formal suficientemente clara para historial, estado, misiones, muestras y control.
10) La seguridad del sistema es básica o insuficiente.
11) La persistencia de telemetría, eventos y misiones necesita consolidarse.
12) El sistema mezcla simulación y operación real de forma poco desacoplada.

========================
3. OBJETIVO GENERAL
========================

Quiero que conviertas este proyecto en una plataforma mucho más profesional de monitoreo UAV, con estas características:

- Backend modular y mantenible
- Persistencia real e integrada
- API clara
- WebSockets bien estructurados
- Frontend tipo dashboard moderno
- Controles funcionales y seguros
- Video integrado
- Buen manejo de errores
- Configuración por entorno
- Logs y observabilidad
- Seguridad razonable
- Mejor experiencia de usuario
- Base lista para crecimiento futuro

========================
4. STACK A MANTENER / MEJORAR
========================

Mantén y mejora, si es viable, el stack actual:
- Python
- Flask
- Flask-SocketIO
- DroneKit
- pymavlink / MAVLink
- OpenCV
- SQLite
- HTML / CSS / JS
- Leaflet
- OpenStreetMap
- Chart.js

Puedes reorganizar, modularizar y añadir librerías complementarias útiles SIEMPRE que tengan sentido. No cambies el stack por otro completamente distinto sin justificación fuerte.

========================
5. LO QUE QUIERO QUE HAGAS
========================

Haz una intervención integral del proyecto con enfoque profesional. Quiero que hagas, como mínimo, lo siguiente:

-----------------------------------
A. REESTRUCTURACIÓN DE ARQUITECTURA
-----------------------------------

1) Reorganiza el proyecto en módulos claros, por ejemplo:
- app / factory
- config
- services
- routes / api
- sockets
- database / models / repositories
- telemetry providers
- video service
- mission service
- control service
- utils
- static / templates

2) Implementa patrón application factory si mejora el orden.
3) Elimina acoplamientos innecesarios y reduce variables globales.
4) Separa claramente:
- adquisición de telemetría,
- persistencia,
- emisión al frontend,
- control del UAV,
- video,
- simulación.

-----------------------------------
B. CONFIGURACIÓN Y ENTORNOS
-----------------------------------

1) Mueve toda configuración hardcodeada a variables de entorno o archivo de configuración:
- host
- port
- secret key
- database path
- UAV connection string
- video source
- modo debug
- intervalos de refresco
- CORS permitidos

2) Implementa config por entorno:
- development
- testing
- production

3) Agrega un archivo .env.example bien documentado.

-----------------------------------
C. PERSISTENCIA REAL DE DATOS
-----------------------------------

1) Integra la base de datos al flujo principal.
2) Asegura que al iniciar una misión:
- se cree registro de misión,
- se guarde hora de inicio,
- se marque estado,
- se cierre correctamente al terminar.

3) Guarda telemetría periódicamente con campos robustos, al menos:
- mission_id
- timestamp completo
- lat
- lon
- alt
- modo
- voltaje
- corriente
- velocidad si está disponible
- heading si está disponible
- estado de conexión
- fuente (real/simulado)

4) Mantén y mejora la tabla de muestras de agua:
- ph
- turbidez
- oxigeno_disuelto
- conductividad
- timestamp
- ubicación
- observaciones si procede

5) Mejora el esquema SQL y consistencia:
- claves foráneas
- índices útiles
- tipos coherentes
- manejo de errores de escritura
- timestamps completos

6) Si es posible, crea una capa repository/service para no mezclar SQL crudo por todas partes.

-----------------------------------
D. TELEMETRÍA Y OPERACIÓN UAV
-----------------------------------

1) Crea una capa de proveedor de telemetría desacoplada:
- proveedor real
- proveedor simulado

2) Define una interfaz o contrato común para ambos.
3) Mejora la reconexión automática cuando se pierde el UAV.
4) Emite al frontend estados claros:
- connected
- disconnected
- simulated
- reconnecting
- error

5) Unifica las diferencias de puertos o connection strings detectadas entre scripts.
6) Si el script de control por consola existe, intégralo a la lógica principal o conviértelo en servicio reutilizable.
7) Evita acciones peligrosas sin validación del estado del vehículo.

-----------------------------------
E. CONTROL DEL DRON DESDE LA WEB
-----------------------------------

Convierte el dashboard en un centro de control funcional y seguro.

1) Implementa endpoints REST y/o eventos Socket.IO para:
- armar
- desarmar
- cambiar modo de vuelo
- iniciar misión
- detener misión
- aterrizar
- activar simulación si aplica

2) Valida que los cambios de modo sean legales según el estado actual.
3) Devuelve respuestas estructuradas con éxito/error y mensaje claro.
4) Agrega confirmaciones de seguridad en frontend para acciones críticas como:
- arm
- disarm
- land

5) Registra en logs y, si es útil, en DB eventos operativos importantes.

-----------------------------------
F. API FORMAL
-----------------------------------

Diseña una API clara y profesional. Como mínimo:
- GET /api/system/status
- GET /api/telemetry/latest
- GET /api/missions
- GET /api/missions/<id>
- GET /api/missions/<id>/telemetry
- GET /api/missions/<id>/samples
- POST /api/missions/start
- POST /api/missions/stop
- POST /api/uav/arm
- POST /api/uav/disarm
- POST /api/uav/mode
- GET /api/video/status

Requisitos:
- respuestas JSON consistentes
- códigos HTTP correctos
- manejo de errores centralizado
- validación de payloads
- documentación mínima en README o docs

-----------------------------------
G. SEGURIDAD
-----------------------------------

Quiero mejoras de seguridad reales y razonables para este tipo de proyecto.

1) Elimina configuraciones inseguras por defecto.
2) Restringe CORS configurándolo por entorno.
3) Añade validación de entradas en API y eventos socket.
4) Protege acciones críticas con una capa mínima de autenticación simple si es viable para este proyecto.
   Puede ser:
   - token de acceso sencillo
   - auth básica para panel admin
   - sesión protegida
   No compliques demasiado, pero no lo dejes totalmente abierto.

5) Implementa rate limiting en endpoints sensibles si es razonable.
6) Sanitiza entradas.
7) Evita exponer trazas o secretos en producción.
8) Agrega headers de seguridad si procede.
9) Revisa riesgos del stream de video.
10) Asegura que acciones críticas queden auditadas en logs.

-----------------------------------
H. FRONTEND / UX / UI
-----------------------------------

Quiero una mejora fuerte del frontend, pero manteniendo la esencia del proyecto.

Convierte la interfaz en un dashboard profesional con:
- diseño limpio
- cards
- mejor jerarquía visual
- responsive
- estados claros del sistema
- mapa destacado
- panel de video
- panel de control
- panel de métricas
- historial reciente o eventos
- mejor organización visual

Debes mejorar:

1) CSS:
- elimina estilos inline innecesarios
- centraliza estilos
- usa variables CSS
- mejora responsive design
- mejora legibilidad y espaciado

2) Mapa:
- marcador del UAV
- trayectoria
- opción de seguimiento on/off
- mejor comportamiento de auto-centro
- leyenda o panel de coordenadas
- estado de conexión visible

3) Gráficas:
- voltaje
- corriente
- altitud
- otras métricas si están disponibles
- mejor control del historial mostrado

4) Video:
- incrusta correctamente el feed si el backend lo ofrece
- muestra placeholder si la cámara no está disponible
- muestra estado del video

5) Controles:
- que sí funcionen
- que reflejen estado real
- que muestren feedback visual
- que se deshabiliten si la acción no es válida

6) Estados del sistema visibles:
- conectado / desconectado / simulado
- misión activa / inactiva
- cámara activa / inactiva
- base de datos OK / error

7) Experiencia:
- notificaciones toast o alertas elegantes
- mensajes de error claros
- confirmación para acciones críticas
- indicadores de carga

-----------------------------------
I. VIDEO
-----------------------------------

1) Mantén la funcionalidad de OpenCV si ya existe.
2) Integra el stream real al frontend.
3) Maneja errores de cámara sin romper la app.
4) Permite configurar la fuente de video.
5) Separa el servicio de video del resto de la lógica.

-----------------------------------
J. LOGGING Y OBSERVABILIDAD
-----------------------------------

1) Agrega logs estructurados o al menos bien organizados.
2) Diferencia niveles:
- INFO
- WARNING
- ERROR
- DEBUG

3) Registra:
- inicio de sistema
- conexión/desconexión UAV
- inicio/fin de misión
- cambios de modo
- errores de DB
- errores de video
- errores de socket/API

4) Haz que los logs no ensucien la lógica de negocio.

-----------------------------------
K. TESTS Y CALIDAD
-----------------------------------

1) Agrega pruebas al menos para:
- endpoints críticos
- lógica de persistencia
- validación de payloads
- estados del sistema
- partes desacopladas que sean fáciles de testear

2) Mejora nombres de funciones, comentarios y estructura.
3) Añade type hints donde tenga sentido.
4) Limpia código duplicado.
5) Reduce deuda técnica visible.

-----------------------------------
L. DOCUMENTACIÓN Y DESPLIEGUE
-----------------------------------

1) Reescribe el README de forma profesional incluyendo:
- descripción del sistema
- arquitectura
- stack
- instalación
- variables de entorno
- ejecución
- uso con simulación
- uso con dron real si aplica
- endpoints API
- screenshots si puedes generarlas o marcarlas como sugerencia
- problemas comunes

2) Agrega instrucciones claras de ejecución local.
3) Si es viable, agrega:
- requirements limpio
- script de arranque
- Dockerfile
- docker-compose opcional
- .gitignore correcto

========================================
6. REQUISITOS TÉCNICOS IMPORTANTES
========================================

1) No rompas el flujo actual de telemetría si ya funciona.
2) Mantén compatibilidad con modo simulado.
3) Si una función depende de hardware real, agrega fallback o manejo elegante.
4) Si implementas autenticación, que sea ligera y adecuada al proyecto.
5) No conviertas esto en microservicios ni sobreingeniería innecesaria.
6) Prefiero una arquitectura limpia pero razonable.
7) Si haces cambios grandes, deja el proyecto consistente y ejecutable.

========================================
7. ENTREGABLES QUE QUIERO
========================================

Quiero que entregues TODO esto:

1) Código refactorizado e integrado.
2) Resumen técnico de los cambios realizados.
3) Explicación clara de la nueva arquitectura.
4) Lista de problemas detectados y cómo fueron corregidos.
5) Lista de mejoras pendientes opcionales, si quedan.
6) README actualizado.
7) Variables de entorno ejemplo.
8) Instrucciones de ejecución.
9) Si puedes, un pequeño plan de evolución futura.

========================================
8. FORMA DE TRABAJO QUE QUIERO DE TI
========================================

Sigue este orden:

FASE 1:
- Inspecciona todo el repositorio
- Resume la arquitectura actual
- Enumera problemas concretos detectados
- Propón arquitectura objetivo

FASE 2:
- Refactoriza backend
- Integra base de datos
- Implementa API y sockets mejorados
- Integra control UAV
- Mejora seguridad

FASE 3:
- Refactoriza frontend
- Integra video
- Mejora UX/UI
- Conecta controles reales

FASE 4:
- Agrega pruebas, documentación y configuración

FASE 5:
- Entrega resumen final detallado

========================================
9. CRITERIOS DE ACEPTACIÓN
========================================

Consideraré el trabajo correcto solo si al final se cumple lo siguiente:

- El sistema arranca sin errores evidentes.
- Hay una estructura de proyecto más limpia y profesional.
- La DB ya está integrada realmente.
- Las misiones se registran.
- La telemetría se guarda.
- La UI muestra telemetría en vivo.
- El mapa y las gráficas funcionan.
- El video se integra o falla elegantemente.
- Los botones de control ya no son solo visuales.
- Hay validaciones y manejo de errores.
- La configuración ya no está hardcodeada en todos lados.
- La seguridad mejoró.
- Existe documentación clara.
- El sistema sigue soportando simulación.
- El resultado final se siente como una versión madura del prototipo original.

========================================
10. RESTRICCIÓN FINAL
========================================

No me des solo sugerencias. Quiero implementación real, cambios de código, estructura mejorada y explicación profesional de lo que hiciste.

Si detectas que algo no puede completarse totalmente por falta de hardware o contexto del dron, entonces:
- deja el sistema preparado,
- documenta la limitación,
- implementa fallback o modo simulado,
- y no dejes partes rotas.

Empieza inspeccionando el repositorio y trabaja de forma metódica, con criterio de ingeniería senior.