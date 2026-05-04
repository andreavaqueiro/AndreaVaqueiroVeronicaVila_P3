# Data Model - Eco-Dimming

## 1. Introducción y Enfoque NGSI-LD

Este proyecto adopta NGSI-LD como modelo de información base del Context Broker para representar contexto urbano como un grafo semántico interoperable.

Motivación técnica:
- Linked Data nativo: cada entidad tiene un identificador global y relaciones explícitas.
- Separación formal entre Property y Relationship:
  - Property: valores de estado, configuración o métricas.
  - Relationship: enlaces entre entidades mediante object con URNs del tipo urn:ngsi-ld:...
- Interoperabilidad: alineación directa con Smart Data Models oficiales para reutilización y portabilidad entre plataformas FIWARE.
- Trazabilidad contextual: permite navegar dependencias entre sensores, grupos de farolas, cuadros eléctricos y alertas transversales.

## 2. Diagrama Lógico de Relaciones

Relación lógica principal en el sistema:

CrowdFlowObserved -> apunta a -> Device -> controla/monitoriza -> StreetlightGroup -> engloba -> Streetlight

Relaciones de infraestructura y contexto extendido:
- Streetlight -> pertenece a -> StreetlightGroup
- StreetlightGroup -> depende de -> StreetlightControlCabinet
- CrowdFlowObserved -> generado por -> Device
- WeatherAlert -> afecta a -> StreetlightGroup y Streetlight (vía motor de reglas)

Interpretación operativa:
- El flujo peatonal llega como telemetría al Device.
- El Device actualiza CrowdFlowObserved en el broker.
- El motor de decisión consume ese contexto y actúa sobre StreetlightGroup/Streetlight.
- StreetlightControlCabinet aporta estado eléctrico y consumo agregado para operación y mantenimiento.
- WeatherAlert introduce una dimensión transversal de emergencia para priorizar seguridad sobre ahorro.

## 3. Diccionario de Entidades (Smart Data Models)

Nota de modelado:
- Los nombres de entidades, atributos y relaciones siguen Smart Data Models FIWARE.
- Todos los campos de valor se modelan como Property.
- Todas las referencias entre entidades se modelan como Relationship con object = URN NGSI-LD.

### 3.1 Dominio Streetlighting

#### 3.1.1 Entidad: Streetlight
Tipo: Streetlight

Atributos clave:
- location (GeoProperty)
- status (Property)
- illuminanceLevel (Property)
- refStreetlightGroup (Relationship)

Atributos estáticos vs dinámicos:

| Atributo | Tipo NGSI-LD | Tipo de dato | Clasificación | Justificación |
|---|---|---|---|---|
| location | GeoProperty | GeoJSON Point | Estático | Ubicación física de la farola, definida en alta y rara vez cambia. |
| refStreetlightGroup | Relationship | URN entidad | Estático | Vinculación estructural de la farola a su grupo de control. |
| status | Property | Text | Dinámico | Estado operativo actualizado por lógica de control o mantenimiento. |
| illuminanceLevel | Property | Number (0-100) | Dinámico | Nivel de intensidad regulado continuamente por reglas adaptativas. |

#### 3.1.2 Entidad: StreetlightGroup
Tipo: StreetlightGroup

Atributos clave:
- powerState (Property)
- refStreetlightControlCabinet (Relationship)

Atributos estáticos vs dinámicos:

| Atributo | Tipo NGSI-LD | Tipo de dato | Clasificación | Justificación |
|---|---|---|---|---|
| refStreetlightControlCabinet | Relationship | URN entidad | Estático | Relación topológica estable entre grupo y cuadro eléctrico. |
| powerState | Property | Text/Number | Dinámico | Estado energético del grupo ajustado por políticas de operación. |

#### 3.1.3 Entidad: StreetlightControlCabinet
Tipo: StreetlightControlCabinet

Atributos clave:
- brandName (Property)
- energyConsumed (Property)
- workingMode (Property)

Atributos estáticos vs dinámicos:

| Atributo | Tipo NGSI-LD | Tipo de dato | Clasificación | Justificación |
|---|---|---|---|---|
| brandName | Property | Text | Estático | Dato de inventario del fabricante del cuadro. |
| energyConsumed | Property | Number (kWh) | Dinámico | Métrica operativa acumulada/intervalar actualizada por telemetría. |
| workingMode | Property | Text | Dinámico | Modo de operación vigente (normal, ahorro, emergencia, etc.). |

### 3.2 Dominio Transversal / Sensoring

#### 3.2.1 Entidad: CrowdFlowObserved
Tipo: CrowdFlowObserved

Atributos clave:
- peopleCount (Property)
- occupancy (Property)
- refDevice (Relationship)

Atributos estáticos vs dinámicos:

| Atributo | Tipo NGSI-LD | Tipo de dato | Clasificación | Justificación |
|---|---|---|---|---|
| refDevice | Relationship | URN entidad | Estático | El origen de medición suele ser un sensor concreto asociado al punto. |
| peopleCount | Property | Integer | Dinámico | Conteo de personas recibido en cada ciclo de observación. |
| occupancy | Property | Number (0..1 o %) | Dinámico | Tasa de ocupación derivada o enviada por sensor/edge. |

#### 3.2.2 Entidad transversal: Device (Agente IoT)
Tipo: Device

Rol en la arquitectura:
- Modelo transversal para representar el sensor físico o pasarela IoT que origina observaciones.
- Permite desacoplar la observación contextual (CrowdFlowObserved) del activo hardware.

Atributos clave:
- category (Property)
- batteryLevel (Property)
- controlledAsset (Relationship)

Atributos estáticos vs dinámicos:

| Atributo | Tipo NGSI-LD | Tipo de dato | Clasificación | Justificación |
|---|---|---|---|---|
| category | Property | Array/Text | Estático | Clasificación funcional del dispositivo (camera, counter, gateway, etc.). |
| controlledAsset | Relationship | URN entidad | Estático | Activo urbano al que está asociado (por ejemplo un StreetlightGroup). |
| batteryLevel | Property | Number (%) | Dinámico | Estado energético del sensor, actualizado por telemetría IoT. |

Justificación de uso transversal:
- Homogeneiza gestión de dispositivos entre dominios.
- Facilita mantenimiento predictivo y calidad de dato (batería baja, dispositivo degradado).
- Aporta trazabilidad desde la medición hasta el activo urbano controlado.

#### 3.2.3 Entidad transversal: WeatherAlert
Tipo: WeatherAlert

Rol en la arquitectura:
- Modelo transversal de contexto externo para incorporar condiciones meteorológicas adversas en la lógica de iluminación.

Atributos clave:
- alertCategory (Property)
- severity (Property)

Atributos estáticos vs dinámicos:

| Atributo | Tipo NGSI-LD | Tipo de dato | Clasificación | Justificación |
|---|---|---|---|---|
| alertCategory | Property | Text | Dinámico | Tipo de alerta activa (rain, wind, storm, fog, etc.). |
| severity | Property | Integer/Text | Dinámico | Severidad de la alerta, variable según evolución meteorológica. |

Justificación de uso transversal:
- Permite políticas de seguridad context-aware: con alta severidad, priorizar iluminación al 100%.
- Mejora robustez del sistema ante emergencias, incluso con baja densidad peatonal.

## 4. Estrategia de Actualización de Atributos

Canales de ingesta y actualización:
- IoT Agent recibe telemetría por MQTT/HTTP y la traduce a operaciones NGSI-LD.
- Nota técnica: Para mantener la compatibilidad nativa con NGSI-LD, se utilizará un IoT Agent for JSON (o MQTT) configurado explícitamente en modo NGSI-LD (NGSI-LD payload mapping), evitando así la necesidad de traductores intermedios desde NGSIv2.
- Atributos dinámicos se actualizan mediante PATCH parcial sobre entidades existentes.
- Atributos estáticos se establecen en alta y solo cambian en procesos de inventario/reconfiguración.

Patrón recomendado:
- Telemetría frecuente: peopleCount, occupancy, batteryLevel, status, illuminanceLevel, powerState, energyConsumed.
- Topología estable: refStreetlightGroup, refStreetlightControlCabinet, refDevice, controlledAsset, location.

## 5. Ejemplo de Payload NGSI-LD

Ejemplo válido de creación de entidad Streetlight (POST /ngsi-ld/v1/entities):

```json
{
  "id": "urn:ngsi-ld:Streetlight:ACOR-PLZ-MARIA-PITA-001",
  "type": "Streetlight",
  "location": {
    "type": "GeoProperty",
    "value": {
      "type": "Point",
      "coordinates": [
        -8.395942,
        43.371265
      ]
    }
  },
  "status": {
    "type": "Property",
    "value": "ok"
  },
  "illuminanceLevel": {
    "type": "Property",
    "value": 20,
    "unitCode": "P1"
  },
  "refStreetlightGroup": {
    "type": "Relationship",
    "object": "urn:ngsi-ld:StreetlightGroup:ACOR-CENTRO-G01"
  },
  "@context": [
    "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
    "https://raw.githubusercontent.com/smart-data-models/dataModel.Streetlighting/master/context.jsonld"
  ]
}
```

## 6. Convenciones de Identificación y Calidad de Datos

Convenciones recomendadas de URN:
- Streetlight: urn:ngsi-ld:Streetlight:<zona>-<id>
- StreetlightGroup: urn:ngsi-ld:StreetlightGroup:<zona>-<grupo>
- StreetlightControlCabinet: urn:ngsi-ld:StreetlightControlCabinet:<zona>-<cabinet>
- Device: urn:ngsi-ld:Device:<zona>-<sensor>
- CrowdFlowObserved: urn:ngsi-ld:CrowdFlowObserved:<zona>-<sensor>-<timestamp>
- WeatherAlert: urn:ngsi-ld:WeatherAlert:<ambito>-<evento>-<timestamp>

Criterios mínimos de calidad:
- Todas las relaciones deben resolver a URNs existentes en el broker.
- Toda entidad geográfica debe incluir location en formato GeoProperty válido.
- Las actualizaciones dinámicas deben incluir timestamp operativo para trazabilidad temporal.

## 7. Referencias Técnicas
- NGSI-LD Core: https://uri.etsi.org/ngsi-ld/
- Smart Data Models: https://smartdatamodels.org/
- Streetlight: https://smartdatamodels.org/dataModel.Streetlighting/Streetlight
- StreetlightGroup: https://smartdatamodels.org/dataModel.Streetlighting/StreetlightGroup
- StreetlightControlCabinet: https://smartdatamodels.org/dataModel.Streetlighting/StreetlightControlCabinet
- CrowdFlowObserved: https://smartdatamodels.org/dataModel.CrowdFlowObserved/CrowdFlowObserved
- Device: https://smartdatamodels.org/dataModel.Device/Device
- WeatherAlert: https://smartdatamodels.org/dataModel.Weather/WeatherAlert
