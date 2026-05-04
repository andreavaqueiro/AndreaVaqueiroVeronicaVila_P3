#!/usr/bin/env python3
"""Cliente mínimo para consultar Orion-LD (NGSI-LD) y adaptar entidades al frontend.

Objetivo del módulo:
- Centralizar el acceso a Orion como *single source of truth*.
- Evitar generación de datos en endpoints HTTP.

No implementa escritura/actuación; solo lectura y transformación.
"""

from __future__ import annotations

import os
from typing import Any, Optional
from urllib.parse import quote

import requests


ORION_BASE_URL = os.getenv("ORION_BASE_URL", "http://localhost:1026").rstrip("/")

HEADERS_LD = {
    # keyValues devuelve JSON simple (más fácil de consumir por dashboard).
    "Accept": "application/json",
}


# Cuando las entidades se crean con @context inline, Orion puede devolver
# options=keyValues usando IRIs como claves. Mapeamos los alias relevantes.
TERM_ALIASES: dict[str, list[str]] = {
    "illuminanceLevel": [
        "illuminanceLevel",
        "https://smartdatamodels.org/dataModel.Streetlighting/illuminanceLevel",
    ],
    "powerConsumption": [
        "powerConsumption",
        "https://smartdatamodels.org/dataModel.Streetlighting/powerConsumption",
    ],
    "refStreetlightGroup": [
        "refStreetlightGroup",
        "https://smartdatamodels.org/dataModel.Streetlighting/refStreetlightGroup",
    ],
    "refStreetlightControlCabinet": [
        "refStreetlightControlCabinet",
        "https://smartdatamodels.org/dataModel.Streetlighting/refStreetlightControlCabinet",
    ],
    "energyConsumed": [
        "energyConsumed",
        "https://smartdatamodels.org/dataModel.Streetlighting/energyConsumed",
    ],
    "workingMode": [
        "workingMode",
        "https://smartdatamodels.org/dataModel.Streetlighting/workingMode",
    ],
    "peopleCount": [
        "peopleCount",
        "https://smartdatamodels.org/dataModel.CrowdFlowObserved/peopleCount",
    ],
    "occupancy": [
        "occupancy",
        "https://smartdatamodels.org/dataModel.CrowdFlowObserved/occupancy",
    ],
    "refDevice": [
        "refDevice",
        "https://smartdatamodels.org/dataModel.CrowdFlowObserved/refDevice",
    ],
    "lastUpdate": [
        "lastUpdate",
        "https://schema.org/dateModified",
    ],
}


def _get_by_alias(entity: dict[str, Any], term: str) -> Any:
    for key in TERM_ALIASES.get(term, [term]):
        if key in entity:
            return entity.get(key)
    return None


def encode_entity_id(entity_id: str) -> str:
    return quote(entity_id, safe="")


def _get_property_value(entity: dict[str, Any], prop: str, default: Any = None) -> Any:
    """Extrae el valor de una Property en NGSI-LD.

    Soporta:
    - Formato normalizado NGSI-LD: {"type":"Property","value":...}
    - Formato keyValues: valor directo
    """
    value = _get_by_alias(entity, prop)
    if value is None:
        return default
    if isinstance(value, dict) and "value" in value:
        return value.get("value", default)
    return value


def _get_relationship_object(entity: dict[str, Any], rel: str) -> Optional[str]:
    value = _get_by_alias(entity, rel)
    # normalizado NGSI-LD
    if isinstance(value, dict):
        obj = value.get("object")
        if isinstance(obj, str):
            return obj
    # keyValues puede devolver string directamente
    if isinstance(value, str):
        return value
    return None


def _get_point_coordinates(entity: dict[str, Any], prop: str = "location") -> Optional[tuple[float, float]]:
    loc = entity.get(prop)
    if not isinstance(loc, dict):
        return None

    # keyValues: {"type":"Point","coordinates":[lon,lat]}
    coords = loc.get("coordinates")
    if not coords:
        # normalizado: {"type":"GeoProperty","value":{"type":"Point","coordinates":[lon,lat]}}
        loc_value = loc.get("value")
        if isinstance(loc_value, dict):
            coords = loc_value.get("coordinates")
    if not (isinstance(coords, list) and len(coords) == 2):
        return None

    lon, lat = coords
    try:
        return float(lat), float(lon)
    except (TypeError, ValueError):
        return None


def orion_health(timeout_s: float = 2.0) -> bool:
    # Orion-LD (NGSI-LD) no expone un /health estable; /version es el endpoint
    # ligero y fiable para comprobar disponibilidad.
    try:
        resp = requests.get(f"{ORION_BASE_URL}/version", timeout=timeout_s)
        if resp.status_code == 200:
            return True
    except requests.RequestException:
        pass

    # Fallback por compatibilidad con mocks u otras variantes.
    try:
        resp = requests.get(f"{ORION_BASE_URL}/health", timeout=timeout_s)
        return resp.status_code == 200
    except requests.RequestException:
        return False


def list_entities(entity_type: str, timeout_s: float = 10.0, page_limit: int = 1000) -> list[dict[str, Any]]:
    """Lista entidades de un tipo, paginando para evitar el límite por defecto.

    Usa options=keyValues para facilitar consumo desde frontend.
    """
    url = f"{ORION_BASE_URL}/ngsi-ld/v1/entities"
    offset = 0
    all_entities: list[dict[str, Any]] = []

    while True:
        params = {
            "type": entity_type,
            "options": "keyValues",
            "limit": page_limit,
            "offset": offset,
        }
        resp = requests.get(url, params=params, headers=HEADERS_LD, timeout=timeout_s)
        resp.raise_for_status()
        page = resp.json()
        if not isinstance(page, list):
            break

        all_entities.extend(page)
        if len(page) < page_limit:
            break
        offset += page_limit

    return all_entities


def streetlight_to_frontend(entity: dict[str, Any]) -> Optional[dict[str, Any]]:
    coords = _get_point_coordinates(entity, "location")
    if not coords:
        return None
    lat, lon = coords

    intensity = _get_property_value(entity, "illuminanceLevel")
    if intensity is None:
        intensity = _get_property_value(entity, "luminousIntensity")

    power = _get_property_value(entity, "powerConsumption")

    return {
        "id": entity.get("id"),
        "type": entity.get("type"),
        "lat": lat,
        "lng": lon,
        "status": _get_property_value(entity, "status"),
        "intensity": intensity,
        "power": power,
        "illuminanceLevel": _get_property_value(entity, "illuminanceLevel"),
        "powerState": _get_property_value(entity, "powerState"),
        "dateObserved": _get_property_value(entity, "dateObserved"),
        "lastUpdate": _get_property_value(entity, "lastUpdate"),
        "refGroup": _get_relationship_object(entity, "refStreetlightGroup"),
        "refCabinet": _get_relationship_object(entity, "refControlCabinet")
        or _get_relationship_object(entity, "refStreetlightControlCabinet"),
    }


def streetlights_to_frontend(entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for ent in entities:
        mapped = streetlight_to_frontend(ent)
        if mapped:
            result.append(mapped)
    return result


def crowd_flow_to_frontend(entity: dict[str, Any]) -> Optional[dict[str, Any]]:
    coords = _get_point_coordinates(entity, "location")
    if not coords:
        return None
    lat, lon = coords

    return {
        "id": entity.get("id"),
        "type": entity.get("type"),
        "location": [lon, lat],
        "peopleCount": _get_property_value(entity, "peopleCount", 0),
        "occupancy": _get_property_value(entity, "occupancy"),
        "description": _get_property_value(entity, "description"),
        "dateObserved": _get_property_value(entity, "dateObserved"),
        "refDevice": _get_relationship_object(entity, "refDevice"),
    }


def crowd_flows_to_frontend(entities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for ent in entities:
        mapped = crowd_flow_to_frontend(ent)
        if mapped:
            result.append(mapped)
    return result


def streetlight_stats(frontend_streetlights: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(frontend_streetlights)
    on_count = sum(1 for sl in frontend_streetlights if sl.get("status") == "on")
    off_count = sum(1 for sl in frontend_streetlights if sl.get("status") == "off")
    fault_count = sum(1 for sl in frontend_streetlights if sl.get("status") == "fault")

    total_power = 0.0
    for sl in frontend_streetlights:
        if sl.get("status") == "on":
            try:
                total_power += float(sl.get("power") or 0)
            except (TypeError, ValueError):
                continue

    total_energy = (total_power * 6) / 1000  # kWh para 6 horas (heurístico del dashboard)

    return {
        "total": total,
        "on": on_count,
        "off": off_count,
        "fault": fault_count,
        "totalPowerConsumption": round(total_power, 2),
        "totalEnergyConsumption6h": round(total_energy, 2),
    }
