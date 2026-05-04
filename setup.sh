#!/bin/bash
# Setup and run Eco-Dimming MVP

set -e

echo "=== Eco-Dimming MVP Setup ==="
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor, instala Docker."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado. Por favor, instala Docker Compose."
    exit 1
fi

echo "✓ Docker y Docker Compose detectados"
echo ""

# Clean up existing containers (optional)
echo "Inicializando servicios..."
docker-compose down -v 2>/dev/null || true
echo ""

# Start services
echo "Levantando servicios FIWARE..."
docker-compose up -d

echo ""
echo "Esperando a que los servicios se estabilicen (30 segundos)..."
sleep 30

echo ""
echo "=== MVP listo ==="
echo ""
echo "Servicios activos:"
echo "  🔗 Orion Context Broker:  http://localhost:1026"
echo "  🔌 IoT Agent:             http://localhost:4041"
echo "  📡 MQTT Broker:           localhost:1883"
echo "  ⚙️  Backend API:           http://localhost:8080"
echo "  🎨 Frontend (nginx):       http://localhost"
echo ""
echo "Paso siguiente:"
echo "  1. python3 simulator.py init       (provisionar topología)"
echo "  2. python3 simulator.py run        (simular cambios en tiempo real)"
echo "  3. Abrir http://localhost en navegador"
echo ""
