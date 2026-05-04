#!/usr/bin/env python3
"""Provisiona entidades NGSI-LD base para Eco-Dimming en Orion Context Broker.

Crea:
- 1 StreetlightControlCabinet
- 2 StreetlightGroup asociados al cuadro
- 4 Streetlight (2 por grupo) con coordenadas en A Coruna
- 2 Device y 2 CrowdFlowObserved inicializados a 0
"""

from __future__ import annotations

import os
import sys
from typing import Dict, List

import requests

ORION_BASE_URL = os.getenv("ORION_BASE_URL", "http://localhost:1026").rstrip("/")

HEADERS_LD_JSON = {
    "Content-Type": "application/ld+json",
    "Accept": "application/ld+json",
}

COMMON_CONTEXT: List[str] = [
    "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
    "https://raw.githubusercontent.com/smart-data-models/dataModel.Streetlighting/master/context.jsonld",
    "https://raw.githubusercontent.com/smart-data-models/dataModel.Device/master/context.jsonld",
    "https://raw.githubusercontent.com/smart-data-models/dataModel.CrowdFlowObserved/master/context.jsonld",
]


def post_entity(entity: Dict) -> None:
    """Crea una entidad NGSI-LD. Si ya existe, se omite sin abortar."""
    url = f"{ORION_BASE_URL}/ngsi-ld/v1/entities"
    response = requests.post(url, headers=HEADERS_LD_JSON, json=entity, timeout=15)

    if response.status_code in (201, 204):
        print(f"[CREATED] {entity['id']}")
        return

    if response.status_code == 409:
        print(f"[SKIPPED] Ya existe: {entity['id']}")
        return

    print(f"[ERROR] No se pudo crear {entity['id']}: {response.status_code} {response.text}")
    response.raise_for_status()


def generate_streetlight_coordinates():
    """Genera 40 coordenadas realistas distribuidas en A Coruña (centro urbano)."""
    import random
    
    # Centro: Plaza de Maria Pita - A Coruña
    center_lat = 43.3712
    center_lon = -8.3959
    
    # Radio de distribución en grados (~500m)
    lat_range = 0.0045
    lon_range = 0.0045
    
    coordinates = []
    for i in range(40):
        lat = center_lat + random.uniform(-lat_range, lat_range)
        lon = center_lon + random.uniform(-lon_range, lon_range)
        coordinates.append((lat, lon, i))
    
    return coordinates


def build_entities() -> List[Dict]:
    """Construye la topologia expandida del sistema Eco-Dimming con 40 farolas."""
    cabinet_id = "urn:ngsi-ld:StreetlightControlCabinet:ACOR-CAB-001"

    group_1_id = "urn:ngsi-ld:StreetlightGroup:ACOR-CENTRO-G01"
    group_2_id = "urn:ngsi-ld:StreetlightGroup:ACOR-CENTRO-G02"
    group_3_id = "urn:ngsi-ld:StreetlightGroup:ACOR-CENTRO-G03"
    group_4_id = "urn:ngsi-ld:StreetlightGroup:ACOR-CENTRO-G04"

    device_1_id = "urn:ngsi-ld:Device:ACOR-MP-SENSOR-001"
    device_2_id = "urn:ngsi-ld:Device:ACOR-MP-SENSOR-002"
    device_3_id = "urn:ngsi-ld:Device:ACOR-MP-SENSOR-003"
    device_4_id = "urn:ngsi-ld:Device:ACOR-MP-SENSOR-004"

    crowd_1_id = "urn:ngsi-ld:CrowdFlowObserved:ACOR-MP-CROWD-001"
    crowd_2_id = "urn:ngsi-ld:CrowdFlowObserved:ACOR-MP-CROWD-002"
    crowd_3_id = "urn:ngsi-ld:CrowdFlowObserved:ACOR-MP-CROWD-003"
    crowd_4_id = "urn:ngsi-ld:CrowdFlowObserved:ACOR-MP-CROWD-004"

    entities: List[Dict] = []

    # Cuadro de control
    entities.append(
        {
            "id": cabinet_id,
            "type": "StreetlightControlCabinet",
            "brandName": {"type": "Property", "value": "Schneider Electric"},
            "energyConsumed": {
                "type": "Property",
                "value": 1280.0,
                "unitCode": "KWH",
            },
            "workingMode": {"type": "Property", "value": "eco"},
            "@context": COMMON_CONTEXT,
        }
    )

    # Grupos de farolas (4 grupos para distribuir 40 farolas)
    for group_id, power in [(group_1_id, "eco"), (group_2_id, "eco"), (group_3_id, "eco"), (group_4_id, "eco")]:
        entities.append(
            {
                "id": group_id,
                "type": "StreetlightGroup",
                "powerState": {"type": "Property", "value": power},
                "refStreetlightControlCabinet": {
                    "type": "Relationship",
                    "object": cabinet_id,
                },
                "@context": COMMON_CONTEXT,
            }
        )

    # Generar 40 farolas con estados variados
    import random
    coords = generate_streetlight_coordinates()
    groups = [group_1_id, group_2_id, group_3_id, group_4_id]
    states = ["on", "off", "fault"]  # Estados posibles
    
    for lat, lon, idx in coords:
        streetlight_id = f"urn:ngsi-ld:Streetlight:ACOR-SL-{idx+1:03d}"
        group_id = groups[idx % 4]
        
        # Variar estados: 70% encendida, 20% apagada, 10% averiada
        rand = random.random()
        if rand < 0.7:
            status = "on"
            intensity = random.randint(20, 100)
        elif rand < 0.9:
            status = "off"
            intensity = 0
        else:
            status = "fault"
            intensity = random.randint(0, 50)
        
        entities.append(
            {
                "id": streetlight_id,
                "type": "Streetlight",
                "location": {
                    "type": "GeoProperty",
                    "value": {
                        "type": "Point",
                        "coordinates": [lon, lat],
                    },
                },
                "status": {"type": "Property", "value": status},
                "illuminanceLevel": {
                    "type": "Property",
                    "value": intensity,
                    "unitCode": "P1",
                },
                "powerConsumption": {
                    "type": "Property",
                    "value": intensity * 0.75 if status == "on" else 0,
                    "unitCode": "W",
                },
                "lastUpdate": {
                    "type": "Property",
                    "value": "2026-04-29T12:00:00Z",
                },
                "refStreetlightGroup": {
                    "type": "Relationship",
                    "object": group_id,
                },
                "@context": COMMON_CONTEXT,
            }
        )

    # Sensores de dispositivos (4 sensores)
    for did, gid in [(device_1_id, group_1_id), (device_2_id, group_2_id), 
                      (device_3_id, group_3_id), (device_4_id, group_4_id)]:
        entities.append(
            {
                "id": did,
                "type": "Device",
                "category": {"type": "Property", "value": ["crowdSensor", "iotAgent"]},
                "batteryLevel": {"type": "Property", "value": random.randint(80, 100), "unitCode": "P1"},
                "controlledAsset": {
                    "type": "Relationship",
                    "object": gid,
                },
                "@context": COMMON_CONTEXT,
            }
        )

    # Observadores de flujo peatonal (4 ubicaciones)
    crowd_coords = [
        (43.3710, -8.3965),
        (43.3715, -8.3955),
        (43.3708, -8.3950),
        (43.3720, -8.3965),
    ]
    
    for cid, did, (lat, lon) in zip([crowd_1_id, crowd_2_id, crowd_3_id, crowd_4_id],
                                      [device_1_id, device_2_id, device_3_id, device_4_id],
                                      crowd_coords):
        entities.append(
            {
                "id": cid,
                "type": "CrowdFlowObserved",
                "location": {
                    "type": "GeoProperty",
                    "value": {
                        "type": "Point",
                        "coordinates": [lon, lat],
                    },
                },
                "peopleCount": {"type": "Property", "value": 0},
                "occupancy": {"type": "Property", "value": 0.0},
                "refDevice": {
                    "type": "Relationship",
                    "object": did,
                },
                "@context": COMMON_CONTEXT,
            }
        )

    return entities


def main() -> int:
    print(f"Usando ORION_BASE_URL={ORION_BASE_URL}")
    entities = build_entities()
    for entity in entities:
        post_entity(entity)

    print("Provision finalizado.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except requests.RequestException as exc:
        print(f"Error de red o HTTP: {exc}", file=sys.stderr)
        raise SystemExit(1)
