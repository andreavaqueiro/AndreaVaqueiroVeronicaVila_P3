#!/usr/bin/env python3
"""Servidor web para servir dashboard HTML y exponer APIs leídas desde Orion.

Nota: Este servidor NO genera datos. Orion-LD es la fuente única de verdad.
"""

from __future__ import annotations

import os
from pathlib import Path

import requests
from flask import Flask, jsonify

app = Flask(__name__)

# URL de Orion-LD (NGSI-LD)
ORION_BASE_URL = os.getenv("ORION_BASE_URL", "http://localhost:1026").rstrip("/")

@app.route("/")
def index() -> tuple[str, int]:
    """Sirve el dashboard HTML."""
    # Intentar servir el dashboard.html (nuevo)
    html_path = Path(__file__).parent / "dashboard.html"
    if not html_path.exists():
        # Fallback a index.html (viejo)
        html_path = Path(__file__).parent / "index.html"
    
    if html_path.exists():
        with open(html_path) as f:
            return f.read(), 200
    return "Dashboard no encontrado", 404

@app.route("/health")
def health() -> dict[str, str]:
    """Health check."""
    return {"status": "ok"}

@app.route("/api/fiware/health")
def fiware_health() -> dict[str, str]:
    """Verificar conexión con Orion."""
    try:
        from orion_client import orion_health

        if orion_health(timeout_s=2.0):
            return {"status": "ok", "orion": ORION_BASE_URL}
    except Exception:
        pass
    return {"status": "error", "orion": ORION_BASE_URL}, 503

@app.route("/api/streetlights/fiware")
def get_streetlights_fiware() -> dict:
    """Obtener farolas FIWARE adaptadas para Leaflet."""
    try:
        from orion_client import list_entities, streetlights_to_frontend, streetlight_stats

        entities = list_entities("Streetlight")
        data = streetlights_to_frontend(entities)
        return jsonify({"data": data, "stats": streetlight_stats(data)})
    except Exception as e:
        return {"error": str(e)}, 400

@app.route("/api/crowd-flows/fiware")
def get_crowd_flows_fiware() -> dict:
    """Obtener flujos peatonales FIWARE."""
    try:
        from orion_client import crowd_flows_to_frontend, list_entities

        entities = list_entities("CrowdFlowObserved")
        return jsonify(crowd_flows_to_frontend(entities))
    except Exception as e:
        return {"error": str(e)}, 400

@app.route("/api/traffic-flows/fiware")
def get_traffic_flows_fiware() -> dict:
    """Obtener flujos de tráfico FIWARE."""
    try:
        return {"error": "Not implemented in FIWARE-only mode"}, 501
    except Exception as e:
        return {"error": str(e)}, 400

@app.route("/api/group-stats/<group_id>")
def get_group_stats(group_id: str) -> dict:
    """Obtener estadísticas de un grupo específico."""
    try:
        return {"error": "Not implemented in FIWARE-only mode"}, 501
    except Exception as e:
        return {"error": str(e)}, 400

if __name__ == "__main__":
    print("🌐 Servidor Web iniciado en http://localhost:3000")
    print("   Dashboard: http://localhost:3000")
    print(f"   FIWARE Orion: {ORION_BASE_URL}")
    print()
    app.run(host="0.0.0.0", port=3000, debug=False)
