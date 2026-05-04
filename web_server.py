#!/usr/bin/env python3
"""Servidor web para servir dashboard HTML y proxy APIs FIWARE."""

from __future__ import annotations

import os
from pathlib import Path

import requests
from flask import Flask, jsonify

app = Flask(__name__)

# URL del Mock Orion
ORION_BASE_URL = os.getenv("ORION_BASE_URL", "http://localhost:8000")

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
        resp = requests.get(f"{ORION_BASE_URL}/health", timeout=2)
        if resp.status_code == 200:
            return {"status": "ok", "orion": ORION_BASE_URL}
    except Exception:
        pass
    return {"status": "error", "orion": ORION_BASE_URL}, 503

@app.route("/api/streetlights/fiware")
def get_streetlights_fiware() -> dict:
    """Obtener farolas FIWARE adaptadas para Leaflet."""
    try:
        from fiware_adapter import FIWAREAdapter
        
        adapter = FIWAREAdapter()
        return jsonify({
            "data": adapter.streetlights_to_frontend(),
            "stats": adapter.get_streetlight_statistics()
        })
    except Exception as e:
        return {"error": str(e)}, 400

@app.route("/api/crowd-flows/fiware")
def get_crowd_flows_fiware() -> dict:
    """Obtener flujos peatonales FIWARE."""
    try:
        from fiware_adapter import FIWAREAdapter
        
        adapter = FIWAREAdapter()
        return jsonify(adapter.crowd_flows_to_frontend())
    except Exception as e:
        return {"error": str(e)}, 400

@app.route("/api/traffic-flows/fiware")
def get_traffic_flows_fiware() -> dict:
    """Obtener flujos de tráfico FIWARE."""
    try:
        from fiware_adapter import FIWAREAdapter
        
        adapter = FIWAREAdapter()
        return jsonify(adapter.traffic_flows_to_frontend())
    except Exception as e:
        return {"error": str(e)}, 400

@app.route("/api/group-stats/<group_id>")
def get_group_stats(group_id: str) -> dict:
    """Obtener estadísticas de un grupo específico."""
    try:
        from fiware_adapter import FIWAREAdapter
        
        adapter = FIWAREAdapter()
        return jsonify(adapter.get_group_statistics(group_id))
    except Exception as e:
        return {"error": str(e)}, 400

if __name__ == "__main__":
    print("🌐 Servidor Web iniciado en http://localhost:3000")
    print("   Dashboard: http://localhost:3000")
    print(f"   FIWARE Orion: {ORION_BASE_URL}")
    print()
    app.run(host="0.0.0.0", port=3000, debug=False)
