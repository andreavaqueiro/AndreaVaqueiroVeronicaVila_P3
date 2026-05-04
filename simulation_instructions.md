# Ejecución de Scripts de Datos de Prueba (Eco-Dimming)

## 1. Requisitos
- Python 3.10+
- Orion Context Broker NGSI-LD accesible (ejemplo local: http://localhost:1026)
- Suscripción activa Orion -> QuantumLeap para capturar históricos

## 2. Instalación de dependencias
```bash
pip install -r requirements.txt
```

## 3. Configuración de Orion
Ambos scripts usan la variable de entorno `ORION_BASE_URL`.

Ejemplo Linux/macOS:
```bash
export ORION_BASE_URL="http://localhost:1026"
```

Si no se define, el valor por defecto es `http://localhost:1026`.

## 4. Orden de ejecución
1. Provisionar entidades base (estado actual/estático):
```bash
python provision_entities.py
```

2. Simular histórico nocturno (20 iteraciones, 1 segundo por iteración):
```bash
python simulate_history.py
```

## 5. Parámetros opcionales de simulación
Puedes ajustar iteraciones y frecuencia sin editar código:

```bash
export SIM_ITERATIONS=20
export SIM_SLEEP_SECONDS=1
python simulate_history.py
```

## 6. Resultado esperado
- Orion contiene la topología base: cabinet, grupos, farolas, devices y crowd flows.
- Durante la simulación se generan PATCH de atributos dinámicos:
  - `energyConsumed` ascendente en `StreetlightControlCabinet`
  - `peopleCount` y `occupancy` en `CrowdFlowObserved`
  - `illuminanceLevel` y `status` en `Streetlight`
- QuantumLeap registra automáticamente el histórico al recibir notificaciones de Orion.
