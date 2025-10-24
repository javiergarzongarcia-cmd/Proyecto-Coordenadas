# Route Planning App

Aplicación de planificación de rutas con FastAPI, React y PostgreSQL.

## Requisitos previos
- Docker y Docker Compose (recomendado)
- Alternativa local: Python 3.10+ y Node 18+

## Estructura
- `/backend`: API FastAPI (Python)
- `/frontend`: React + Vite
- `/database`: Esquema SQL

## Puesta en marcha rápida (Docker)
```bash
# Desde la raíz
docker compose up -d --build
# API: http://localhost:8000/docs
# Frontend: http://localhost:5173
```

## Base de datos
El esquema está en `database/schema.sql`. El backend crea tablas si no existen al iniciar.

## Backend (local sin Docker)
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Ajusta DATABASE_URL si es necesario
python -m app  # Uvicorn en 0.0.0.0:8000
```

## Frontend (local sin Docker)
```bash
cd frontend
npm install
# opcional: echo "VITE_API_URL=http://localhost:8000" > .env
npm run dev
```

## Endpoints
- POST `/api/routes` crea ruta con waypoints y devuelve detalle + distancia total
- GET `/api/routes` lista rutas con `waypoint_count` y `total_distance_km`
- GET `/api/routes/{id}` devuelve detalle completo de la ruta

## Cálculo de distancia
Se utiliza Haversine (preciso). El frontend también calcula en vivo para vista previa.

## Extras
- CORS habilitado para desarrollo
- Dockerfiles para backend y frontend
- `.gitignore` actualizado

## Despliegue
- Puedes publicar el backend en Fly.io/Render y el frontend en Vercel/Netlify
- Configura `VITE_API_URL` en el frontend apuntando a la URL del backend
