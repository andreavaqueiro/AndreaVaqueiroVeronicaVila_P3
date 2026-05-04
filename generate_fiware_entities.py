#!/usr/bin/env python3
"""Generador de entidades FIWARE para iluminación urbana inteligente en A Coruña.

Crea entidades realistas siguiendo los Smart Data Models de FIWARE NGSI-LD.
Compatible para insertar en Orion Context Broker.
"""

from __future__ import annotations

import json
import random
from fiware_data_models import (
    Streetlight,
    StreetlightGroup,
    StreetlightControlCabinet,
    StreetlightFeeder,
    StreetlightModel,
    CrowdFlowObserved,
    TrafficFlowObserved,
    ItemFlowObserved,
    StreetlightStatus,
    PowerState,
)

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN GEOGRÁFICA - A CORUÑA
# ═══════════════════════════════════════════════════════════════════════════

CORUÑA_CENTER = (-8.3970, 43.3750)  # Centro de A Coruña (lon, lat)

# Zonas principales de A Coruña (centros aproximados)
ZONES = {
    "centro": {
        "center": (-8.3890, 43.3790),
        "description": "Centro Histórico",
        "radius": 0.003,
    },
    "ciudad_vieja": {
        "center": (-8.3750, 43.3850),
        "description": "Ciudad Vieja",
        "radius": 0.002,
    },
    "calle_real": {
        "center": (-8.4000, 43.3750),
        "description": "Calle Real y alrededores",
        "radius": 0.0025,
    },
    "paseo_maritimo": {
        "center": (-8.3600, 43.3700),
        "description": "Paseo Marítimo",
        "radius": 0.004,
    },
    "ensanche": {
        "center": (-8.4100, 43.3600),
        "description": "Ensanche",
        "radius": 0.005,
    },
    "juan_florez": {
        "center": (-8.4200, 43.3800),
        "description": "Avenida Juan Flórez",
        "radius": 0.003,
    },
}


# ═══════════════════════════════════════════════════════════════════════════
# MODELOS DE FAROLA
# ═══════════════════════════════════════════════════════════════════════════

STREETLIGHT_MODELS = [
    StreetlightModel(
        id_="urn:ngsi-ld:StreetlightModel:coruña:LED-200",
        description="Farola LED 200W - Modelo estándar",
        brand="Philips",
        model_name="StreetLite Mini",
        lamp_type="LED",
        luminous_flux=25000,
        color_temperature=4000,
        life_expectancy=50000,
    ),
    StreetlightModel(
        id_="urn:ngsi-ld:StreetlightModel:coruña:LED-150",
        description="Farola LED 150W - Modelo compacto",
        brand="Osram",
        model_name="Echelon",
        lamp_type="LED",
        luminous_flux=18000,
        color_temperature=4000,
        life_expectancy=50000,
    ),
    StreetlightModel(
        id_="urn:ngsi-ld:StreetlightModel:coruña:HPS-250",
        description="Farola HPS 250W - Modelo antiguo",
        brand="Sylvania",
        model_name="Supersonic",
        lamp_type="HPS",
        luminous_flux=25000,
        color_temperature=2700,
        life_expectancy=24000,
    ),
]


# ═══════════════════════════════════════════════════════════════════════════
# COORDINACIÓN DE ZONAS
# ═══════════════════════════════════════════════════════════════════════════

STREETLIGHT_GROUPS_CONFIG = [
    {
        "id": "urn:ngsi-ld:StreetlightGroup:coruña:grupo-centro",
        "zone": "centro",
        "description": "Grupo de farolas del Centro Histórico",
        "count": 12,
    },
    {
        "id": "urn:ngsi-ld:StreetlightGroup:coruña:grupo-ciudad-vieja",
        "zone": "ciudad_vieja",
        "description": "Grupo de farolas de Ciudad Vieja",
        "count": 12,
    },
    {
        "id": "urn:ngsi-ld:StreetlightGroup:coruña:grupo-calle-real",
        "zone": "calle_real",
        "description": "Grupo de farolas de Calle Real",
        "count": 11,
    },
    {
        "id": "urn:ngsi-ld:StreetlightGroup:coruña:grupo-paseo-maritimo",
        "zone": "paseo_maritimo",
        "description": "Grupo de farolas del Paseo Marítimo",
        "count": 10,
    },
    {
        "id": "urn:ngsi-ld:StreetlightGroup:coruña:grupo-ensanche",
        "zone": "ensanche",
        "description": "Grupo de farolas del Ensanche",
        "count": 12,
    },
    {
        "id": "urn:ngsi-ld:StreetlightGroup:coruña:grupo-juan-florez",
        "zone": "juan_florez",
        "description": "Grupo de farolas de Avenida Juan Flórez",
        "count": 11,
    },
]


# ═══════════════════════════════════════════════════════════════════════════
# FUNCIONES DE GENERACIÓN
# ═══════════════════════════════════════════════════════════════════════════

def generate_random_location(center: tuple[float, float], radius: float) -> tuple[float, float]:
    """Generar una ubicación aleatoria dentro de un radio."""
    angle = random.uniform(0, 2 * 3.14159)
    distance = random.uniform(0, radius)
    lon = center[0] + distance * (angle ** 0.5)
    lat = center[1] + distance * (angle ** 0.5)
    return (lon, lat)


def generate_streetlight_models() -> dict[str, StreetlightModel]:
    """Generar modelos de farola."""
    models = {}
    for model in STREETLIGHT_MODELS:
        models[model.id] = model
    return models


def generate_streetlight_groups() -> list[StreetlightGroup]:
    """Generar grupos de farolas."""
    groups = []
    feeders = generate_feeders()
    cabinets = generate_control_cabinets()

    for group_config in STREETLIGHT_GROUPS_CONFIG:
        zone = ZONES[group_config["zone"]]
        group = StreetlightGroup(
            id_=group_config["id"],
            location=zone["center"],
            description=group_config["description"],
            ref_control_cabinet=cabinets[group_config["zone"]].id,
            ref_feeder=feeders[group_config["zone"]].id,
            power_state=PowerState.NORMAL,
        )
        groups.append(group)

    return groups


def generate_feeders() -> dict[str, StreetlightFeeder]:
    """Generar líneas de alimentación por zona."""
    feeders = {}
    for zone_name, zone_config in ZONES.items():
        feeder = StreetlightFeeder(
            id_=f"urn:ngsi-ld:StreetlightFeeder:coruña:{zone_name}",
            description=f"Línea de alimentación - {zone_config['description']}",
            voltage=230.0,
            amperage=63.0,
            power_state=PowerState.NORMAL,
        )
        feeders[zone_name] = feeder
    return feeders


def generate_control_cabinets() -> dict[str, StreetlightControlCabinet]:
    """Generar armarios de control por zona."""
    cabinets = {}
    for zone_name, zone_config in ZONES.items():
        cabinet = StreetlightControlCabinet(
            id_=f"urn:ngsi-ld:StreetlightControlCabinet:coruña:{zone_name}",
            location=zone_config["center"],
            description=f"Armario de control - {zone_config['description']}",
            status=StreetlightStatus.ON,
            power_state=PowerState.NORMAL,
        )
        cabinets[zone_name] = cabinet
    return cabinets


def generate_streetlights() -> list[Streetlight]:
    """Generar 70 farolas distribuidas en las zonas."""
    streetlights = []
    groups = generate_streetlight_groups()
    feeders = generate_feeders()
    cabinets = generate_control_cabinets()
    models = generate_streetlight_models()
    model_list = list(models.values())

    counter = 1
    for group_config in STREETLIGHT_GROUPS_CONFIG:
        zone_name = group_config["zone"]
        zone_config = ZONES[zone_name]
        group_id = group_config["id"]
        cabinet = cabinets[zone_name]
        feeder = feeders[zone_name]
        model = random.choice(model_list)

        # Generar N farolas para esta zona
        for _ in range(group_config["count"]):
            location = generate_random_location(
                zone_config["center"], zone_config["radius"]
            )
            
            # Distribuir estados: 75% ON, 10% OFF, 15% FAULT
            rand = random.random()
            if rand < 0.75:
                status = StreetlightStatus.ON
                power_state = PowerState.NORMAL
                intensity = random.randint(60, 100)
                power = 100.0
            elif rand < 0.85:
                status = StreetlightStatus.OFF
                power_state = PowerState.NORMAL
                intensity = 0
                power = 0.0
            else:
                status = StreetlightStatus.FAULT
                power_state = PowerState.FAILURE
                intensity = random.randint(0, 30)
                power = random.uniform(10, 50)

            streetlight = Streetlight(
                id_=f"urn:ngsi-ld:Streetlight:coruña:SL-{counter:03d}",
                location=location,
                status=status,
                power_state=power_state,
                luminous_intensity=intensity,
                power_consumption=power,
                illuminance_level=intensity * 100 if status == StreetlightStatus.ON else 0,
                ref_streetlight_model=model.id,
                ref_streetlight_group=group_id,
                ref_control_cabinet=cabinet.id,
                ref_feeder=feeder.id,
            )
            streetlights.append(streetlight)
            counter += 1

    return streetlights


def generate_crowd_flows() -> list[CrowdFlowObserved]:
    """Generar observaciones de flujo peatonal por zona."""
    crowd_flows = []
    groups = generate_streetlight_groups()

    for zone_name, zone_config in ZONES.items():
        group = next((g for g in groups if zone_name in g.id), None)
        if not group:
            continue

        # Simulación de flujo peatonal variado
        people_count = random.randint(5, 50)
        occupancy = min(people_count / 100, 1.0)

        flow = CrowdFlowObserved(
            id_=f"urn:ngsi-ld:CrowdFlowObserved:coruña:{zone_name}",
            location=zone_config["center"],
            people_count=people_count,
            occupancy=occupancy,
            max_occupancy=100,
            ref_streetlight_group=group.id,
            description=f"Flujo peatonal - {zone_config['description']}",
        )
        crowd_flows.append(flow)

    return crowd_flows


def generate_traffic_flows() -> list[TrafficFlowObserved]:
    """Generar observaciones de flujo de tráfico por zona."""
    traffic_flows = []
    groups = generate_streetlight_groups()

    traffic_zones = ["centro", "calle_real", "paseo_maritimo", "juan_florez"]

    for zone_name in traffic_zones:
        if zone_name not in ZONES:
            continue

        zone_config = ZONES[zone_name]
        group = next((g for g in groups if zone_name in g.id), None)
        if not group:
            continue

        vehicle_count = random.randint(5, 30)

        flow = TrafficFlowObserved(
            id_=f"urn:ngsi-ld:TrafficFlowObserved:coruña:{zone_name}",
            location=zone_config["center"],
            vehicle_count=vehicle_count,
            vehicle_type="mixed",
            ref_streetlight_group=group.id,
            description=f"Flujo de tráfico - {zone_config['description']}",
        )
        traffic_flows.append(flow)

    return traffic_flows


def generate_item_flows() -> list[ItemFlowObserved]:
    """Generar observaciones genéricas de flujo de elementos."""
    item_flows = []
    groups = generate_streetlight_groups()

    for zone_name, zone_config in ZONES.items():
        group = next((g for g in groups if zone_name in g.id), None)
        if not group:
            continue

        item_count = random.randint(0, 20)

        flow = ItemFlowObserved(
            id_=f"urn:ngsi-ld:ItemFlowObserved:coruña:{zone_name}",
            location=zone_config["center"],
            item_count=item_count,
            item_type="generic",
            ref_streetlight_group=group.id,
            description=f"Flujo genérico - {zone_config['description']}",
        )
        item_flows.append(flow)

    return item_flows


# ═══════════════════════════════════════════════════════════════════════════
# EXPORTAR TODAS LAS ENTIDADES
# ═══════════════════════════════════════════════════════════════════════════

def generate_all_entities() -> dict[str, list]:
    """Generar todas las entidades FIWARE y exportarlas como NGSI-LD."""
    print("🔧 Generando entidades FIWARE...")

    # Generar entidades
    models = generate_streetlight_models()
    feeders = generate_feeders()
    cabinets = generate_control_cabinets()
    groups = generate_streetlight_groups()
    streetlights = generate_streetlights()
    crowd_flows = generate_crowd_flows()
    traffic_flows = generate_traffic_flows()
    item_flows = generate_item_flows()

    # Convertir a NGSI-LD
    entities = {
        "StreetlightModel": [m.to_ngsi_ld() for m in models.values()],
        "StreetlightFeeder": [f.to_ngsi_ld() for f in feeders.values()],
        "StreetlightControlCabinet": [c.to_ngsi_ld() for c in cabinets.values()],
        "StreetlightGroup": [g.to_ngsi_ld() for g in groups],
        "Streetlight": [sl.to_ngsi_ld() for sl in streetlights],
        "CrowdFlowObserved": [cf.to_ngsi_ld() for cf in crowd_flows],
        "TrafficFlowObserved": [tf.to_ngsi_ld() for tf in traffic_flows],
        "ItemFlowObserved": [if_.to_ngsi_ld() for if_ in item_flows],
    }

    print(f"✅ Entidades generadas:")
    for entity_type, entity_list in entities.items():
        print(f"   - {entity_type}: {len(entity_list)}")

    return entities


def export_to_json(filename: str = "fiware_entities.json"):
    """Exportar entidades a fichero JSON."""
    entities = generate_all_entities()
    
    with open(filename, "w") as f:
        json.dump(entities, f, indent=2)
    
    print(f"\n💾 Entidades exportadas a {filename}")
    return entities


if __name__ == "__main__":
    print("═" * 70)
    print("GENERADOR DE ENTIDADES FIWARE - ILUMINACIÓN URBANA A CORUÑA")
    print("═" * 70)
    print()

    entities = export_to_json()
    
    print(f"\n📊 Resumen:")
    total = sum(len(v) for v in entities.values())
    print(f"   Total de entidades: {total}")
    print()
    print("📝 Estructura NGSI-LD compatible con:")
    print("   - Orion Context Broker")
    print("   - QuantumLeap para series temporales")
    print("   - Smart Data Models de FIWARE")
