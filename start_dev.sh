#!/bin/bash
# Script para levantar el MVP completo en desarrollo local

set -e

echo "🚀 Iniciando MVP Eco-Dimming (Desarrollo Local)"
echo ""

cd /home/andrea/XDEI/AndreaVaqueiro_VeronicaVila_P3
source venv/bin/activate

# Limpiar procesos anteriores
echo "Limpiando procesos anteriores..."
pkill -f mock_orion.py || true
pkill -f web_server.py || true
sleep 1

echo ""
echo "📊 Levantando servicios..."
echo ""

# Terminal 1: Mock Orion en puerto 8000
echo "1️⃣  Mock Orion → puerto 8000"
python3 mock_orion.py > /tmp/mock_orion.log 2>&1 &
MOCK_PID=$!
echo "   PID: $MOCK_PID"

sleep 3

# Terminal 2: Web Server en puerto 3000
echo "2️⃣  Web Server → puerto 3000"
python3 web_server.py > /tmp/web_server.log 2>&1 &
WEB_PID=$!
echo "   PID: $WEB_PID"

sleep 2

echo ""
echo "✅ Servicios levantados:"
echo "   🌐 Dashboard:  http://localhost:3000"
echo "   🔌 API:        http://localhost:8000"
echo ""
echo "📝 Próximos pasos:"
echo "   1. ORION_BASE_URL='http://localhost:8000' python3 provision_entities.py"
echo "   2. ORION_BASE_URL='http://localhost:8000' python3 simulate_history.py"
echo "   3. Abre http://localhost:3000 en tu navegador"
echo ""
echo "Para detener:"
echo "   kill $MOCK_PID $WEB_PID"
echo ""

# Mantener el script corriendo
wait
