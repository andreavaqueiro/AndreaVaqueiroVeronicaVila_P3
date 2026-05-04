#!/usr/bin/env python3
"""Simulador único de datos para Eco-Dimming (FIWARE NGSI-LD).

Objetivo:
- Unificar provisión + simulación en un solo pipeline coherente.
- Orion-LD es la única fuente de verdad: este script crea entidades y las
  actualiza en el tiempo mediante peticiones NGSI-LD.

Uso típico:
  python3 simulator.py init
  python3 simulator.py run

Variables de entorno:
- ORION_BASE_URL (default: http://localhost:1026)
- SIM_ITERATIONS (default: 0 -> infinito)
- SIM_SLEEP_SECONDS (default: 2)
- SIM_SEED (default: 42)

Este script NO se usa desde endpoints HTTP.
"""

from __future__ import annotations

import argparse
import os
import random
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable, Optional
from urllib.parse import quote

import requests


ORION_BASE_URL = os.getenv("ORION_BASE_URL", "http://localhost:1026").rstrip("/")
DEFAULT_ITERATIONS = int(os.getenv("SIM_ITERATIONS", "0"))
DEFAULT_SLEEP_SECONDS = float(os.getenv("SIM_SLEEP_SECONDS", "2"))
DEFAULT_SEED = int(os.getenv("SIM_SEED", "42"))

HEADERS_LD_JSON = {
    "Content-Type": "application/ld+json",
    "Accept": "application/ld+json",
}

# Contexto mínimo embebido para evitar descargas remotas.
COMMON_CONTEXT: dict[str, str] = {
    "location": "https://uri.etsi.org/ngsi-ld/location",
    "GeoProperty": "https://uri.etsi.org/ngsi-ld/GeoProperty",
    "Property": "https://uri.etsi.org/ngsi-ld/Property",
    "Relationship": "https://uri.etsi.org/ngsi-ld/Relationship",
    "unitCode": "https://uri.etsi.org/ngsi-ld/unitCode",
    "observedAt": "https://uri.etsi.org/ngsi-ld/observedAt",
    "brandName": "https://schema.org/brand",
    "energyConsumed": "https://smartdatamodels.org/dataModel.Streetlighting/energyConsumed",
    "workingMode": "https://smartdatamodels.org/dataModel.Streetlighting/workingMode",
    "powerState": "https://smartdatamodels.org/dataModel.Streetlighting/powerState",
    "refStreetlightControlCabinet": "https://smartdatamodels.org/dataModel.Streetlighting/refStreetlightControlCabinet",
    "refStreetlightGroup": "https://smartdatamodels.org/dataModel.Streetlighting/refStreetlightGroup",
    "status": "https://smartdatamodels.org/dataModel.Streetlighting/status",
    "illuminanceLevel": "https://smartdatamodels.org/dataModel.Streetlighting/illuminanceLevel",
    "powerConsumption": "https://smartdatamodels.org/dataModel.Streetlighting/powerConsumption",
    "lastUpdate": "https://schema.org/dateModified",
    "category": "https://smartdatamodels.org/dataModel.Device/category",
    "batteryLevel": "https://smartdatamodels.org/dataModel.Device/batteryLevel",
    "controlledAsset": "https://smartdatamodels.org/dataModel.Device/controlledAsset",
    "peopleCount": "https://smartdatamodels.org/dataModel.CrowdFlowObserved/peopleCount",
    "occupancy": "https://smartdatamodels.org/dataModel.CrowdFlowObserved/occupancy",
    "refDevice": "https://smartdatamodels.org/dataModel.CrowdFlowObserved/refDevice",
}


@dataclass(frozen=True)
class TopologyIds:
    cabinet_id: str
    group_ids: list[str]
    device_ids: list[str]
    crowd_ids: list[str]
    streetlight_ids: list[str]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def encode_entity_id(entity_id: str) -> str:
    return quote(entity_id, safe="")


def orion_url(path: str) -> str:
    return f"{ORION_BASE_URL}{path}"


def post_entity(entity: dict[str, Any], timeout_s: float = 15.0) -> None:
    url = orion_url("/ngsi-ld/v1/entities")
    resp = requests.post(url, headers=HEADERS_LD_JSON, json=entity, timeout=timeout_s)

    if resp.status_code in (201, 204):
        print(f"[CREATED] {entity['id']}")
        return
    if resp.status_code == 409:
        print(f"[SKIPPED] Ya existe: {entity['id']}")
        return

    print(f"[ERROR] POST {entity['id']} -> {resp.status_code} {resp.text}")
    resp.raise_for_status()


def delete_entity(entity_id: str, timeout_s: float = 10.0) -> None:
    url = orion_url(f"/ngsi-ld/v1/entities/{encode_entity_id(entity_id)}")
    resp = requests.delete(url, timeout=timeout_s)
    if resp.status_code in (204, 404):
        return
    resp.raise_for_status()


def get_entity(entity_id: str, timeout_s: float = 10.0) -> Optional[dict[str, Any]]:
    url = orion_url(f"/ngsi-ld/v1/entities/{encode_entity_id(entity_id)}")
    resp = requests.get(url, headers=HEADERS_LD_JSON, timeout=timeout_s)
    if resp.status_code == 200:
        data = resp.json()
        return data if isinstance(data, dict) else None
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return None


def patch_attrs(entity_id: str, attrs: dict[str, Any], timeout_s: float = 10.0) -> None:
    url = orion_url(f"/ngsi-ld/v1/entities/{encode_entity_id(entity_id)}/attrs")
    # Orion-LD requiere @context cuando Content-Type es application/ld+json.
    payload: dict[str, Any] = {"@context": COMMON_CONTEXT}
    payload.update(attrs)
    resp = requests.patch(url, headers=HEADERS_LD_JSON, json=payload, timeout=timeout_s)
    # 207: multi-status (actualización parcial) es común si algún atributo
    # no existe todavía. Nos vale mientras el broker acepte la petición.
    if resp.status_code in (200, 204, 207):
        return
    print(f"[ERROR] PATCH {entity_id} -> {resp.status_code} {resp.text}")
    resp.raise_for_status()


def list_entities(entity_type: str, timeout_s: float = 10.0, limit: int = 1000) -> list[dict[str, Any]]:
    url = orion_url("/ngsi-ld/v1/entities")
    offset = 0
    all_entities: list[dict[str, Any]] = []

    while True:
        params = {"type": entity_type, "limit": limit, "offset": offset}
        resp = requests.get(url, params=params, headers=HEADERS_LD_JSON, timeout=timeout_s)
        resp.raise_for_status()
        page = resp.json()
        if not isinstance(page, list):
            break
        all_entities.extend(page)
        if len(page) < limit:
            break
        offset += limit

    return all_entities


def generate_streetlight_coordinates(count: int, seed: int) -> list[tuple[float, float]]:
    """Coordenadas realistas distribuidas en A Coruña (cerca de María Pita)."""
    rng = random.Random(seed)

    center_lat = 43.3712
    center_lon = -8.3959

    # ~500m (aprox.)
    lat_range = 0.0045
    lon_range = 0.0045

    coords: list[tuple[float, float]] = []
    for _ in range(count):
        lat = center_lat + rng.uniform(-lat_range, lat_range)
        lon = center_lon + rng.uniform(-lon_range, lon_range)
        coords.append((lat, lon))
    return coords


def build_topology(streetlight_count: int, seed: int) -> tuple[TopologyIds, list[dict[str, Any]]]:
    cabinet_id = "urn:ngsi-ld:StreetlightControlCabinet:ACOR-CAB-001"

    group_ids = [
        "urn:ngsi-ld:StreetlightGroup:ACOR-CENTRO-G01",
        "urn:ngsi-ld:StreetlightGroup:ACOR-CENTRO-G02",
        "urn:ngsi-ld:StreetlightGroup:ACOR-CENTRO-G03",
        "urn:ngsi-ld:StreetlightGroup:ACOR-CENTRO-G04",
    ]

    device_ids = [
        "urn:ngsi-ld:Device:ACOR-MP-SENSOR-001",
        "urn:ngsi-ld:Device:ACOR-MP-SENSOR-002",
        "urn:ngsi-ld:Device:ACOR-MP-SENSOR-003",
        "urn:ngsi-ld:Device:ACOR-MP-SENSOR-004",
    ]

    crowd_ids = [
        "urn:ngsi-ld:CrowdFlowObserved:ACOR-MP-CROWD-001",
        "urn:ngsi-ld:CrowdFlowObserved:ACOR-MP-CROWD-002",
        "urn:ngsi-ld:CrowdFlowObserved:ACOR-MP-CROWD-003",
        "urn:ngsi-ld:CrowdFlowObserved:ACOR-MP-CROWD-004",
    ]

    streetlight_ids = [
        f"urn:ngsi-ld:Streetlight:ACOR-SL-{i+1:03d}" for i in range(streetlight_count)
    ]

    entities: list[dict[str, Any]] = []

    entities.append(
        {
            "id": cabinet_id,
            "type": "StreetlightControlCabinet",
            "brandName": {"type": "Property", "value": "Schneider Electric"},
            "energyConsumed": {"type": "Property", "value": 1280.0, "unitCode": "KWH"},
            "workingMode": {"type": "Property", "value": "eco"},
            "lastUpdate": {"type": "Property", "value": utc_now_iso()},
            "@context": COMMON_CONTEXT,
        }
    )

    for group_id in group_ids:
        entities.append(
            {
                "id": group_id,
                "type": "StreetlightGroup",
                "powerState": {"type": "Property", "value": "eco"},
                "refStreetlightControlCabinet": {"type": "Relationship", "object": cabinet_id},
                "lastUpdate": {"type": "Property", "value": utc_now_iso()},
                "@context": COMMON_CONTEXT,
            }
        )

    rng = random.Random(seed)
    coords = generate_streetlight_coordinates(streetlight_count, seed)

    for idx, (lat, lon) in enumerate(coords):
        streetlight_id = streetlight_ids[idx]
        group_id = group_ids[idx % len(group_ids)]

        rand = rng.random()
        if rand < 0.7:
            status = "on"
            intensity = rng.randint(20, 100)
        elif rand < 0.9:
            status = "off"
            intensity = 0
        else:
            status = "fault"
            intensity = rng.randint(0, 50)

        entities.append(
            {
                "id": streetlight_id,
                "type": "Streetlight",
                "location": {
                    "type": "GeoProperty",
                    "value": {"type": "Point", "coordinates": [lon, lat]},
                },
                "status": {"type": "Property", "value": status},
                "illuminanceLevel": {"type": "Property", "value": intensity, "unitCode": "P1"},
                "powerConsumption": {
                    "type": "Property",
                    "value": intensity * 0.75 if status == "on" else 0,
                    "unitCode": "W",
                },
                "powerState": {"type": "Property", "value": "normal"},
                "lastUpdate": {"type": "Property", "value": utc_now_iso()},
                "refStreetlightGroup": {"type": "Relationship", "object": group_id},
                "@context": COMMON_CONTEXT,
            }
        )

    for did, gid in zip(device_ids, group_ids, strict=False):
        entities.append(
            {
                "id": did,
                "type": "Device",
                "category": {"type": "Property", "value": ["crowdSensor", "iotAgent"]},
                "batteryLevel": {"type": "Property", "value": rng.randint(80, 100), "unitCode": "P1"},
                "controlledAsset": {"type": "Relationship", "object": gid},
                "lastUpdate": {"type": "Property", "value": utc_now_iso()},
                "@context": COMMON_CONTEXT,
            }
        )

    crowd_coords = [
        (43.3710, -8.3965),
        (43.3715, -8.3955),
        (43.3708, -8.3950),
        (43.3720, -8.3965),
    ]

    for cid, did, (lat, lon) in zip(crowd_ids, device_ids, crowd_coords, strict=False):
        entities.append(
            {
                "id": cid,
                "type": "CrowdFlowObserved",
                "location": {
                    "type": "GeoProperty",
                    "value": {"type": "Point", "coordinates": [lon, lat]},
                },
                "peopleCount": {"type": "Property", "value": 0},
                "occupancy": {"type": "Property", "value": 0.0},
                "refDevice": {"type": "Relationship", "object": did},
                "lastUpdate": {"type": "Property", "value": utc_now_iso()},
                "@context": COMMON_CONTEXT,
            }
        )

    ids = TopologyIds(
        cabinet_id=cabinet_id,
        group_ids=group_ids,
        device_ids=device_ids,
        crowd_ids=crowd_ids,
        streetlight_ids=streetlight_ids,
    )
    return ids, entities


def reset_our_entities(timeout_s: float = 10.0) -> None:
    """Borra entidades del escenario Eco-Dimming para evitar duplicados."""
    prefixes = [
        "urn:ngsi-ld:Streetlight:ACOR-SL-",
        "urn:ngsi-ld:CrowdFlowObserved:ACOR-MP-CROWD-",
        "urn:ngsi-ld:Device:ACOR-MP-SENSOR-",
        "urn:ngsi-ld:StreetlightGroup:ACOR-CENTRO-",
        "urn:ngsi-ld:StreetlightControlCabinet:ACOR-CAB-001",
    ]

    types_to_scan = ["Streetlight", "CrowdFlowObserved", "Device", "StreetlightGroup", "StreetlightControlCabinet"]
    to_delete: list[str] = []
    for t in types_to_scan:
        for ent in list_entities(t, timeout_s=timeout_s):
            eid = ent.get("id")
            if isinstance(eid, str) and any(eid == p or eid.startswith(p) for p in prefixes):
                to_delete.append(eid)

    # Borramos primero dependientes y luego el cabinet.
    for eid in sorted(to_delete, reverse=True):
        delete_entity(eid, timeout_s=timeout_s)

    print(f"[RESET] Borradas {len(to_delete)} entidades del escenario")


def init_topology(streetlight_count: int, seed: int, reset: bool) -> TopologyIds:
    if reset:
        reset_our_entities()

    ids, entities = build_topology(streetlight_count=streetlight_count, seed=seed)
    for entity in entities:
        post_entity(entity)

    return ids


def read_energy_kwh(cabinet: dict[str, Any]) -> Optional[float]:
    try:
        val = cabinet.get("energyConsumed")
        if isinstance(val, dict) and "value" in val:
            return float(val["value"])
    except (TypeError, ValueError):
        return None
    return None


def compute_base_intensity(total_people: int) -> tuple[int, str]:
    if total_people > 30:
        return 100, "Alta demanda peatonal"
    if total_people > 10:
        return 60, "Demanda moderada"
    return 20, "Modo ahorro"


def run_simulation(
    ids: TopologyIds,
    iterations: int,
    sleep_s: float,
    seed: int,
    failure_rate: float,
    off_rate: float,
) -> None:
    rng = random.Random(seed)

    energy_kwh = 1280.0
    cabinet = get_entity(ids.cabinet_id)
    if cabinet:
        current = read_energy_kwh(cabinet)
        if current is not None:
            energy_kwh = max(energy_kwh, current)

    print(f"Usando ORION_BASE_URL={ORION_BASE_URL}")
    print(
        f"Simulación: iterations={'infinito' if iterations == 0 else iterations}, sleep={sleep_s}s, seed={seed}"
    )

    i = 0
    while True:
        if iterations and i >= iterations:
            break

        # --- CrowdFlowObserved ---
        people_per_sensor: list[int] = []
        for _ in ids.crowd_ids:
            people_per_sensor.append(rng.randint(0, 25))

        total_people = sum(people_per_sensor)
        base_intensity, reason = compute_base_intensity(total_people)

        for crowd_id, people in zip(ids.crowd_ids, people_per_sensor, strict=False):
            occupancy = min(1.0, people / 50.0)
            patch_attrs(
                crowd_id,
                {
                    "peopleCount": {"type": "Property", "value": people},
                    "occupancy": {"type": "Property", "value": round(occupancy, 3)},
                    "lastUpdate": {"type": "Property", "value": utc_now_iso()},
                },
            )

        # --- Streetlights ---
        for sid in ids.streetlight_ids:
            r = rng.random()
            if r < failure_rate:
                status = "fault"
                intensity = rng.randint(0, 30)
            elif r < failure_rate + off_rate:
                status = "off"
                intensity = 0
            else:
                status = "on"
                intensity = max(0, min(100, base_intensity + rng.randint(-10, 10)))

            power = intensity * 0.75 if status == "on" else 0
            patch_attrs(
                sid,
                {
                    "status": {"type": "Property", "value": status},
                    "illuminanceLevel": {"type": "Property", "value": intensity, "unitCode": "P1"},
                    "powerConsumption": {"type": "Property", "value": power, "unitCode": "W"},
                    "lastUpdate": {"type": "Property", "value": utc_now_iso()},
                },
            )

        # --- Cabinet energy ---
        energy_kwh += rng.uniform(0.4, 1.4)
        patch_attrs(
            ids.cabinet_id,
            {
                "energyConsumed": {"type": "Property", "value": round(energy_kwh, 3), "unitCode": "KWH"},
                "lastUpdate": {"type": "Property", "value": utc_now_iso()},
            },
        )

        print(
            f"[Iter {i+1:03d}] total_people={total_people:02d} base_intensity={base_intensity}% ({reason}) energyConsumed={energy_kwh:.3f}kWh"
        )

        i += 1
        time.sleep(sleep_s)


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Simulador único Eco-Dimming (Orion NGSI-LD)")
    sub = p.add_subparsers(dest="cmd", required=True)

    init_p = sub.add_parser("init", help="Crea la topología base (idempotente)")
    init_p.add_argument("--streetlights", type=int, default=40, help="Número de farolas (default: 40)")
    init_p.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Semilla (default: env SIM_SEED o 42)")
    init_p.add_argument("--reset", action="store_true", help="Borra primero las entidades del escenario")

    run_p = sub.add_parser("run", help="Crea (si hace falta) y actualiza en bucle")
    run_p.add_argument("--streetlights", type=int, default=40, help="Número de farolas (default: 40)")
    run_p.add_argument("--seed", type=int, default=DEFAULT_SEED, help="Semilla (default: env SIM_SEED o 42)")
    run_p.add_argument("--reset", action="store_true", help="Borra primero las entidades del escenario")
    run_p.add_argument(
        "--iterations",
        type=int,
        default=DEFAULT_ITERATIONS,
        help="Iteraciones (0=infinito). Default: env SIM_ITERATIONS o 0",
    )
    run_p.add_argument(
        "--sleep",
        type=float,
        default=DEFAULT_SLEEP_SECONDS,
        help="Segundos entre iteraciones. Default: env SIM_SLEEP_SECONDS o 2",
    )
    run_p.add_argument(
        "--failure-rate",
        type=float,
        default=0.01,
        help="Probabilidad de farola en fault por iteración (default: 0.01)",
    )
    run_p.add_argument(
        "--off-rate",
        type=float,
        default=0.04,
        help="Probabilidad de farola apagada por iteración (default: 0.04)",
    )

    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)

    if args.cmd == "init":
        init_topology(streetlight_count=args.streetlights, seed=args.seed, reset=args.reset)
        return 0

    if args.cmd == "run":
        ids = init_topology(streetlight_count=args.streetlights, seed=args.seed, reset=args.reset)
        run_simulation(
            ids,
            iterations=args.iterations,
            sleep_s=args.sleep,
            seed=args.seed,
            failure_rate=args.failure_rate,
            off_rate=args.off_rate,
        )
        return 0

    return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nInterrumpido por usuario")
        raise SystemExit(0)
    except requests.RequestException as exc:
        print(f"Error de red o HTTP: {exc}", file=sys.stderr)
        raise SystemExit(1)
