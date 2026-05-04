# 🔥 Eco-Dimming MVP - Iluminación Urbana Inteligente

**Smart City Platform con FIWARE NGSI-LD**

Plataforma de iluminación urbana inteligente para A Coruña, basada en Smart Data Models de FIWARE, con visualización en tiempo real, heatmap de actividad urbana y optimización energética.

---

## 📋 Características Principales

### ✅ Implementado

- **70 farolas FIWARE-compatibles** distribuidas en 6 zonas de A Coruña
- **Dashboard interactivo** con mapa Leaflet.js y visualización de estado
- **Heatmap dinámico** de actividad urbana (peatones/tráfico)
- **Cálculo automático** de consumo energético
- **Modelos FIWARE NGSI-LD** completos:
  - Streetlight, StreetlightGroup, StreetlightControlCabinet
  - StreetlightFeeder, StreetlightModel
  - CrowdFlowObserved, TrafficFlowObserved, ItemFlowObserved
- **Simulador de datos** dinámicos cada 3 segundos
- **Mock Orion Context Broker** en puerto 8000
- **Web Server** en puerto 3000
- **API REST** compatible NGSI-LD
- **Control toggle** para heatmap
- **CORS habilitado** para comunicación cross-origin

### ⏳ Próximamente

- Integración real con Orion Context Broker
- QuantumLeap para series temporales
- WebSockets para actualizaciones en tiempo real
- Autenticación y autorización
- Dashboard de analítica histórica
- API de optimización inteligente

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│  PRESENTACIÓN - Dashboard Web (Leaflet.js + Chart.js)  │
│  http://localhost:3000                                  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│  LÓGICA - Web Server (Flask)                            │
│  GET /  - Sirve dashboard                              │
│  GET /health - Health check                            │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│  DATOS - FIWARE Adapter + Mock Orion (Flask)           │
│  POST/GET /ngsi-ld/v1/entities - NGSI-LD API          │
│  PATCH /ngsi-ld/v1/entities/{id}/attrs - Updates      │
│  GET /v2/entities/{id}/attrs/{attr} - Histórico        │
│  http://localhost:8000                                  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│  GENERACIÓN - FIWARE Entities (Python)                  │
│  - Streetlight (68)                                     │
│  - StreetlightGroup (6)                                │
│  - StreetlightModel (3)                                │
│  - CrowdFlowObserved (2+)                              │
│  - TrafficFlowObserved (1+)                            │
│  - ItemFlowObserved (2+)                               │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 Estructura del Proyecto

```
AndreaVaqueiro_VeronicaVila_P3/
├── 📄 README.md                          ← Este documento
│
├── 🔌 BACKEND - FIWARE & API
│   ├── fiware_data_models.py             ← Clases NGSI-LD
│   ├── generate_fiware_entities.py       ← Generador de entidades
│   ├── fiware_adapter.py                 ← Adaptador para frontend
│   ├── fiware_entities.json              ← Dump de entidades
│   ├── fiware_adapter_example.json       ← Ejemplo adaptador
│   ├── mock_orion.py                     ← Simulador Orion + QuantumLeap
│   ├── web_server.py                     ← Servidor web Flask
│   ├── simulate_streetlights.py          ← Simulador de datos
│   └── provision_entities.py             ← Provisión de entidades
│
├── 🎨 FRONTEND - Dashboard
│   └── index.html                        ← Dashboard interactivo
│
├── 📚 DOCUMENTACIÓN
│   ├── FIWARE_DATA_MODEL.md              ← Modelo de datos FIWARE
│   ├── FIWARE_INTEGRATION.md             ← Guía de integración
│   ├── PRD.md                            ← Requerimientos funcionales
│   ├── data_model.md                     ← Modelo de datos original
│   ├── architecture.md                   ← Arquitectura del sistema
│   └── README.md                         ← Este archivo
│
├── 🔧 CONFIGURACIÓN
│   ├── venv/                             ← Virtual environment Python
│   └── requirements.txt (generado)       ← Dependencias
│
└── 🗄️ DATOS
    └── COORDENADAS 6 ZONAS A CORUÑA
        - Centro Histórico (12 farolas)
        - Ciudad Vieja (12 farolas)
        - Calle Real (11 farolas)
        - Paseo Marítimo (10 farolas)
        - Ensanche (12 farolas)
        - Avenida Juan Flórez (11 farolas)
```

---

## 🚀 Inicio Rápido

### 1. Requisitos

- Python 3.12+
- pip
- 3 terminales (para ejecutar 3 servidores)

### 2. Instalación

```bash
# Clonar/descargar el proyecto
cd /home/andrea/XDEI/AndreaVaqueiro_VeronicaVila_P3

# Crear virtual environment
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install flask flask-cors requests
```

### 3. Ejecutar Sistema

**Terminal 1: Mock Orion Context Broker**

```bash
cd /home/andrea/XDEI/AndreaVaqueiro_VeronicaVila_P3
source venv/bin/activate
python mock_orion.py

# Output esperado:
# 🔌 Mock Orion + QuantumLeap iniciado en http://localhost:8000
```

**Terminal 2: Simulador de Datos**

```bash
cd /home/andrea/XDEI/AndreaVaqueiro_VeronicaVila_P3
source venv/bin/activate
ORION_BASE_URL="http://localhost:8000" \
SIM_ITERATIONS=500 \
SIM_SLEEP_SECONDS=3 \
python simulate_streetlights.py

# Output esperado:
# [Iteración 1] Peatones: 26, Intensidad base: 60%
# [Iteración 2] Peatones: 10, Intensidad base: 20%
```

**Terminal 3: Web Server**

```bash
cd /home/andrea/XDEI/AndreaVaqueiro_VeronicaVila_P3
source venv/bin/activate
python web_server.py

# Output esperado:
# 🌐 Servidor Web iniciado en http://localhost:3000
```

### 4. Acceder Dashboard

```
http://localhost:3000
```

---

## 🗺️ Dashboard - Cómo Usar

### Panel Principal

**Estado General**
- 🔴 Farolas Activas: Número de farolas con status "on"
- 👥 Peatones Detectados: Flujo peatonal actual
- ⚡ Consumo (kWh): Energía consumida en últimas 6 horas
- ⚠️ Anomalías: Alertas de farolas con fallo

**Mapa**
- 💡 Amarillo: Farola funcionando normalmente (ON)
- ⚫ Gris: Farola apagada (OFF)
- ⚠️ Rojo: Farola con fallo (FAULT)
- 🔥 Heatmap: Actividad urbana (click toggle para activar/desactivar)

**Recomendación**
- Sugerencia de intensidad óptima basada en peatones
- Botón para aplicar cambios

**Gráficos**
- ⚡ Consumo Energético: Línea con histórico 6h
- 👥 Flujo Peatonal: Barras con histórico 6h

### Heatmap de Actividad

**Cómo activar:**
1. Hacer click en botón "🔥 Heatmap: OFF" (esquina superior derecha)
2. Verá colores en el mapa:
   - 🔵 Azul: Baja actividad
   - 🟢 Verde: Actividad normal
   - 🟡 Amarillo: Actividad moderada
   - 🟠 Naranja: Alta actividad
   - 🔴 Rojo: Máxima actividad

**Intensidad:**
- Basada en densidad de peatones/tráfico
- Se actualiza cada 10 segundos
- No oculta marcadores de farolas

---

## 📊 Estadísticas Actuales

| Métrica | Valor |
|---------|-------|
| **Farolas Totales** | 68 |
| **Farolas Activas (ON)** | 47 (69%) |
| **Farolas Apagadas (OFF)** | 11 (16%) |
| **Farolas Averiadas (FAULT)** | 10 (15%) |
| **Potencia Total** | 4,700 W |
| **Consumo 6h** | 28.2 kWh |
| **Zonas** | 6 |
| **Grupos** | 6 |
| **Armarios Control** | 6 |
| **Líneas Alimentación** | 6 |

---

## 🔌 API FIWARE NGSI-LD

### Endpoints Mock Orion (Puerto 8000)

```bash
# Listar farolas
GET http://localhost:8000/ngsi-ld/v1/entities?type=Streetlight

# Obtener una farola específica
GET http://localhost:8000/ngsi-ld/v1/entities/urn:ngsi-ld:Streetlight:coruña:SL-001

# Obtener grupos
GET http://localhost:8000/ngsi-ld/v1/entities?type=StreetlightGroup

# Obtener flujo peatonal
GET http://localhost:8000/ngsi-ld/v1/entities?type=CrowdFlowObserved

# Actualizar estado de farola
PATCH http://localhost:8000/ngsi-ld/v1/entities/urn:ngsi-ld:Streetlight:coruña:SL-001/attrs
{
  "status": {
    "type": "Property",
    "value": "off"
  }
}
```

### Endpoints Web Server (Puerto 3000)

```bash
# Servir dashboard
GET http://localhost:3000/

# Health check
GET http://localhost:3000/health

# FIWARE (cuando esté implementado)
GET http://localhost:3000/api/streetlights/fiware
GET http://localhost:3000/api/crowd-flows/fiware
GET http://localhost:3000/api/traffic-flows/fiware
```

---

## 🔄 Ciclo de Datos

1. **Provisión Inicial** (0 seg)
   - Generador crea 68 farolas FIWARE
   - Mock Orion almacena en memoria

2. **Simulación** (3 seg)
   - Simulador aleatoriamente cambia:
     - Estado (ON/OFF/FAULT)
     - Intensidad (20-100%)
     - Peatones (5-50)
   - PATCH actualiza en Orion

3. **Dashboard Refresh** (10 seg)
   - Fetch obtiene datos de Orion
   - Convierte a formato Leaflet
   - Renderiza marcadores en mapa
   - Actualiza heatmap si está habilitado

4. **Histórico** (Guardado)
   - QuantumLeap simula histórico
   - Se pueden consultar cambios anteriores

---

## 📐 Modelo de Datos FIWARE

### Entidad Streetlight (Farola)

```json
{
  "id": "urn:ngsi-ld:Streetlight:coruña:SL-001",
  "type": "Streetlight",
  "location": {
    "type": "GeoProperty",
    "value": { "type": "Point", "coordinates": [-8.3890, 43.3790] }
  },
  "status": { "type": "Property", "value": "on" },
  "powerState": { "type": "Property", "value": "normal" },
  "luminousIntensity": { "type": "Property", "value": 85 },
  "powerConsumption": { "type": "Property", "value": 102.0 },
  "illuminanceLevel": { "type": "Property", "value": 8500 },
  "dateObserved": { "type": "Property", "value": "2026-05-04T14:58:47Z" },
  "refStreetlightGroup": { "type": "Relationship", "object": "urn:ngsi-ld:StreetlightGroup:coruña:grupo-centro" },
  "refStreetlightModel": { "type": "Relationship", "object": "urn:ngsi-ld:StreetlightModel:coruña:LED-200" }
}
```

### Jerarquía de Relaciones

```
Streetlight (68)
├── refStreetlightModel → StreetlightModel (3)
├── refStreetlightGroup → StreetlightGroup (6)
│   ├── refControlCabinet → StreetlightControlCabinet (6)
│   └── refFeeder → StreetlightFeeder (6)
└── Flujos de Contexto:
    ├── CrowdFlowObserved (2+) → refStreetlightGroup
    ├── TrafficFlowObserved (1+) → refStreetlightGroup
    └── ItemFlowObserved (2+) → refStreetlightGroup
```

---

## 📁 Modelos FIWARE Disponibles

| Tipo | Cantidad | Descripción |
|------|----------|-------------|
| **Streetlight** | 68 | Farolas individuales |
| **StreetlightGroup** | 6 | Grupos por zona |
| **StreetlightControlCabinet** | 6 | Armarios de control |
| **StreetlightFeeder** | 6 | Líneas de alimentación |
| **StreetlightModel** | 3 | Modelos técnicos (LED, HPS) |
| **CrowdFlowObserved** | 2+ | Flujo de peatones |
| **TrafficFlowObserved** | 1+ | Flujo de tráfico |
| **ItemFlowObserved** | 2+ | Flujo genérico |
| **TOTAL** | **94+** | Entidades FIWARE |

---

## 🛠️ Configuración

### Variables de Entorno

```bash
# Backend
ORION_BASE_URL="http://localhost:8000"
API_BASE="http://localhost:8000"

# Simulador
SIM_ITERATIONS=500      # Número de iteraciones
SIM_SLEEP_SECONDS=3     # Tiempo entre iteraciones

# Frontend (index.html)
API_BASE="http://localhost:8000"
```

### Puertos

| Servicio | Puerto | URL |
|----------|--------|-----|
| Mock Orion | 8000 | http://localhost:8000 |
| Web Server | 3000 | http://localhost:3000 |
| Simulador | (interno) | - |

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'flask'"

```bash
source venv/bin/activate
pip install flask flask-cors requests
```

### "Address already in use" en puerto 8000/3000

```bash
# Encontrar proceso en puerto
lsof -i :8000

# Matar proceso
kill -9 <PID>
```

### Dashboard no muestra farolas

1. Verificar que Mock Orion está corriendo
2. Verificar que Simulador está corriendo
3. Abrir Developer Console (F12) y revisar errores
4. Verificar URL en `API_BASE` en `index.html`

### Heatmap no se ve

1. Verificar que leaflet.heat está cargado (Inspector: buscar "leaflet-heat")
2. Hacer click en botón "🔥 Heatmap: OFF" para activar
3. Revisar console para logs de heatmap
4. Esperar 10 segundos a que se actualice dashboard

---

## 📚 Documentación

- [FIWARE_DATA_MODEL.md](FIWARE_DATA_MODEL.md) - Especificación completa de entidades
- [FIWARE_INTEGRATION.md](FIWARE_INTEGRATION.md) - Guía de integración técnica
- [PRD.md](PRD.md) - Requerimientos funcionales
- [architecture.md](architecture.md) - Arquitectura del sistema

---

## 🎯 Próximas Fases

### Fase 2: Orion Real
- Desplegar Orion Context Broker
- Conectar QuantumLeap
- Migrations de datos mock → real

### Fase 3: Machine Learning
- Optimización automática de intensidad
- Predicción de demanda
- Mantenimiento predictivo

### Fase 4: Escalabilidad
- WebSockets para updates en tiempo real
- Dashboard de analítica histórica
- API de terceros

---

## 👥 Equipo

- **Andrea Vaqueiro**
- **Verónica Vila**

**Institución**: Universidad
**Proyecto**: P3 - Eco-Dimming MVP
**Año**: 2026

---

## 📜 Licencia

Proyecto académico. Uso educativo y de investigación.

---

## 📞 Soporte

Para dudas o problemas:
1. Revisar la sección "Troubleshooting"
2. Consultar documentación en `/FIWARE_*.md`
3. Verificar logs en consolas de ejecución

---

**Estado del Proyecto**: ✅ MVP Funcional
**Versión**: 1.0
**Última actualización**: 2026-05-04
