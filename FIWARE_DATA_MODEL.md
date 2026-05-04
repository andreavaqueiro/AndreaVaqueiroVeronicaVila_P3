# Modelo de Datos FIWARE - Iluminación Urbana Inteligente en A Coruña

## Visión General

Este MVP implementa un sistema de iluminación urbana inteligente basado en los **Smart Data Models de FIWARE** (NGSI-LD). Los datos siguen la especificación NGSI-LD y son compatibles con **Orion Context Broker** y **QuantumLeap**.

### Estándares Utilizados

- **NGSI-LD v1.6**: Especificación de datos de contexto
- **FIWARE Smart Data Models**: Modelos de datos estandarizados
  - `dataModel.Streetlighting`: Datos de iluminación urbana
  - `dataModel.Transportation`: Datos de tráfico y flujo peatonal

### Zonificación de A Coruña

El MVP cubre 6 zonas principales:

| Zona | Centro (lon, lat) | Descripción | Farolas |
|------|-------------------|-------------|---------|
| Centro | (-8.3890, 43.3790) | Centro Histórico | 12 |
| Ciudad Vieja | (-8.3750, 43.3850) | Ciudad Vieja | 12 |
| Calle Real | (-8.4000, 43.3750) | Calle Real | 11 |
| Paseo Marítimo | (-8.3600, 43.3700) | Paseo Marítimo | 10 |
| Ensanche | (-8.4100, 43.3600) | Ensanche | 12 |
| Avenida Juan Flórez | (-8.4200, 43.3800) | Avenida Juan Flórez | 11 |
| **Total** | | | **70** |

---

## Entidades Principales

### 1. Streetlight (Farola Individual)

**Tipo NGSI-LD**: `Streetlight`

**Propósito**: Representa una farola individual del sistema de iluminación.

**Atributos**:

```ngsi-ld
{
  "id": "urn:ngsi-ld:Streetlight:coruña:SL-001",
  "type": "Streetlight",
  
  // Ubicación geográfica
  "location": {
    "type": "GeoProperty",
    "value": {
      "type": "Point",
      "coordinates": [-8.3890, 43.3790]  // [lon, lat]
    }
  },
  
  // Estado de la farola
  "status": {
    "type": "Property",
    "value": "on"  // on | off | fault | dimmed
  },
  
  // Estado de energía
  "powerState": {
    "type": "Property",
    "value": "normal"  // normal | lowPower | failure | maintenance
  },
  
  // Intensidad luminosa (0-100%)
  "luminousIntensity": {
    "type": "Property",
    "value": 85
  },
  
  // Consumo de potencia (W)
  "powerConsumption": {
    "type": "Property",
    "value": 102.0  // 85% * 120W
  },
  
  // Nivel de iluminancia (lux)
  "illuminanceLevel": {
    "type": "Property",
    "value": 8500  // 85 * 100 lux
  },
  
  // Fecha de observación (ISO 8601)
  "dateObserved": {
    "type": "Property",
    "value": "2026-05-04T14:58:47Z"
  },
  
  // Referencias a otras entidades
  "refStreetlightModel": {
    "type": "Relationship",
    "object": "urn:ngsi-ld:StreetlightModel:coruña:LED-200"
  },
  
  "refStreetlightGroup": {
    "type": "Relationship",
    "object": "urn:ngsi-ld:StreetlightGroup:coruña:grupo-centro"
  },
  
  "refControlCabinet": {
    "type": "Relationship",
    "object": "urn:ngsi-ld:StreetlightControlCabinet:coruña:centro"
  },
  
  "refFeeder": {
    "type": "Relationship",
    "object": "urn:ngsi-ld:StreetlightFeeder:coruña:centro"
  }
}
```

**Distribución de Estados**:
- 75% ON (farolas funcionando normalmente)
- 10% OFF (farolas apagadas)
- 15% FAULT (farolas con fallo)

---

### 2. StreetlightGroup (Grupo de Farolas)

**Tipo NGSI-LD**: `StreetlightGroup`

**Propósito**: Agrupa farolas por zona, barrio o línea de alimentación.

**Atributos**:

```ngsi-ld
{
  "id": "urn:ngsi-ld:StreetlightGroup:coruña:grupo-centro",
  "type": "StreetlightGroup",
  
  // Centroide del grupo
  "location": {
    "type": "GeoProperty",
    "value": {
      "type": "Point",
      "coordinates": [-8.3890, 43.3790]
    }
  },
  
  // Descripción del grupo
  "description": {
    "type": "Property",
    "value": "Grupo de farolas del Centro Histórico"
  },
  
  // Estado de energía del grupo
  "powerState": {
    "type": "Property",
    "value": "normal"
  },
  
  // Lista de farolas del grupo
  "hasStreetlight": {
    "type": "Relationship",
    "object": [
      "urn:ngsi-ld:Streetlight:coruña:SL-001",
      "urn:ngsi-ld:Streetlight:coruña:SL-002",
      // ... 10 más
    ]
  },
  
  // Referencia al armario de control
  "refControlCabinet": {
    "type": "Relationship",
    "object": "urn:ngsi-ld:StreetlightControlCabinet:coruña:centro"
  },
  
  // Referencia a la línea de alimentación
  "refFeeder": {
    "type": "Relationship",
    "object": "urn:ngsi-ld:StreetlightFeeder:coruña:centro"
  },
  
  "dateObserved": {
    "type": "Property",
    "value": "2026-05-04T14:58:47Z"
  }
}
```

**Cantidad**: 6 grupos (uno por zona)

---

### 3. StreetlightControlCabinet (Armario de Control)

**Tipo NGSI-LD**: `StreetlightControlCabinet`

**Propósito**: Representa el armario de control que gestiona un grupo de farolas.

**Atributos**:

```ngsi-ld
{
  "id": "urn:ngsi-ld:StreetlightControlCabinet:coruña:centro",
  "type": "StreetlightControlCabinet",
  
  // Ubicación del armario
  "location": {
    "type": "GeoProperty",
    "value": {
      "type": "Point",
      "coordinates": [-8.3890, 43.3790]
    }
  },
  
  // Descripción
  "description": {
    "type": "Property",
    "value": "Armario de control - Centro Histórico"
  },
  
  // Estado
  "status": {
    "type": "Property",
    "value": "on"
  },
  
  // Estado de energía
  "powerState": {
    "type": "Property",
    "value": "normal"  // normal | lowPower | failure
  },
  
  // Referencia a la línea de alimentación
  "refFeeder": {
    "type": "Relationship",
    "object": "urn:ngsi-ld:StreetlightFeeder:coruña:centro"
  },
  
  "dateObserved": {
    "type": "Property",
    "value": "2026-05-04T14:58:47Z"
  }
}
```

**Cantidad**: 6 armarios (uno por zona)

---

### 4. StreetlightFeeder (Línea de Alimentación)

**Tipo NGSI-LD**: `StreetlightFeeder`

**Propósito**: Representa las líneas de alimentación eléctrica del sistema.

**Atributos**:

```ngsi-ld
{
  "id": "urn:ngsi-ld:StreetlightFeeder:coruña:centro",
  "type": "StreetlightFeeder",
  
  // Descripción
  "description": {
    "type": "Property",
    "value": "Línea de alimentación - Centro Histórico"
  },
  
  // Voltaje (V)
  "voltage": {
    "type": "Property",
    "value": 230.0
  },
  
  // Amperaje (A)
  "amperage": {
    "type": "Property",
    "value": 63.0
  },
  
  // Estado de energía
  "powerState": {
    "type": "Property",
    "value": "normal"
  },
  
  "dateObserved": {
    "type": "Property",
    "value": "2026-05-04T14:58:47Z"
  }
}
```

**Cantidad**: 6 líneas (una por zona)

---

### 5. StreetlightModel (Modelo Técnico)

**Tipo NGSI-LD**: `StreetlightModel`

**Propósito**: Define las características técnicas de los diferentes tipos de farola.

**Atributos**:

```ngsi-ld
{
  "id": "urn:ngsi-ld:StreetlightModel:coruña:LED-200",
  "type": "StreetlightModel",
  
  // Descripción
  "description": {
    "type": "Property",
    "value": "Farola LED 200W - Modelo estándar"
  },
  
  // Marca
  "brand": {
    "type": "Property",
    "value": "Philips"
  },
  
  // Nombre del modelo
  "modelName": {
    "type": "Property",
    "value": "StreetLite Mini"
  },
  
  // Tipo de lámpara
  "lampType": {
    "type": "Property",
    "value": "LED"  // LED | HPS | Fluorescent
  },
  
  // Flujo luminoso (lúmenes)
  "luminousFlux": {
    "type": "Property",
    "value": 25000
  },
  
  // Temperatura de color (K)
  "colorTemperature": {
    "type": "Property",
    "value": 4000
  },
  
  // Vida esperada (horas)
  "lifeExpectancy": {
    "type": "Property",
    "value": 50000
  },
  
  "dateObserved": {
    "type": "Property",
    "value": "2026-05-04T14:58:47Z"
  }
}
```

**Modelos Disponibles**:
1. LED-200 (Philips StreetLite Mini) - 25000 lm
2. LED-150 (Osram Echelon) - 18000 lm
3. HPS-250 (Sylvania Supersonic) - 25000 lm

---

## Entidades de Contexto Urbano

### 6. CrowdFlowObserved (Flujo Peatonal)

**Tipo NGSI-LD**: `CrowdFlowObserved`

**Propósito**: Observación de flujo peatonal en una zona para optimizar iluminación.

**Atributos**:

```ngsi-ld
{
  "id": "urn:ngsi-ld:CrowdFlowObserved:coruña:centro",
  "type": "CrowdFlowObserved",
  
  // Ubicación de la observación
  "location": {
    "type": "GeoProperty",
    "value": {
      "type": "Point",
      "coordinates": [-8.3890, 43.3790]
    }
  },
  
  // Cantidad de peatones detectados
  "peopleCount": {
    "type": "Property",
    "value": 42
  },
  
  // Ocupación relativa (0-1)
  "occupancy": {
    "type": "Property",
    "value": 0.42
  },
  
  // Ocupación máxima esperada
  "maxOccupancy": {
    "type": "Property",
    "value": 100
  },
  
  // Descripción de la zona
  "description": {
    "type": "Property",
    "value": "Flujo peatonal - Centro Histórico"
  },
  
  // Referencia al grupo de farolas cercano
  "refStreetlightGroup": {
    "type": "Relationship",
    "object": "urn:ngsi-ld:StreetlightGroup:coruña:grupo-centro"
  },
  
  "dateObserved": {
    "type": "Property",
    "value": "2026-05-04T14:58:47Z"
  }
}
```

**Cantidad**: 6 (uno por zona)
**Rango de valores**: 5-50 peatones (simulado)

---

### 7. TrafficFlowObserved (Flujo de Tráfico)

**Tipo NGSI-LD**: `TrafficFlowObserved`

**Propósito**: Observación de flujo vehicular para optimizar iluminación de vías.

**Atributos**:

```ngsi-ld
{
  "id": "urn:ngsi-ld:TrafficFlowObserved:coruña:calle-real",
  "type": "TrafficFlowObserved",
  
  // Ubicación de la observación
  "location": {
    "type": "GeoProperty",
    "value": {
      "type": "Point",
      "coordinates": [-8.4000, 43.3750]
    }
  },
  
  // Cantidad de vehículos
  "vehicleCount": {
    "type": "Property",
    "value": 18
  },
  
  // Tipo de vehículos
  "vehicleType": {
    "type": "Property",
    "value": "mixed"  // car | bus | truck | mixed
  },
  
  // Descripción
  "description": {
    "type": "Property",
    "value": "Flujo de tráfico - Calle Real"
  },
  
  // Referencia al grupo de farolas
  "refStreetlightGroup": {
    "type": "Relationship",
    "object": "urn:ngsi-ld:StreetlightGroup:coruña:grupo-calle-real"
  },
  
  "dateObserved": {
    "type": "Property",
    "value": "2026-05-04T14:58:47Z"
  }
}
```

**Cantidad**: 4 (en zonas principales con tráfico)
**Rango de valores**: 5-30 vehículos (simulado)

---

### 8. ItemFlowObserved (Flujo Genérico)

**Tipo NGSI-LD**: `ItemFlowObserved`

**Propósito**: Observación genérica de flujo de elementos/personas para uso extensible.

**Atributos**:

```ngsi-ld
{
  "id": "urn:ngsi-ld:ItemFlowObserved:coruña:centro",
  "type": "ItemFlowObserved",
  
  // Ubicación
  "location": {
    "type": "GeoProperty",
    "value": {
      "type": "Point",
      "coordinates": [-8.3890, 43.3790]
    }
  },
  
  // Cantidad de elementos
  "itemCount": {
    "type": "Property",
    "value": 12
  },
  
  // Tipo de elemento
  "itemType": {
    "type": "Property",
    "value": "generic"  // generic | person | vehicle | bike
  },
  
  // Descripción
  "description": {
    "type": "Property",
    "value": "Flujo genérico - Centro Histórico"
  },
  
  // Referencia al grupo
  "refStreetlightGroup": {
    "type": "Relationship",
    "object": "urn:ngsi-ld:StreetlightGroup:coruña:grupo-centro"
  },
  
  "dateObserved": {
    "type": "Property",
    "value": "2026-05-04T14:58:47Z"
  }
}
```

**Cantidad**: 6 (uno por zona)

---

## Relaciones entre Entidades

### Jerarquía Estructural

```
Streetlight (70)
    ↓ refStreetlightModel
StreetlightModel (3)

    ↓ refStreetlightGroup
StreetlightGroup (6)
    ↓ hasStreetlight
    ├─ Streetlight (70)
    
    ↓ refControlCabinet
StreetlightControlCabinet (6)

    ↓ refFeeder
StreetlightFeeder (6)
```

### Relaciones de Contexto Urbano

```
CrowdFlowObserved (6)
    ↓ refStreetlightGroup
StreetlightGroup (6)

TrafficFlowObserved (4)
    ↓ refStreetlightGroup
StreetlightGroup (sub)

ItemFlowObserved (6)
    ↓ refStreetlightGroup
StreetlightGroup (6)
```

---

## Volumen Total de Datos

| Tipo de Entidad | Cantidad |
|-----------------|----------|
| Streetlight | 70 |
| StreetlightGroup | 6 |
| StreetlightControlCabinet | 6 |
| StreetlightFeeder | 6 |
| StreetlightModel | 3 |
| CrowdFlowObserved | 6 |
| TrafficFlowObserved | 4 |
| ItemFlowObserved | 6 |
| **TOTAL** | **107** |

---

## Casos de Uso

### 1. Dashboard de Iluminación
- Mostrar estados de farolas en el mapa (desde `Streetlight`)
- Calcular consumo energético total (desde `Streetlight.powerConsumption`)
- Agrupar por zonas (desde `StreetlightGroup`)

### 2. Heatmap de Actividad Urbana
- Mostrar intensidad de ocupación (desde `CrowdFlowObserved`)
- Correlacionar con iluminación (desde `Streetlight.luminousIntensity`)
- Optimizar intensidad dinámicamente

### 3. Gestión de Tráfico y Seguridad
- Mostrar flujo de vehículos (desde `TrafficFlowObserved`)
- Aumentar iluminación en zonas de alto tráfico
- Alertas de mantenimiento (desde `Streetlight.powerState`)

### 4. Mantenimiento Predictivo
- Monitorear `powerState` de farolas
- Alertar sobre fallos (`status = "fault"`)
- Planificar reemplazos usando `StreetlightModel.lifeExpectancy`

### 5. Optimización Energética
- Calcular consumo por grupo (agregar `Streetlight.powerConsumption`)
- Ajustar `luminousIntensity` según `CrowdFlowObserved`
- Generar reportes de eficiencia energética

---

## Formato NGSI-LD

Todas las entidades siguen el estándar NGSI-LD v1.6:

```
{
  "id": "urn:ngsi-ld:EntityType:location:identifier",
  "type": "EntityType",
  "attribute1": {
    "type": "Property|Relationship|GeoProperty",
    "value": <value>
  }
}
```

### Tipos de Atributos

- **Property**: Valor simple con tipo de dato
- **Relationship**: Referencia a otra entidad (URN)
- **GeoProperty**: Dato geográfico (GeoJSON Point)

---

## Integración con Orion

### Provisión de Entidades

```bash
# Crear una farola
POST http://localhost:8000/ngsi-ld/v1/entities
{
  "id": "urn:ngsi-ld:Streetlight:coruña:SL-001",
  "type": "Streetlight",
  ...
}

# Actualizar estado de una farola
PATCH http://localhost:8000/ngsi-ld/v1/entities/urn:ngsi-ld:Streetlight:coruña:SL-001/attrs/status
{
  "type": "Property",
  "value": "off"
}

# Consultar farolas en una zona
GET http://localhost:8000/ngsi-ld/v1/entities?type=Streetlight&georel=near;maxDistance:1000&geometry=Point&coordinates=[-8.3890,43.3790]
```

### Series Temporales con QuantumLeap

Las entidades se sincronizan automáticamente con QuantumLeap para históricos:

```bash
# Consultar histórico de consumo
GET http://localhost:8668/v2/entities/urn:ngsi-ld:Streetlight:coruña:SL-001/attrs/powerConsumption
```

---

## Archivos del Proyecto

- `fiware_data_models.py`: Definición de clases FIWARE (NGSI-LD)
- `generate_fiware_entities.py`: Generador de entidades
- `fiware_entities.json`: Datos generados (para importación manual)
- `mock_orion.py`: Simulador Orion + QuantumLeap
- `provision_entities.py`: Script de provisión automática
- `index.html`: Dashboard que consume datos FIWARE

---

## Próximos Pasos

1. ✅ Definir modelos FIWARE NGSI-LD
2. ✅ Generar entidades compatibles
3. ⏳ Integrar con Orion Context Broker real
4. ⏳ Configurar QuantumLeap para series temporales
5. ⏳ Implementar API REST para consultas
6. ⏳ Dashboard en tiempo real con WebSockets

---

**Versión**: 1.0
**Última actualización**: 2026-05-04
**Estado**: MVP Funcional con datos simulados FIWARE-compatibles
