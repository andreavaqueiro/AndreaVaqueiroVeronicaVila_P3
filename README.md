# Eco-Dimming MVP - Iluminación Urbana Inteligente

## 📋 Descripción

MVP completo de un sistema de iluminación urbana adaptativa basado en FIWARE NGSI-LD, con capacidades de:
- Gestión de contexto urbano en tiempo real (Orion Context Broker)
- Persistencia de históricos (QuantumLeap + CrateDB)
- Lógica simple de recomendación de intensidad lumínica
- Detección básica de anomalías
- Dashboard interactivo con mapa y gráficas

**Scope:** 1 cuadro eléctrico, 2 grupos, 8 farolas, 2 puntos de flujo peatonal.

## 🚀 Quick Start

### 1. Requisitos previos

- Docker y Docker Compose instalados
- Python 3.10+ (para scripts de simulación)
- Navegador web moderno

### 2. Iniciar infraestructura FIWARE

```bash
# Desde la carpeta del proyecto
chmod +x setup.sh
./setup.sh
```

Esto levantará todos los servicios (Orion, QuantumLeap, MQTT, CrateDB, Backend, Frontend).

Espera a que se muestren los endpoints disponibles.

### 3. Provisionar entidades (topología base)

Abre una nueva terminal en la carpeta del proyecto:

```bash
python -m venv venv  # Si no lo has hecho
source venv/bin/activate  # En Linux/macOS
pip install -r requirements.txt
python provision_entities.py
```

Esto crea:
- 1 StreetlightControlCabinet
- 2 StreetlightGroup
- 8 Streetlight
- 2 CrowdFlowObserved
- 2 Device

### 4. Simular datos históricos

En la misma terminal:

```bash
python simulate_history.py
```

Esto genera 20 iteraciones de simulación:
- Incrementa consumo energético
- Itera 5: Pico peatonal (45 personas) → farolas a 100%
- Itera 10: Baja densidad (2 personas) → farolas a modo ahorro (20%)

### 5. Abrir dashboard

Abre en el navegador: **http://localhost**

Verás:
- 🗺️ Mapa con farolas (coloreadas por intensidad)
- 📊 Métricas de estado actual
- 💡 Recomendación de intensidad
- ⚡ Gráficos de consumo energético
- 👥 Gráficos de flujo peatonal
- ⚠️ Anomalías detectadas

## 📁 Estructura del Proyecto

```
eco-dimming/
├── backend.py                    # API FastAPI
├── index.html                    # Frontend (Leaflet + Chart.js)
├── provision_entities.py         # Provisionar topología NGSI-LD
├── simulate_history.py           # Simulador de datos
├── docker-compose.yml            # Orquestación de servicios
├── Dockerfile.backend            # Imagen del backend
├── mosquitto.conf                # Configuración MQTT
├── nginx.conf                    # Configuración servidor web
├── requirements.txt              # Dependencias Python
├── setup.sh                      # Script de inicialización
└── README.md                     # Este archivo
```

## 🔧 Endpoints de la API

- `GET /health` - Health check
- `GET /api/streetlights` - Estado de farolas
- `GET /api/streetlight-groups` - Estado de grupos
- `GET /api/cabinet` - Estado del cuadro eléctrico
- `GET /api/crowd-flows` - Flujos peatonales actuales
- `GET /api/historical/energy?hours=6` - Histórico de consumo
- `GET /api/historical/crowd?hours=6` - Histórico de peatones
- `GET /api/recommendation` - Recomendación de intensidad
- `GET /api/anomalies` - Anomalías detectadas

## 🎯 Funcionalidades Implementadas

✅ **Visualización en mapa**
- Mapa interactivo de A Coruña con Leaflet
- Marcadores de farolas coloreados por intensidad
- Popups con información por farola

✅ **Consulta de estado**
- Estado actual de todas las entidades
- Relaciones entre farolas, grupos y cuadros

✅ **Histórico temporal**
- Series de consumo energético
- Series de flujo peatonal
- Gráficos con Chart.js

✅ **Lógica de recomendación**
- Basada en densidad peatonal actual
- Regla simple: alta densidad → 100%, baja → 20%

✅ **Detección de anomalías**
- Farola con intensidad alta sin demanda
- Consumo fuera de patrón

## 🔌 Servicios FIWARE (docker-compose)

| Servicio | Puerto | URL |
|----------|--------|-----|
| Orion Context Broker | 1026 | http://localhost:1026 |
| QuantumLeap | 8668 | http://localhost:8668 |
| IoT Agent | 4041 | http://localhost:4041 |
| MQTT Broker | 1883 | mqtt://localhost:1883 |
| CrateDB | 4200 | http://localhost:4200 |
| Frontend | 80 | http://localhost |
| Backend API | 8080 | http://localhost:8080 |

## 🛑 Parar servicios

```bash
docker-compose down
```

Para eliminar también los datos persistentes:

```bash
docker-compose down -v
```

## 📊 Simular nuevos escenarios

Puedes modificar `simulate_history.py` para:
- Cambiar número de iteraciones: `SIM_ITERATIONS`
- Cambiar intervalo: `SIM_SLEEP_SECONDS`

```bash
export SIM_ITERATIONS=50
export SIM_SLEEP_SECONDS=2
python simulate_history.py
```

## 📚 Documentación Relacionada

- [PRD.md](PRD.md) - Product Requirements Document
- [architecture.md](architecture.md) - Arquitectura del sistema
- [data_model.md](data_model.md) - Modelos de datos NGSI-LD
- [simulation_instructions.md](simulation_instructions.md) - Instrucciones de simulación

## 🎓 Propósito Académico

Este MVP forma parte de la práctica "Gestión de Datos en Entornos Inteligentes" de la Universidad de A Coruña, demostrando arquitectura FIWARE, NGSI-LD y Smart Data Models en contexto de smart cities.

## ⚠️ Limitaciones del MVP

- Sin integración con hardware real
- Simulación de datos (no sensores físicos)
- Lógica de reglas simplificada
- Sin autenticación ni autorización
- Sin observabilidad avanzada (logs, trazas)

## 🚀 Mejoras Futuras

- Integración con sensores reales
- ML para predicción de demanda
- Motor de reglas complejo
- Sistema de alertas operativas
- Mantenimiento predictivo
- Escalado a múltiples zonas
- Despliegue en cloud nativo

## 📝 Licencia

Proyecto académico - Universidad de A Coruña, 2026

---

**Creado:** Abril 2026  
**Basado en:** FIWARE NGSI-LD, Smart Data Models Oficiales
