#!/bin/bash
# Script para levantar el MVP con arquitectura FIWARE real (Docker Compose)

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "🚀 Iniciando MVP Eco-Dimming (FIWARE real)"
echo ""

echo "📦 Levantando stack con docker-compose..."
docker-compose up -d --build

echo ""
echo "✅ Servicios levantados:"
echo "   🌐 Frontend:  http://localhost"
echo "   ⚙️  Backend:   http://localhost:8080/health"
echo "   🔗 Orion-LD:   http://localhost:1026/version"
echo ""
echo "📝 Próximos pasos:"
echo "   1. python3 simulator.py init"
echo "   2. python3 simulator.py run   (opcional, para updates en tiempo real)"
echo "   3. Abre http://localhost en tu navegador"
echo ""
echo "Para detener:"
echo "   docker-compose down"
