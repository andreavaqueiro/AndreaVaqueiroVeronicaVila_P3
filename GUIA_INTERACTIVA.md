# 🗺️ Guía Interactiva - Exploración del Mapa

## Comenzar Ahora

Abre en tu navegador:
```
http://localhost:3000
```

---

## 🎯 Qué Verás

### 1. **Mapa Principal (600px de altura)**
   - Centrado en Plaza María Pita, A Coruña (43.3712°N, 8.3959°O)
   - OpenStreetMap como base
   - Zoom nivel 15 (vista de barrio)

### 2. **40 Farolas como Marcadores**
   Distribuidas en un área de ~500m x 500m:
   - 🟡 **Amarillas/Naranja/Rojas**: Encendidas (intensidad variable)
   - ⚫ **Grises**: Apagadas (0% intensidad)
   - 🔴 **Rojas con ⚠️**: Averiadas (requieren mantenimiento)

### 3. **Leyenda Visual (bajo el mapa)**
   Explica qué significa cada color

---

## 🖱️ Acciones Interactivas

### Hacer Clic en una Farola
Se abrirá un popup con:

```
┌──────────────────────────────────────────┐
│ ACOR-SL-001                              │ ← Identificador
├──────────────────────────────────────────┤
│ Estado: 🟢 ENCENDIDA                     │ ← Color del estado
│                                           │
│ Intensidad: 85%   │   Consumo: 63.75W   │ ← Métricas clave
│                                           │
│ Ubicación:                                │
│ 43.370234°N                               │
│ -8.396542°O                               │
│                                           │
│ Última actualización:                     │
│ 2026-04-29T14:25:30Z                     │
└──────────────────────────────────────────┘
```

### Zoom y Navegación
- **Rueda del mouse**: Zoom in/out
- **Arrastra**: Mover mapa
- **Doble clic**: Zoom in automático

---

## 📊 Cambios en Tiempo Real

Cada 10 segundos:
- Dashboard se actualiza automáticamente
- Farolas cambian de color según nueva intensidad
- Métricas se recalculan

Cada 3 segundos (simulador):
- Estados de farolas cambian
- Densidad de peatones varía (0-50)
- Intensidad se ajusta a demanda

---

## 📈 Gráficos (Abajo en el Panel)

### Consumo Energético
- Gráfico de líneas
- Últimas 6 horas
- Eje Y: kWh
- Tendencia general: Mayor consumo = Más peatones

### Flujo Peatonal
- Gráfico de barras
- Últimas 6 horas
- Eje Y: Número de personas
- Picos correlacionados con intensidad

---

## 🔍 Ejemplos de Exploración

### Ejemplo 1: Encontrar Farolas Averiadas
1. Busca íconos ⚠️ en rojo brillante
2. Haz clic para ver más detalles
3. Revisa "Estado: 🔴 AVERIADA"

### Ejemplo 2: Comparar Consumo
1. Haz clic en farola encendida al 100%
2. Anota consumo (e.g., 75W)
3. Haz clic en farola al 20%
4. Compara consumo (e.g., 15W)

### Ejemplo 3: Detectar Anomalías
1. Espera cambio de densidad de peatones
2. Observa que intensidad de farolas cambia
3. Si ve farola encendida al 100% sin peatones → Anomalía

---

## 💡 Datos Mostrados por Farola

```javascript
{
  "id": "urn:ngsi-ld:Streetlight:ACOR-SL-001",
  "status": "on" / "off" / "fault",
  "illuminanceLevel": 0-100 (porcentaje),
  "powerConsumption": watts,
  "location": {
    "latitude": grados,
    "longitude": grados
  },
  "lastUpdate": ISO 8601 timestamp
}
```

---

## 🎨 Código de Colores

### Intensidad de Farola Encendida
- 🔴 **Rojo intenso**: 80-100% (máxima luminosidad)
- 🟠 **Naranja**: 40-79% (media)
- 🟡 **Amarillo**: 1-39% (mínima)

### Estados
- 🟢 Verde: ON (encendida)
- ⚫ Gris: OFF (apagada)
- 🔴 Rojo: FAULT (averiada)

---

## 📱 Paneles Informativos (Lado Derecho)

### Panel 1: Estado General
- **Farolas Activas**: Total de farolas (40 en este caso)
- **Peatones Detectados**: Suma de todos los sensores
- **Consumo (kWh)**: Total del cuadro de control
- **Anomalías**: Conteo de eventos sospechosos

### Panel 2: Recomendación de Intensidad
- Basada en densidad de peatones
- Razón de la recomendación
- Botón para aplicar

### Panel 3 & 4: Gráficos
- Histórico de consumo
- Histórico de peatones

---

## 🔄 Auto-Refresco

- Dashboard: Cada 10 segundos
- Mapas: Se limpian y se redibujan
- Popups: Se cierran al actualizar

**Consejo**: Deja abierto el dashboard y observa los cambios automáticos

---

## ⚙️ Ajustes (si fuera necesario)

### Cambiar Velocidad de Simulación
```bash
ORION_BASE_URL="http://localhost:8000" \
SIM_SLEEP_SECONDS=1 \
python3 simulate_streetlights.py
```

### Cambiar Número de Iteraciones
```bash
SIM_ITERATIONS=50 python3 simulate_streetlights.py
```

---

## 🛠️ Troubleshooting

### Mapa no carga
- Verifica que http://localhost:3000 es accesible
- Revisa consola del navegador (F12)

### Popups vacíos
- Espera a que cargue la farola
- Recarga la página (F5)

### Gráficos no actualizan
- Verifica simulador activo
- Recarga página (F5)

### Farolas no visibles
- Aumenta zoom con rueda del mouse
- Comprueba que Mock Orion en 8000 está activo

---

## 📞 Comandos Útiles

```bash
# Ver todas las farolas en JSON
curl http://localhost:8000/ngsi-ld/v1/entities?type=Streetlight | jq

# Ver solo IDs y estados
curl http://localhost:8000/ngsi-ld/v1/entities?type=Streetlight | \
  jq '.[] | {id, status: .status.value, intensity: .illuminanceLevel.value}'

# Monitorear cambios en tiempo real
watch -n 5 'curl -s http://localhost:8000/ngsi-ld/v1/entities?type=Streetlight | jq ".[0] | {id, status: .status.value}"'

# Ver flujo de peatones
curl http://localhost:8000/ngsi-ld/v1/entities?type=CrowdFlowObserved | jq '.[] | {id, peopleCount: .peopleCount.value}'
```

---

## 🎬 Escenario de Demostración Recomendado

1. **Minuto 0-1**: Abre dashboard, observa mapa
2. **Minuto 1-2**: Haz clic en 3-4 farolas diferentes
3. **Minuto 2-3**: Anota intensidades de 2 farolas
4. **Minuto 3-4**: Espera 10 segundos (actualización automática)
5. **Minuto 4-5**: Compara nuevas intensidades
6. **Minuto 5-6**: Revisa gráficos de consumo y peatones
7. **Minuto 6-7**: Busca farolas averiadas
8. **Minuto 7-8**: Observa cambios de color/estado

**Resultado**: Demostración clara de visualización y datos en tiempo real

---

**🎉 ¡Disfruta explorando el MVP Eco-Dimming!**

*Última actualización: 29 Abril 2026*
