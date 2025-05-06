#!/bin/sh
echo "💡 [ENTRYPOINT] Avvio inizializzazione Django..."

# Colleziona file statici
echo "🧹 Raccolta static files..."
python AdriaProject/manage.py collectstatic --no-input

# Migrazioni database
echo "📦 Eseguo le migrations..."
python AdriaProject/manage.py makemigrations
python AdriaProject/manage.py migrate

# Importazione dataset iniziali (solo se necessario)
echo "🌱 Importazione dataset iniziali (se serve)..."
python AdriaProject/manage.py initdatasets || echo "⚠️ Comando initdatasets fallito o non necessario"

# Messaggio finale
echo "✅ Backend Django avviato su http://localhost:8000"
echo "✅ Frontend Angular disponibile su http://localhost:4200 (se configurato correttamente)"

# Avvia il comando specificato nel Dockerfile o docker-compose
exec "$@"



