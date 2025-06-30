#!/bin/sh

timestamp() {
  date +"[%Y-%m-%d %H:%M:%S]"
}

echo "$(timestamp) 💡 [ENTRYPOINT] Starting Django initialization..."

# Colleziona file statici
echo "$(timestamp) 🧹 Collecting static files..."
python adria_project_backend/manage.py collectstatic --no-input
echo "$(timestamp) ✅ Static files collected."

# Eseguo makemigrations
echo "$(timestamp) 📦 Running makemigrations..."
python adria_project_backend/manage.py makemigrations
echo "$(timestamp) ✅ Makemigrations complete."

# Eseguo migrate
echo "$(timestamp) 📦 Applying migrations..."
python adria_project_backend/manage.py migrate
echo "$(timestamp) ✅ Migrations applied successfully."

# Importazione dataset iniziali
echo "$(timestamp) 🌱 Attempting initial dataset import (if needed)..."
python adria_project_backend/manage.py initdatasets && \
  echo "$(timestamp) ✅ Dataset import completed." || \
  echo "$(timestamp) ⚠️ Dataset import skipped or failed."

# Messaggio finale
echo "$(timestamp) ✅ Django backend ready on http://localhost:8000"
echo "$(timestamp) ✅ Angular frontend available on http://localhost:4200 (if configured)"

# Avvia il comando finale
exec "$@"




