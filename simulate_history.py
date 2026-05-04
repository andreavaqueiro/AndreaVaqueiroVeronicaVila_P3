#!/usr/bin/env python3
"""Simula historico nocturno para Eco-Dimming via actualizaciones NGSI-LD.

Requiere que las entidades ya existan en Orion (ejecutar provision_entities.py primero).
Envía PATCH a /ngsi-ld/v1/entities/{entityId}/attrs para que QuantumLeap persista
los cambios mediante suscripciones existentes.
"""

from __future__ import annotations

import os
import random
import sys
import time
from datetime import datetime, timezone
from typing import Dict, Iterable
from urllib.parse import quote

import requests

ORION_BASE_URL = os.getenv("ORION_BASE_URL", "http://localhost:1026").rstrip("/")
ITERATIONS = int(os.getenv("SIM_ITERATIONS", "20"))
SLEEP_SECONDS = float(os.getenv("SIM_SLEEP_SECONDS", "1"))

HEADERS_PATCH = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

CABINET_ID = "urn:ngsi-ld:StreetlightControlCabinet:ACOR-CAB-001"

CROWD_IDS = [
    "urn:ngsi-ld:CrowdFlowObserved:ACOR-MP-CROWD-001",
    "urn:ngsi-ld:CrowdFlowObserved:ACOR-MP-CROWD-002",
]

STREETLIGHT_IDS = [
    "urn:ngsi-ld:Streetlight:ACOR-MP-001",
    "urn:ngsi-ld:Streetlight:ACOR-MP-002",
    "urn:ngsi-ld:Streetlight:ACOR-MP-003",
    "urn:ngsi-ld:Streetlight:ACOR-MP-004",
]


def patch_attrs(entity_id: str, attrs: Dict) -> None:
    """PATCH de atributos NGSI-LD sobre una entidad existente."""
    encoded_id = quote(entity_id, safe="")
    url = f"{ORION_BASE_URL}/ngsi-ld/v1/entities/{encoded_id}/attrs"
    response = requests.patch(url, headers=HEADERS_PATCH, json=attrs, timeout=15)

    if response.status_code in (204, 200):
        return

    print(f"[ERROR] PATCH {entity_id} -> {response.status_code} {response.text}")
    response.raise_for_status()


def current_observed_at() -> str:
    return datetime.now(timezone.utc).isoformat()


def patch_cabinet_energy(energy_value: float) -> None:
    patch_attrs(
        CABINET_ID,
        {
            "energyConsumed": {
                "type": "Property",
                "value": round(energy_value, 3),
                "unitCode": "KWH",
                "observedAt": current_observed_at(),
            }
        },
    )


def patch_crowd_people(people_count: int) -> None:
    occupancy = min(1.0, people_count / 50.0)
    payload = {
        "peopleCount": {
            "type": "Property",
            "value": people_count,
            "observedAt": current_observed_at(),
        },
        "occupancy": {
            "type": "Property",
            "value": round(occupancy, 3),
            "observedAt": current_observed_at(),
        },
    }
    for crowd_id in CROWD_IDS:
        patch_attrs(crowd_id, payload)


def patch_streetlights(level: int, status: str) -> None:
    payload = {
        "illuminanceLevel": {
            "type": "Property",
            "value": level,
            "unitCode": "P1",
            "observedAt": current_observed_at(),
        },
        "status": {
            "type": "Property",
            "value": status,
            "observedAt": current_observed_at(),
        },
    }
    for sid in STREETLIGHT_IDS:
        patch_attrs(sid, payload)


def low_traffic_step() -> int:
    return random.randint(0, 6)


def medium_traffic_step() -> int:
    return random.randint(20, 35)


def simulate() -> None:
    energy_kwh = 1280.0

    print(
        f"Iniciando simulacion: iteraciones={ITERATIONS}, sleep={SLEEP_SECONDS}s, ORION={ORION_BASE_URL}"
    )

    for i in range(1, ITERATIONS + 1):
        # Consumo siempre ascendente con pequenas variaciones por ciclo.
        energy_kwh += random.uniform(0.4, 1.4)
        patch_cabinet_energy(energy_kwh)

        if i < 5:
            people = low_traffic_step()
            patch_crowd_people(people)
            patch_streetlights(20, "20%")

        elif i == 5:
            # Pico peatonal solicitado.
            patch_crowd_people(45)
            patch_streetlights(100, "100%")

        elif 5 < i < 10:
            people = max(30, medium_traffic_step())
            patch_crowd_people(people)
            patch_streetlights(100, "100%")

        elif i == 10:
            # Retorno a modo ahorro solicitado.
            patch_crowd_people(2)
            patch_streetlights(20, "20%")

        else:
            people = low_traffic_step()
            patch_crowd_people(people)
            patch_streetlights(20, "20%")

        print(
            f"[Iter {i:02d}] energyConsumed={energy_kwh:.3f} kWh | peopleCount={people if i not in (5,10) else (45 if i == 5 else 2)}"
        )
        time.sleep(SLEEP_SECONDS)

    print("Simulacion historica finalizada.")


if __name__ == "__main__":
    try:
        simulate()
    except requests.RequestException as exc:
        print(f"Error de red o HTTP: {exc}", file=sys.stderr)
        raise SystemExit(1)
