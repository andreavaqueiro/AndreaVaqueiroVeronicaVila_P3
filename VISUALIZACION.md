# 🌍 MVP Eco-Dimming - Visualización en Vivo

## Estado Actual

✅ **Servicios Activos:**
- Mock Orion API (puerto 8000)
- Web Server Dashboard (puerto 3000)
- Simulador de Farolas (ejecutándose)

✅ **Datos Disponibles:**
- 40 farolas inteligentes distribuidas en A Coruña
- 4 grupos de farolas
- 4 sensores de flujo peatonal
- Estados dinámicos: Encendida (on), Apagada (off), Averiada (fault)

---

## 📊 Acceso al Dashboard

### URL Principal
```
http://localhost:3000
```

Abre en tu navegador para ver:
- 🗺️ Mapa interactivo de A Coruña (Plaza María Pita)
- 💡 40 farolas con iconos de estado
- 📈 Gráficos de consumo energético y flujo peatonal
- ⚠️ Detector de anomalías

---

## 🎯 Características Implementadas

### 1. **Visualización de Farolas en Mapa**
- Cada farola es un marcador circular con ícono
- Colores diferenciados por estado:
  - 🟡 **ENCENDIDA** (amarillo/naranja/rojo según intensidad)
  - ⚫ **APAGADA** (gris)
  - 🔴 **AVERIADA** (rojo brillante)

### 2. **Popups Informativos Detallados**
Haz clic en cualquier farola para ver:
- **ID**: Identificador único (ACOR-SL-001, etc.)
- **Estado**: on/off/fault con color codificado
- **Intensidad**: 0-100% (lumens)
- **Consumo**: Potencia actual en Watts
- **Ubicación**: Coordenadas GPS exactas (lat/lon)
- **Última Actualización**: Timestamp en ISO 8601

### 3. **Sistema de Estados**
- **Encendida (on)**: Ícono 💡, color amarillo/naranja/rojo según intensidad
- **Apagada (off)**: Ícono ⚫, color gris (0W consumo)
- **Averiada (fault)**: Ícono ⚠️, color rojo (requiere mantenimiento)

### 4. **Leyenda Visual**
Visible bajo el mapa con explicación de colores y estados

### 5. **Métricas en Tiempo Real**
Panel derecho muestra:
- Total de farolas activas
- Peatones detectados en el área
- Consumo energético total (kWh)
- Anomalías detectadas

---

## 🔄 Cambios Dinámicos (Simulador Activo)

Cada 3 segundos:
- Densidad de peatones cambia (0-50 personas)
- Intensidad de farolas se ajusta automáticamente:
  - \> 30 personas: 100% intensidad
  - 10-30 personas: 60% intensidad
  - < 10 personas: 20% (modo ahorro)
- Probabilidad de fallos aleatorios (1%)
- Estados pueden cambiar: on → off → fault → on

**El mapa se actualiza automáticamente cada 10 segundos para reflejar los cambios.**

---

## 📋 Cómo Probar

### Opción 1: Ver Dashboard en Vivo
```bash
# Abre en navegador:
http://localhost:3000

# Haz clic en farolas para ver detalles
# Observa cómo cambian estados y colores
# Mira los gráficos actualizarse
```

### Opción 2: Consultar API Directamente
```bash
# Ver todas las farolas
curl http://localhost:8000/ngsi-ld/v1/entities?type=Streetlight | jq

# Ver una farola específica
curl http://localhost:8000/ngsi-ld/v1/entities/urn:ngsi-ld:Streetlight:ACOR-SL-001 | jq

# Ver estado de flujo peatonal
curl http://localhost:8000/ngsi-ld/v1/entities?type=CrowdFlowObserved | jq
```

### Opción 3: Monitorear Cambios en Tiempo Real
```bash
# Haz una consulta cada 5 segundos
watch -n 5 'curl -s http://localhost:8000/ngsi-ld/v1/entities?type=Streetlight | jq ".[] | {id, status: .status.value, intensity: .illuminanceLevel.value}"'
```

---

## 🛠️ Detener Servicios

```bash
# Para detener simulador (en terminal correspondiente)
Ctrl + C

# Para detener web server (en otra terminal)
Ctrl + C

# Para detener mock orion (en otra terminal)
Ctrl + C
```

---

## 📊 Datos Visualizados

### Ejemplo de Farola en JSON (NGSI-LD)
```json
{
  "id": "urn:ngsi-ld:Streetlight:ACOR-SL-001",
  "type": "Streetlight",
  "status": {
    "type": "Property",
    "value": "on"
  },
  "illuminanceLevel": {
    "type": "Property",
    "value": 85,
    "unitCode": "P1"
  },
  "powerConsumption": {
    "type": "Property",
    "value": 63.75,
    "unitCode": "W"
  },
  "location": {
    "type": "GeoProperty",
    "value": {
      "type": "Point",
      "coordinates": [-8.3959, 43.3712]
    }
  },
  "lastUpdate": {
    "type": "Property",
    "value": "2026-04-29T14:25:30Z"
  }
}
```

---

## ✨ Puntos Destacados

✅ **40 farolas** distribuidas en área urbana de ~1km²  
✅ **Estados dinámicos** que cambian cada 3 segundos  
✅ **Popups informativos** con 6 campos de datos por farola  
✅ **Iconos visuales** que distinguen claramente estados  
✅ **Mapa interactivo** con OpenStreetMap  
✅ **Auto-refresco** cada 10 segundos en dashboard  
✅ **Legendas claras** para facilitar interpretación  

---

## 🔧 Notas Técnicas

- **Backend**: Python (FastAPI/Mock Orion)
- **Frontend**: HTML5 + Leaflet.js + Chart.js
- **Datos**: NGSI-LD (formato Linked Data estándar FIWARE)
- **API**: REST con Content-Type: application/ld+json
- **Almacenamiento**: En memoria (Mock Orion)
- **Actualización**: Tiempo real con WebSocket simulado via polling

---

**Última actualización**: 29 Abril 2026  
**Versión**: MVP 1.0  
**Estado**: ✅ Producción Local
