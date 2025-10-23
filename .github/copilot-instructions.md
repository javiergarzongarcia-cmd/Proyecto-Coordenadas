<!-- Copilot instructions para agentes de codificación -->
# Instrucciones rápidas para agentes de IA

Propósito corto: este repositorio contiene una aplicación de planificación de rutas llamada AGFOREST con un backend en Python (FastAPI + SQLAlchemy) y un frontend en React (Vite). El objetivo de estas instrucciones es permitir que un agente de IA sea productivo rápidamente: dónde mirar, cómo ejecutar la app localmente, patrones y convenciones de diseño observables en el código.

Principales ubicaciones
- Backend: `AGFOREST/backend/`
  - Modelos ORM: `AGFOREST/backend/models.py` — tablas `routes` y `waypoints`.
  - Esquemas/serialización Pydantic: `AGFOREST/backend/maps.py` (RouteCreate/RouteRead/WaypointCreate/WaypointRead).
  - Entradas principales de la API: `AGFOREST/backend/main.py` (endpoints `/routes/`, `/routes/{id}`).
  - Configuración DB y sesión: `AGFOREST/backend/database.py` (lee `DATABASE_URL`, soporta sqlite y postgres).

- Frontend: `AGFOREST/frontend/`
  - Punto de entrada: `AGFOREST/frontend/src/main.jsx` (usa Vite + React).
  - Llamadas a la API: `AGFOREST/frontend/src/api.js` (usa `VITE_API_BASE` o `http://localhost:8000`).
  - Componentes UI: `AGFOREST/frontend/components/` (por ejemplo `RouteList.jsx`, `RouteForm.jsx`, `RouteDetail.jsx`, `WaypointRow.jsx`).

Arquitectura y flujo de datos (big picture)
- El frontend construye JSON con una ruta y su lista de waypoints y la POSTea a `/routes/` (ver `api.js:createRoute`).
- El backend usa Pydantic (`maps.py`) para validar payloads y SQLAlchemy (`models.py`) para persistir `Route` y `Waypoint`.
- `order_index` es la propiedad usada para ordenar waypoints (observable en `models.py`, `maps.py` y `main.py`). Mantener esta convención cuando manipules listas de waypoints.
- Distancia de una ruta se calcula en `main.py` usando la fórmula de Haversine sobre los waypoints; la distancia se intenta persistir en el `Route` si el campo está definido.

Comandos y workflows de desarrollo
- Backend (virtualenv / Pipfile): instalar dependencias listadas en `AGFOREST/backend/requirements.txt`.
  - Correr servidor de desarrollo: usar `uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000` desde la raíz `AGFOREST/` o con `python -m uvicorn backend.main:app --reload`.
  - La app espera una variable `DATABASE_URL` (por defecto usa sqlite `sqlite:///./test.db`). `AGFOREST/backend/database.py` normaliza `postgres://` a `postgresql://`.

- Frontend:
  - Desde `AGFOREST/` ejecutar `npm install` (o `pnpm`/`yarn` según preferencia) y `npm run dev` (usa `vite`).
  - Variable de entorno: `VITE_API_BASE` configura la base del API (por defecto `http://localhost:8000`). Nota: `api.js` espera rutas en `/api/routes/` en algunas cadenas; revisar templates y corregir si es necesario (`createRoute` actualmente concatena `" api/routes/"` — ver sección de problemas).

Integraciones y puntos de atención
- DB: `DATABASE_URL` puede ser sqlite o postgres. Cuando uses postgres asegúrate que la URL comience por `postgresql://` o que `database.py` la normalice.
- Orden de waypoints: siempre usar `order_index` (integer >= 0). Al insertar, el backend ordena los waypoints por `order` en el payload — sin embargo hay inconsistencias en `main.py` donde se referencian `order` y `order_index`. Mantener `order_index` en los payloads y corregir backend si se modifica.
- API base path: `AGFOREST/frontend/src/api.js` construye URLs con `API_BASE` + rutas; algunos endpoints en código tienen espacios o falta de `/` (ej. `${API_BASE} api/routes/`). Los cambios de rutas o base path deben ser coherentes entre frontend y backend.

Patrones y convenciones detectadas
- Uso de Pydantic con `orm_mode = True` para serializar modelos SQLAlchemy (`maps.py`).
- Precaución: `AGFOREST/backend/main.py` contiene duplicados y código muerta (respuestas construidas después de return, `routes = db.query(...).order_by(models.Route.created_at.desc().all())` es erróneo). Un agente debe preferir editar y simplificar funciones de endpoint respetando los schemas en `maps.py`.
- Cuando crees/actualices rutas, el backend hace `db.flush()` para obtener un id antes de crear waypoints. Preservar ese comportamiento si reescribes la lógica de creación para evitar inconsistencias de FK.

Ejemplos concretos (copiar/ajustar)
- Crear ruta (payload esperado por `maps.RouteCreate`):

  {
    "name": "Mi ruta",
    "waypoints": [
      {"latitude": 12.34, "longitude": -45.67, "order_index": 0},
      {"latitude": 12.35, "longitude": -45.68, "order_index": 1}
    ]
  }

- Llamada fetch equivalente en frontend (usar `api.js`): createRoute(data) realiza POST a `${API_BASE}/api/routes/` — verifica que `API_BASE` incluya la `/` final o ajusta la concatenación.

Errores y correcciones observadas (acciones recomendadas)
- `AGFOREST/backend/main.py` contiene múltiples bugs/duplicaciones:
  - Referencias a `order` vs `order_index` al ordenar waypoints.
  - Código después de `return` y objetos `response` duplicados.
  - Uso incorrecto de `.order_by(models.Route.created_at.desc().all())`.
  - `api.js` usa rutas con espacios en la concatenación. 
  Recomendación: cuando hagas cambios, ejecuta manualmente el servidor (uvicorn) y usa `curl`/Postman/`frontend` dev para validar endpoints.

Checklist para PRs de agentes
 - Añadir/actualizar tests unitarios o de integración si tocas lógica de negocio (ruta/waypoints/distance). Si el proyecto no tiene tests, documenta el manual test (payload + endpoint + expected response).
 - Mantener compatibilidad con `maps.py` (schemas Pydantic) y `models.py` (nombres de columnas y relaciones).
 - Actualizar `AGFOREST/frontend/src/api.js` si cambias los paths del backend y probar desde `npm run dev`.

Si necesitas más contexto
- Empieza por ejecutar el backend local y la UI: mira `AGFOREST/backend/` y `AGFOREST/frontend/`.
- Para preguntas específicas, pide que un mantenedor indique la intención sobre: 1) la ruta base `/api/` vs `/` y 2) el campo canonico para orden (`order` o `order_index`).

Fin de instrucciones.
