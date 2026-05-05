#!/usr/bin/env python3
"""Backend API FastAPI para Eco-Dimming MVP.

Expone endpoints para:
- Consulta de estado actual de entidades desde Orion
- Consulta de histórico desde QuantumLeap
- Lógica simple de recomendación de intensidad
- Detección básica de anomalías
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any
from urllib.parse import quote

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from orion_client import (
    ORION_BASE_URL,
    crowd_flows_to_frontend,
    list_entities,
    orion_health,
    streetlight_stats,
    streetlights_to_frontend,
)

QUANTUMLEAP_BASE_URL = os.getenv(
    "QUANTUMLEAP_BASE_URL", "http://localhost:8668"
).rstrip("/")

# Con entidades NGSI-LD compactadas con @context, las notificaciones NGSIv2 (vía /v2)
# suelen usar el IRI completo como nombre de atributo.
QL_ENERGY_ATTR = "https://smartdatamodels.org/dataModel.Streetlighting/energyConsumed"
QL_PEOPLE_ATTR = "https://smartdatamodels.org/dataModel.CrowdFlowObserved/peopleCount"

app = FastAPI(
    title="Eco-Dimming MVP API",
    description="Backend para gestión de iluminación urbana inteligente",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HEADERS_LD = {
    "Accept": "application/ld+json",
}


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check del backend."""
    return {"status": "ok"}


@app.get("/api/fiware/health")
async def fiware_health() -> dict[str, str]:
    """Health check de conectividad con Orion-LD."""
    try:
        ok = orion_health(timeout_s=2.0)
        if not ok:
            raise HTTPException(status_code=503, detail="Orion healthcheck failed")
        return {"status": "ok", "orion": ORION_BASE_URL}
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get("/api/streetlights/fiware")
async def get_streetlights_fiware() -> dict[str, Any]:
    """Devuelve farolas en formato consumible por el dashboard.

    Fuente única de verdad: Orion-LD.
    """
    try:
        entities = list_entities("Streetlight")
        data = streetlights_to_frontend(entities)
        return {"data": data, "stats": streetlight_stats(data)}
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get("/api/crowd-flows/fiware")
async def get_crowd_flows_fiware() -> list[dict[str, Any]]:
    """Devuelve CrowdFlowObserved en formato consumible por el dashboard.

    Fuente única de verdad: Orion-LD.
    """
    try:
        entities = list_entities("CrowdFlowObserved")
        return crowd_flows_to_frontend(entities)
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get("/api/streetlights")
async def get_streetlights() -> dict[str, Any]:
    """Obtiene estado de todas las farolas desde Orion."""
    try:
        url = f"{ORION_BASE_URL}/ngsi-ld/v1/entities?type=Streetlight"
        response = requests.get(url, headers=HEADERS_LD, timeout=10)
        response.raise_for_status()
        entities = response.json()
        return {"count": len(entities), "streetlights": entities}
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get("/api/streetlight-groups")
async def get_streetlight_groups() -> dict[str, Any]:
    """Obtiene estado de grupos de farolas desde Orion."""
    try:
        url = f"{ORION_BASE_URL}/ngsi-ld/v1/entities?type=StreetlightGroup"
        response = requests.get(url, headers=HEADERS_LD, timeout=10)
        response.raise_for_status()
        entities = response.json()
        return {"count": len(entities), "groups": entities}
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get("/api/cabinet")
async def get_cabinet() -> dict[str, Any]:
    """Obtiene estado del cuadro eléctrico desde Orion."""
    try:
        url = f"{ORION_BASE_URL}/ngsi-ld/v1/entities?type=StreetlightControlCabinet"
        response = requests.get(url, headers=HEADERS_LD, timeout=10)
        response.raise_for_status()
        entities = response.json()
        if not entities:
            raise HTTPException(status_code=404, detail="No cabinet found")
        return {"cabinet": entities[0]}
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get("/api/crowd-flows")
async def get_crowd_flows() -> dict[str, Any]:
    """Obtiene flujos peatonales desde Orion."""
    try:
        url = f"{ORION_BASE_URL}/ngsi-ld/v1/entities?type=CrowdFlowObserved"
        response = requests.get(url, headers=HEADERS_LD, timeout=10)
        response.raise_for_status()
        entities = response.json()
        return {"count": len(entities), "flows": entities}
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get("/api/historical/energy")
async def get_historical_energy(hours: int = 6) -> dict[str, Any]:
    """Obtiene histórico de consumo energético desde QuantumLeap."""
    try:
        cabinet_id = "urn:ngsi-ld:StreetlightControlCabinet:ACOR-CAB-001"
        cabinet_id_enc = quote(cabinet_id, safe="")
        now = datetime.now(timezone.utc)
        before = (now - timedelta(hours=hours)).isoformat()
        energy_attr_enc = quote(QL_ENERGY_ATTR, safe="")
        url = f"{QUANTUMLEAP_BASE_URL}/v2/entities/{cabinet_id_enc}/attrs/{energy_attr_enc}"
        response = requests.get(url, params={"fromDate": before}, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {"historical": data}
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get("/api/historical/crowd")
async def get_historical_crowd(hours: int = 6) -> dict[str, Any]:
    """Obtiene histórico de flujos peatonales desde QuantumLeap."""
    try:
        crowd_id = "urn:ngsi-ld:CrowdFlowObserved:ACOR-MP-CROWD-001"
        crowd_id_enc = quote(crowd_id, safe="")
        now = datetime.now(timezone.utc)
        before = (now - timedelta(hours=hours)).isoformat()
        people_attr_enc = quote(QL_PEOPLE_ATTR, safe="")
        url = f"{QUANTUMLEAP_BASE_URL}/v2/entities/{crowd_id_enc}/attrs/{people_attr_enc}"
        response = requests.get(url, params={"fromDate": before}, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {"historical": data}
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


def calculate_recommended_intensity(
    people_count: int, traffic_intensity: float
) -> int:
    """Lógica simple de recomendación de intensidad lumínica."""
    if people_count > 30 or traffic_intensity > 0.7:
        return 100
    elif people_count > 10 or traffic_intensity > 0.4:
        return 60
    else:
        return 20


@app.get("/api/recommendation")
async def get_recommendation() -> dict[str, Any]:
    """Obtiene recomendación de intensidad basada en contexto actual."""
    try:
        entities = list_entities("CrowdFlowObserved")
        crowds = crowd_flows_to_frontend(entities)
        total_people = 0
        for crowd in crowds:
            try:
                total_people += int(crowd.get("peopleCount") or 0)
            except (TypeError, ValueError):
                continue

        # No hay fuente de tráfico en Orion en este MVP; evitamos inventar valores.
        recommended_intensity = calculate_recommended_intensity(total_people, 0.0)

        return {
            "recommendation": {
                "recommended_intensity": recommended_intensity,
                "people_detected": total_people,
                "reason": (
                    "Alta demanda peatonal"
                    if total_people > 30
                    else "Demanda moderada"
                    if total_people > 10
                    else "Modo ahorro"
                ),
            }
        }
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


@app.get("/api/anomalies")
async def get_anomalies() -> dict[str, Any]:
    """Detecta anomalías simples en el estado del sistema."""
    try:
        streetlight_entities = list_entities("Streetlight")
        streetlights = streetlights_to_frontend(streetlight_entities)

        crowd_entities = list_entities("CrowdFlowObserved")
        crowds = crowd_flows_to_frontend(crowd_entities)
        total_people = 0
        for crowd in crowds:
            try:
                total_people += int(crowd.get("peopleCount") or 0)
            except (TypeError, ValueError):
                continue

        anomalies = []
        for sl in streetlights:
            try:
                intensity = float(sl.get("illuminanceLevel") or sl.get("intensity") or 0)
            except (TypeError, ValueError):
                intensity = 0

            if intensity > 80 and total_people < 5:
                anomalies.append(
                    {
                        "type": "high_intensity_low_demand",
                        "streetlight_id": sl.get("id"),
                        "intensity": intensity,
                        "people": total_people,
                    }
                )

        return {"anomalies": anomalies, "count": len(anomalies)}
    except requests.RequestException as e:
        raise HTTPException(status_code=503, detail=str(e)) from e


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
