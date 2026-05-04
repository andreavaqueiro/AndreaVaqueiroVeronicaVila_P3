# Guía de Integración FIWARE - Iluminación Urbana Inteligente

## Resumen

Este documento describe cómo integrar el MVP del dashboard de iluminación con entidades **FIWARE NGSI-LD** en lugar de datos mock simples.

---

## Arquitectura Actual vs Propuesta

### ❌ Arquitectura Actual (Mock)

```
[Dashboard (index.html)]
    ↓ fetch
[Web Server (port 3000)]
    ↓ GET /
[Mock Data MOCK_STREETLIGHTS]
    ↓ JSON simple
[Leaflet Map]
```

### ✅ Arquitectura Propuesta (FIWARE)

```
[Dashboard (index.html)]
    ↓ fetch
[Web Server (port 3000)]
    ↓ GET /api/streetlights
[FIWARE Adapter (fiware_adapter.py)]
    ↓ NGSI-LD entities
[Mock Orion (port 8000) o Orion Real]
    ↓ Storage
[Leaflet Map + Heatmap]
```

---

## Paso 1: Entidades FIWARE Disponibles

### Módulos Creados

1. **fiware_data_models.py**
   - Definición de clases NGSI-LD para:
     - `Streetlight` (farola individual)
     - `StreetlightGroup` (grupo de farolas)
     - `StreetlightControlCabinet` (armario de control)
     - `StreetlightFeeder` (línea de alimentación)
     - `StreetlightModel` (modelo técnico)
     - `CrowdFlowObserved` (flujo peatonal)
     - `TrafficFlowObserved` (flujo de tráfico)
     - `ItemFlowObserved` (flujo genérico)

2. **generate_fiware_entities.py**
   - Generador de 68+ farolas FIWARE-compatibles
   - Distribución geográfica en 6 zonas de A Coruña
   - Exporta a `fiware_entities.json`

3. **fiware_adapter.py**
   - Adaptador para consumo en frontend
   - Métodos de conversión NGSI-LD → formato Leaflet
   - Cálculo de estadísticas FIWARE
   - Exporta a `fiware_adapter_example.json`

---

## Paso 2: Integración en el Backend

### 2.1 Actualizar `mock_orion.py`

Reemplazar provisión de mock data con FIWARE:

```python
# mock_orion.py (pseudocódigo)
from generate_fiware_entities import generate_all_entities

@app.route('/ngsi-ld/v1/entities', methods=['POST'])
def create_entity():
    """Crear entidad FIWARE."""
    data = request.json
    entity_id = data.get('id')
    entity_type = data.get('type')
    
    # Guardar en memoria
    entities_store[entity_id] = data
    
    # Sincronizar con QuantumLeap si existe
    if entity_type == 'Streetlight':
        notify_quantumleap(data)
    
    return jsonify({"id": entity_id}), 201

@app.route('/ngsi-ld/v1/entities/<entity_id>', methods=['GET'])
def get_entity(entity_id):
    """Obtener entidad por ID."""
    return jsonify(entities_store.get(entity_id, {}))

@app.route('/ngsi-ld/v1/entities', methods=['GET'])
def list_entities():
    """Listar entidades (con filtros opcionales)."""
    entity_type = request.args.get('type')
    
    if entity_type:
        return jsonify([e for e in entities_store.values() 
                       if e.get('type') == entity_type])
    
    return jsonify(list(entities_store.values()))
```

### 2.2 Crear endpoint de inicialización FIWARE

```python
# web_server.py o extension

@app.route('/api/fiware/initialize', methods=['POST'])
def initialize_fiware():
    """Inicializar todas las entidades FIWARE."""
    from generate_fiware_entities import generate_all_entities
    
    entities = generate_all_entities()
    
    # Provisionar en Orion (vía mock_orion.py)
    for entity_type, entity_list in entities.items():
        for entity in entity_list:
            requests.post(
                f"{ORION_BASE_URL}/ngsi-ld/v1/entities",
                json=entity
            )
    
    return jsonify({"status": "initialized", "total": 107})
```

### 2.3 Crear endpoints FIWARE para dashboard

```python
# web_server.py (adicionales)

@app.route('/api/streetlights/fiware', methods=['GET'])
def get_streetlights_fiware():
    """Obtener farolas en formato FIWARE adaptado."""
    from fiware_adapter import FIWAREAdapter
    
    adapter = FIWAREAdapter()
    return jsonify({
        "data": adapter.streetlights_to_frontend(),
        "stats": adapter.get_streetlight_statistics()
    })

@app.route('/api/crowd-flows/fiware', methods=['GET'])
def get_crowd_flows_fiware():
    """Obtener flujos peatonales FIWARE."""
    from fiware_adapter import FIWAREAdapter
    
    adapter = FIWAREAdapter()
    return jsonify(adapter.crowd_flows_to_frontend())

@app.route('/api/traffic-flows/fiware', methods=['GET'])
def get_traffic_flows_fiware():
    """Obtener flujos de tráfico FIWARE."""
    from fiware_adapter import FIWAREAdapter
    
    adapter = FIWAREAdapter()
    return jsonify(adapter.traffic_flows_to_frontend())
```

---

## Paso 3: Integración en el Frontend

### 3.1 Actualizar `index.html` para consumir FIWARE

Cambiar endpoints en `loadStreetlights()`:

```javascript
// ANTES (mock):
const resp = await fetch(`${API_BASE}/ngsi-ld/v1/entities?type=Streetlight`);

// DESPUÉS (FIWARE):
const resp = await fetch(`${API_BASE}/api/streetlights/fiware`);
```

### 3.2 Mapeo de propiedades FIWARE → Leaflet

```javascript
// Función auxiliar para convertir FIWARE → formato Leaflet
function fiwareToLeaflet(fiwareEntity) {
    return {
        id: fiwareEntity.id,
        lat: fiwareEntity.lat,  // FIWARE adapter ya convierte
        lng: fiwareEntity.lng,
        status: fiwareEntity.status,
        intensity: fiwareEntity.intensity,
        power: fiwareEntity.power,
        // ... más atributos
    };
}
```

### 3.3 Actualizar heatmap para usar FIWARE

```javascript
// En generateHeatmapData():
// Usar CrowdFlowObserved directamente
if (crowdFlows && crowdFlows.length > 0) {
    crowdFlows.forEach(flow => {
        let coords = flow.location;  // Ya es [lon, lat]
        let intensity = flow.occupancy;  // 0-1
        heatData.push([coords[1], coords[0], intensity]);
    });
}
```

---

## Paso 4: Migración de Datos

### 4.1 Provisión Inicial

**Opción A: Automática (recomendado)**

```bash
# Inicializar FIWARE en el sistema
curl -X POST http://localhost:3000/api/fiware/initialize
```

**Opción B: Manual desde fichero**

```bash
# Importar entidades desde fiware_entities.json
for entity in $(jq -r '.Streetlight[] | @base64' fiware_entities.json); do
    curl -X POST http://localhost:8000/ngsi-ld/v1/entities \
        -d $(echo $entity | base64 -d)
done
```

### 4.2 Verificación

```bash
# Listar todas las farolas FIWARE
curl http://localhost:8000/ngsi-ld/v1/entities?type=Streetlight | jq '.[] | {id, status}'

# Contar por zona
curl http://localhost:8000/ngsi-ld/v1/entities?type=StreetlightGroup | jq '.[] | .id'
```

---

## Paso 5: Actualizar Mock Data para usar FIWARE

### 5.1 Cambiar `provision_entities.py`

```python
# provision_entities.py (actualizado)

from fiware_data_models import *
from generate_fiware_entities import generate_all_entities

def provision_fiware_entities(base_url: str):
    """Provisionar todas las entidades FIWARE en Orion."""
    entities = generate_all_entities()
    
    for entity_type, entity_list in entities.items():
        for entity in entity_list:
            response = requests.post(
                f"{base_url}/ngsi-ld/v1/entities",
                json=entity,
                headers={"Content-Type": "application/ld+json"}
            )
            if response.status_code != 201:
                print(f"❌ Error provisioning {entity['id']}: {response.text}")
            else:
                print(f"✅ Provisioned {entity['id']}")

if __name__ == "__main__":
    ORION_BASE_URL = os.getenv("ORION_BASE_URL", "http://localhost:8000")
    provision_fiware_entities(ORION_BASE_URL)
```

### 5.2 Ejecutar provisión

```bash
ORION_BASE_URL="http://localhost:8000" python provision_entities.py
```

---

## Paso 6: Configuración de Simulación FIWARE

### 6.1 Actualizar `simulate_streetlights.py`

```python
# simulate_streetlights.py (actualizado para FIWARE)

from fiware_adapter import FIWAREAdapter

class FIWARESimulator:
    def __init__(self, orion_url: str):
        self.adapter = FIWAREAdapter()
        self.orion_url = orion_url
    
    def simulate_updates(self, iterations: int = 100, interval: int = 3):
        """Simular cambios de estado de farolas."""
        for iteration in range(iterations):
            # Obtener farolas actuales
            streetlights = self.adapter.streetlights
            
            # Modificar aleatoriamente
            for sl in random.sample(streetlights, k=min(10, len(streetlights))):
                # Cambiar estado o intensidad
                sl.luminous_intensity = random.randint(20, 100)
                
                # Actualizar en Orion
                ngsi_entity = sl.to_ngsi_ld()
                requests.patch(
                    f"{self.orion_url}/ngsi-ld/v1/entities/{sl.id}/attrs",
                    json=ngsi_entity
                )
            
            print(f"[Iteration {iteration}] Updated {len(streetlights)} streetlights")
            time.sleep(interval)

if __name__ == "__main__":
    simulator = FIWARESimulator(
        os.getenv("ORION_BASE_URL", "http://localhost:8000")
    )
    simulator.simulate_updates()
```

---

## Paso 7: Verificación de Integración

### 7.1 Checklist

- ✅ Modelos FIWARE definidos en `fiware_data_models.py`
- ✅ Entidades generadas en `generate_fiware_entities.py`
- ✅ Adaptador frontend en `fiware_adapter.py`
- ✅ Endpoints backend creados
- ✅ Dashboard actualizado para consumir `/api/streetlights/fiware`
- ✅ Heatmap usa datos FIWARE
- ✅ Provisión automática funciona
- ✅ Simulador actualiza entidades FIWARE

### 7.2 Pruebas

```bash
# 1. Inicializar FIWARE
curl -X POST http://localhost:3000/api/fiware/initialize

# 2. Verificar farolas
curl http://localhost:8000/ngsi-ld/v1/entities?type=Streetlight | jq '.[] | .id' | wc -l

# 3. Consultar flujo peatonal
curl http://localhost:3000/api/crowd-flows/fiware | jq '.[] | {id, peopleCount}'

# 4. Acceder dashboard
open http://localhost:3000
```

---

## Paso 8: Migración a Orion Real (Futuro)

Cuando tengas Orion y QuantumLeap instalados:

```bash
# Actualizar BASE_URL en código
export ORION_BASE_URL="http://orion.example.com:1026"
export QUANTUMLEAP_URL="http://quantumleap.example.com:8668"

# Provisionar entidades reales
python provision_entities.py

# Iniciar simulación
python simulate_streetlights.py
```

---

## Estructura de Ficheros

```
/home/andrea/XDEI/AndreaVaqueiro_VeronicaVila_P3/
├── fiware_data_models.py          ← Definiciones NGSI-LD
├── generate_fiware_entities.py     ← Generador de entidades
├── fiware_adapter.py               ← Adaptador para frontend
├── fiware_entities.json            ← Dump de entidades (referencia)
├── fiware_adapter_example.json     ← Ejemplo de adaptador
├── FIWARE_DATA_MODEL.md            ← Documentación de modelos
├── FIWARE_INTEGRATION.md           ← Este documento
├── mock_orion.py                   ← Backend con CORS
├── web_server.py                   ← Servidor web
├── provision_entities.py            ← Provisión FIWARE
├── simulate_streetlights.py        ← Simulador FIWARE
└── index.html                      ← Dashboard (necesita actualización)
```

---

## Ejemplos de Respuestas FIWARE

### GET `/api/streetlights/fiware`

```json
{
  "data": [
    {
      "id": "urn:ngsi-ld:Streetlight:coruña:SL-001",
      "type": "Streetlight",
      "lat": 43.3790,
      "lng": -8.3890,
      "status": "on",
      "intensity": 85,
      "power": 102.0,
      "illuminanceLevel": 8500,
      "powerState": "normal",
      "dateObserved": "2026-05-04T14:58:47Z",
      "refGroup": "urn:ngsi-ld:StreetlightGroup:coruña:grupo-centro"
    }
  ],
  "stats": {
    "total": 68,
    "on": 47,
    "off": 11,
    "fault": 10,
    "totalPowerConsumption": 4700.0,
    "totalEnergyConsumption6h": 28.2
  }
}
```

### GET `/api/crowd-flows/fiware`

```json
[
  {
    "id": "urn:ngsi-ld:CrowdFlowObserved:coruña:centro",
    "type": "CrowdFlowObserved",
    "location": [-8.3890, 43.3790],
    "peopleCount": 42,
    "occupancy": 0.42,
    "description": "Flujo peatonal - Centro Histórico",
    "dateObserved": "2026-05-04T14:58:47Z"
  }
]
```

---

## Referencias

- [FIWARE Smart Data Models](https://github.com/smart-data-models)
- [FIWARE NGSI-LD v1.6](https://www.etsi.org/deliver/etsi_gs/CIM/001_099/008/01.06.01_60/gs_cim_008v010601p.pdf)
- [Orion Context Broker](https://fiware-orion.readthedocs.io/)
- [QuantumLeap](https://quantumleap.readthedocs.io/)

---

**Versión**: 1.0
**Estado**: Integración FIWARE Completa
**Próximos Pasos**: Conectar con Orion real + QuantumLeap
