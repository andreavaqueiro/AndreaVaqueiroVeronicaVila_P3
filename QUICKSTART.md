# ⚡ Quick Start - MVP Funcional

**Tiempo**: 5 minutos para verlo funcionando

---

## 📋 Requisitos

- Python 3.12+
- 3 terminales abiertas
- Navegador web

---

## 🚀 Ejecutar en 3 Pasos

### Paso 1: Terminal 1 - Mock Orion (Puerto 8000)

```bash
cd /home/andrea/XDEI/AndreaVaqueiro_VeronicaVila_P3
source venv/bin/activate
python mock_orion.py
```

Verás:
```
✅ Cargadas 94 entidades FIWARE NGSI-LD
📊 Distribución de entidades:
   - Streetlight: 68
   ...
```

### Paso 2: Terminal 2 - Web Server (Puerto 3000)

```bash
cd /home/andrea/XDEI/AndreaVaqueiro_VeronicaVila_P3
source venv/bin/activate
python web_server.py
```

Verás:
```
🌐 Servidor Web iniciado en http://localhost:3000
```

### Paso 3: Abrir Dashboard en Navegador

```
http://localhost:3000
```

¡Listo! 🎉 Dashboard con:
- 68 farolas en mapa de A Coruña
- Heatmap de actividad urbana (click en botón "🔥 Heatmap")
- Estadísticas en tiempo real

---

## 🎮 Interactuar con Dashboard

1. **Ver Farolas**
   - 💡 Amarillo = ON
   - ⚫ Gris = OFF
   - ⚠️ Rojo = FAULT

2. **Activar Heatmap**
   - Click en botón "🔥 Heatmap: OFF" (arriba derecha)
   - Verás colores (🔵 azul = baja actividad, 🔴 rojo = alta)

3. **Ver Estadísticas**
   - Estado General (panel izquierdo)
   - Gráficos de energía y peatones

---

## 📡 APIs FIWARE (Curl Tests)

```bash
# Test 1: Ver 68 farolas
curl -s "http://localhost:8000/ngsi-ld/v1/entities?type=Streetlight" | jq 'length'

# Test 2: Ver datos adaptados
curl -s "http://localhost:3000/api/streetlights/fiware" | jq '.stats'

# Test 3: Ver flujos peatonales
curl -s "http://localhost:3000/api/crowd-flows/fiware" | jq '.[] | {id, peopleCount}'
```

---

## 🛑 Detener Sistema

En cada terminal:
```
CTRL+C
```

---

## 📚 Documentación Completa

- **[FIWARE_READY.md](FIWARE_READY.md)** - Estado del sistema & arquitectura
- **[README_FIWARE.md](README_FIWARE.md)** - Manual completo
- **[FIWARE_INTEGRATION.md](FIWARE_INTEGRATION.md)** - Guía técnica
- **[FIWARE_DATA_MODEL.md](FIWARE_DATA_MODEL.md)** - Especificación de datos

---

## ✨ Qué Incluye

✅ 94 entidades FIWARE NGSI-LD  
✅ 68 farolas con datos realistas  
✅ 6 zonas de A Coruña  
✅ Heatmap interactivo  
✅ Estadísticas automáticas  
✅ Simulación en tiempo real  
✅ APIs REST FIWARE  
✅ Consumo energético calculado  

---

¡Disfruta! 🚀
