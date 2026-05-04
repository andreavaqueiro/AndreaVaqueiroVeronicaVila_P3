# PRD - Eco-Dimming

## 1. Información del Documento
- **Proyecto:** Eco-Dimming
- **Asignatura:** Gestión de Datos en Entornos Inteligentes
- **Ámbito geográfico:** Ciudad de A Coruña
- **Versión:** 1.0
- **Fecha:** 21/04/2026
- **Tipo de sistema:** Aplicación web de iluminación urbana inteligente basada en FIWARE (NGSI-LD)

## 2. Visión General y Objetivo

### 2.1 Resumen del sistema
**Eco-Dimming** es una aplicación web de gestión de alumbrado urbano que combina:
- visualización geoespacial en tiempo real,
- monitorización de infraestructura de iluminación,
- reglas de iluminación adaptativa según densidad peatonal,
- y un asistente conversacional para soporte a operaciones urbanas.

La solución se despliega sobre un mapa interactivo de A Coruña y utiliza datos contextuales NGSI-LD para coordinar el comportamiento de farolas individuales y grupos de farolas.

### 2.2 Objetivo de negocio y de producto
El objetivo principal es **equilibrar seguridad ciudadana y eficiencia energética**, reduciendo consumo en zonas con baja actividad peatonal y elevando automáticamente la iluminación en zonas de alta afluencia.

Objetivos específicos:
- Reducir el consumo energético total del alumbrado mediante regulación dinámica de intensidad.
- Incrementar la percepción y condiciones de seguridad en rutas peatonales activas.
- Mejorar la capacidad de decisión operativa del personal municipal mediante analítica y asistente IA.

## 3. Alcance del Producto

### 3.1 Incluido en alcance
- Mapa urbano de A Coruña con capas de infraestructura y calor peatonal.
- Gestión de entidades FIWARE NGSI-LD: farolas, grupos, cuadros eléctricos y flujo de personas.
- Motor de reglas para modo ahorro y modo seguridad (100%).
- Chat de gestión urbana basado en Gemini para consultas sobre estado y consumo.
- Persistencia histórica de datos para análisis temporal.

### 3.2 Fuera de alcance (esta práctica)
- Integración con hardware real de alumbrado (se simula vía IoT Agent).
- Optimización predictiva avanzada basada en ML entrenado con series históricas.
- Integración con sistemas corporativos municipales externos (ERP/GMAO).

## 4. Stakeholders y Usuarios
- **Administrador urbano:** monitoriza operación, consulta incidencias y consumos.
- **Operador técnico de alumbrado:** supervisa cuadros eléctricos y estados de farolas.
- **Ciudadanía (beneficiaria indirecta):** recibe mejora de seguridad y calidad del servicio.
- **Equipo académico/proyecto:** implementa, valida y documenta la práctica.

## 5. Requerimientos Funcionales (User Stories)

### FR1. Visualización Geoespacial Avanzada
**Como** administrador urbano, **quiero** visualizar en un mapa de A Coruña la infraestructura de alumbrado y la densidad peatonal en tiempo real, **para** comprender el estado operacional por zonas.

#### Criterios funcionales
- El frontend muestra un mapa interactivo centrado en A Coruña (Leaflet + OpenStreetMap).
- Se habilitan dos capas principales:
  - **Capa de Infraestructura:** marcadores de entidades `Streetlight`.
  - **Capa de Calor (Heatmap):** superposición basada en entidades `CrowdFlowObserved`.
- El usuario puede activar/desactivar capas y consultar metadatos básicos por entidad.

#### Criterios de aceptación
- El mapa carga con coordenadas iniciales de A Coruña.
- Las farolas se renderizan con estado visible (operativa/avería/apagada).
- El heatmap se actualiza de forma periódica con datos de densidad peatonal.

### FR2. Iluminación Adaptativa (Safety Path)
**Como** sistema de control, **quiero** ajustar automáticamente la intensidad de farolas según densidad peatonal, **para** minimizar consumo manteniendo seguridad.

#### Lógica de negocio
- En zonas frías (baja densidad), farolas en modo ahorro entre **10% y 20%**.
- En zonas calientes (alta densidad), actualización dinámica de `Streetlight` y `StreetlightGroup` a **100%** de intensidad.
- Los cambios de estado/intensidad se publican en Orion Context Broker (NGSI-LD) para mantener consistencia contextual.

#### Criterios de aceptación
- Detección de alta densidad en un área provoca incremento de intensidad en las farolas afectadas.
- Al disminuir la densidad, el sistema retorna gradualmente a modo ahorro.
- El estado aplicado queda trazable en histórico (QuantumLeap + CrateDB).

### FR3. Asistente IA de Gestión (Gemini City-GPT)
**Como** administrador urbano, **quiero** consultar un asistente conversacional sobre estado y consumo del alumbrado, **para** obtener diagnósticos y resúmenes operativos rápidamente.

#### Capacidades mínimas
- Chat en Python integrado con API de Google Gemini (`google-generativeai`).
- El asistente puede invocar consultas HTTP al Context Broker para:
  - localizar farolas defectuosas,
  - identificar zonas más iluminadas,
  - resumir consumo energético por periodo.
- Respuestas en lenguaje natural con trazabilidad a entidades/zonas consultadas.

#### Criterios de aceptación
- Ante la pregunta sobre farolas defectuosas, devuelve listado por zona y estado.
- Ante pregunta de zonas más iluminadas, devuelve ranking por intensidad/media temporal.
- Ante pregunta de consumo nocturno, genera resumen entendible para operación.

### FR4. Monitoreo de Infraestructura
**Como** operador técnico, **quiero** supervisar cuadros eléctricos y su relación con grupos de farolas, **para** detectar fallos de infraestructura y priorizar mantenimiento.

#### Criterios funcionales
- Gestión de estado de `StreetlightControlCabinet`.
- Relación visible entre cuadros y grupos (`StreetlightGroup`).
- Visualización de incidencias por cuadro y su impacto en farolas asociadas.

#### Criterios de aceptación
- Se puede consultar el estado de cada cuadro eléctrico.
- Se puede identificar qué grupos/farolas dependen de un cuadro concreto.
- Se refleja en UI cualquier anomalía reportada por infraestructura.

## 6. Arquitectura y Stack Tecnológico

### 6.1 Arquitectura lógica
1. **Captura/simulación IoT:** sensores de personas y actuadores de alumbrado simulados mediante IoT Agent.
2. **Gestión de contexto:** Orion Context Broker en modo NGSI-LD como núcleo de datos de contexto.
3. **Reglas de control:** servicio backend que evalúa densidad peatonal y actualiza intensidad/estado.
4. **Persistencia histórica:** QuantumLeap suscrito al broker y almacenamiento en CrateDB.
5. **Interfaz web:** cliente HTML/JS con Leaflet (mapa + heatmap) y Chart.js para series de consumo.
6. **Asistente IA:** servicio Python con Gemini que combina LLM + consultas al contexto FIWARE.

### 6.2 Stack tecnológico
- **Backend/Data:** FIWARE Orion Context Broker (NGSI-LD), IoT Agent.
- **Históricos:** QuantumLeap + CrateDB.
- **IA:** Python + `google-generativeai` (Gemini API) + cliente HTTP NGSI-LD.
- **Frontend:** HTML, JavaScript, Leaflet.js (+ plugin heatmap), Chart.js.

## 7. Smart Data Models FIWARE (NGSI-LD)

Los siguientes modelos se usarán como base semántica y de interoperabilidad, alineados con Smart Data Models oficiales FIWARE:

### 7.1 Streetlight ([ref:streetlight])
- **Entidad:** `Streetlight`
- **Atributos clave:**
  - `status` (estado operativo)
  - `illuminance` (nivel de iluminación/intensidad)
  - `location` (geometría geoespacial)
  - `refStreetlightGroup` (relación con grupo de farolas)
- **Uso en el sistema:** representa cada farola individual del mapa de infraestructura.

### 7.2 StreetlightGroup ([ref:streetlight-group])
- **Entidad:** `StreetlightGroup`
- **Atributos clave:**
  - `powerState` (estado de energía del grupo)
  - `refStreetlightControlCabinet` (relación al cuadro eléctrico)
- **Uso en el sistema:** permite acciones agregadas sobre un conjunto de farolas (encendido/regulación por zona).

### 7.3 CrowdFlowObserved ([ref:crowd-flow-observed])
- **Entidad:** `CrowdFlowObserved`
- **Atributos clave:**
  - `peopleCount` (conteo de personas)
  - `location` (ubicación de observación)
  - `refDevice` (dispositivo/sensor origen)
- **Uso en el sistema:** alimenta el heatmap y activa reglas de iluminación adaptativa.

### 7.4 Interacción mediante Linked Data (NGSI-LD)
El sistema conecta entidades mediante relaciones semánticas (`Relationship`) para mantener trazabilidad de decisiones:
- `CrowdFlowObserved` aporta contexto de afluencia por ubicación.
- El motor de reglas mapea zonas calientes con farolas y grupos cercanos.
- Se actualizan propiedades de `Streetlight` y `StreetlightGroup`.
- `StreetlightGroup` mantiene enlace estructural a `StreetlightControlCabinet` para diagnóstico de infraestructura.

Este enfoque de Linked Data permite que las consultas del asistente IA y los paneles visuales operen sobre un grafo contextual coherente.

## 8. Caso de Uso Principal (Flujo Paso a Paso)

### Caso: incremento de afluencia en una plaza de A Coruña
1. Un grupo de personas entra en una plaza y los sensores reportan nuevos valores de afluencia.
2. El IoT Agent transforma la telemetría en actualizaciones NGSI-LD de `CrowdFlowObserved`.
3. Orion Context Broker recibe y publica el nuevo contexto.
4. El frontend consulta/consume estos cambios y actualiza el heatmap en tiempo real.
5. El motor de reglas detecta que la celda/zona supera el umbral de densidad.
6. Se identifican las `Streetlight` y `StreetlightGroup` de influencia geográfica.
7. Se ejecutan updates NGSI-LD elevando la intensidad a 100% en esa zona.
8. QuantumLeap registra los cambios y los persiste en CrateDB para análisis posterior.
9. Horas después, un administrador pregunta a Gemini: “¿Cuál fue el consumo de esta noche y qué zonas estuvieron más iluminadas?”.
10. El asistente Python consulta contexto actual + históricos, agrega resultados y devuelve un resumen operativo en lenguaje natural.

## 9. Requerimientos No Funcionales
- **Rendimiento:** actualización de visualización y reglas en intervalos casi en tiempo real.
- **Escalabilidad:** soporte para aumentar número de farolas/sensores sin rediseño de modelo.
- **Interoperabilidad:** uso estricto de NGSI-LD y Smart Data Models oficiales.
- **Trazabilidad:** persistencia histórica para auditoría y análisis.
- **Usabilidad:** panel cartográfico claro para operación urbana.

## 10. KPI de Éxito
- Reducción porcentual de consumo respecto a operación sin regulación dinámica.
- Tiempo medio de reacción ante cambios de densidad peatonal.
- Porcentaje de cobertura de zonas activas correctamente iluminadas al 100%.
- Tiempo de respuesta del asistente para consultas operativas.
- Número de incidencias de infraestructura detectadas y clasificadas.

## 11. Riesgos y Mitigaciones
- **Ruido en datos de afluencia:** aplicar suavizado temporal y umbrales con histéresis.
- **Sobreactuación lumínica por picos puntuales:** ventanas de confirmación antes de subir/bajar intensidad.
- **Dependencia de API externa (Gemini):** fallback a consultas predefinidas si falla servicio IA.
- **Inconsistencia entre tiempo real e histórico:** monitorizar suscripciones y latencia de QuantumLeap.

## 12. Referencias (refs)
- [ref:ngsi-ld]: https://uri.etsi.org/ngsi-ld/
- [ref:fiware-data-models]: https://smartdatamodels.org/
- [ref:streetlight]: https://smartdatamodels.org/dataModel.Streetlighting/Streetlight
- [ref:streetlight-group]: https://smartdatamodels.org/dataModel.Streetlighting/StreetlightGroup
- [ref:crowd-flow-observed]: https://smartdatamodels.org/dataModel.CrowdFlowObserved/CrowdFlowObserved
- [ref:streetlight-control-cabinet]: https://smartdatamodels.org/dataModel.Streetlighting/StreetlightControlCabinet
- [ref:orion-ld]: https://fiware-orion.readthedocs.io/en/master/user/ngsild_implementation_notes/index.html
- [ref:quantumleap]: https://quantumleap.readthedocs.io/
- [ref:cratedb]: https://cratedb.com/docs/

## 13. Trazabilidad de modelos en requisitos
- FR1 usa `Streetlight` + `CrowdFlowObserved` para mapa de infraestructura y heatmap.
- FR2 usa `CrowdFlowObserved` como señal y actualiza `Streetlight`/`StreetlightGroup`.
- FR3 consulta `Streetlight`, `StreetlightGroup`, `StreetlightControlCabinet` e históricos de consumo.
- FR4 monitoriza `StreetlightControlCabinet` y relaciones con `StreetlightGroup`.

Conforme a FIWARE, las entidades y relaciones anteriores deben implementarse como recursos NGSI-LD interoperables y semánticamente alineados con [Smart Data Models][ref:fiware-data-models].
