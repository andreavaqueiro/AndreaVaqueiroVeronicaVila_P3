#!/usr/bin/env python3
"""Mock de Orion Context Broker y QuantumLeap para pruebas sin Docker.

Simula las funcionalidades mínimas de Orion NGSI-LD y QuantumLeap
para validar los scripts de provisión y simulación en entorno local.

Carga entidades FIWARE reales desde generate_fiware_entities.py
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)

# Habilitar CORS para todas las rutas
CORS(app, resources={r"/*": {"origins": "*"}})

# Almacenamiento en memoria (sustituye a MongoDB)
entities_store: dict[str, dict] = {}
historical_store: dict[str, list] = {}


def initialize_fiware_entities() -> int:
    """Inicializa entidades FIWARE desde el generador.
    
    Returns:
        int: Número de entidades cargadas
    """
    try:
        from generate_fiware_entities import generate_all_entities
        
        entities = generate_all_entities()
        total_count = 0
        
        for entity_type, entity_list in entities.items():
            for entity in entity_list:
                entity_id = entity.get("id")
                if entity_id:
                    entities_store[entity_id] = entity
                    total_count += 1
        
        print(f"✅ Cargadas {total_count} entidades FIWARE NGSI-LD")
        
        # Resumen por tipo
        type_counts = {}
        for entity in entities_store.values():
            entity_type = entity.get("type", "Unknown")
            type_counts[entity_type] = type_counts.get(entity_type, 0) + 1
        
        print("\n📊 Distribución de entidades:")
        for entity_type, count in sorted(type_counts.items()):
            print(f"   - {entity_type}: {count}")
        print()
        
        return total_count
    
    except Exception as e:
        print(f"❌ Error inicializando FIWARE: {e}")
        return 0


@app.route("/health", methods=["GET"])
def health() -> dict[str, str]:
    """Health check."""
    return {"status": "ok"}


@app.route("/ngsi-ld/v1/entities", methods=["POST"])
def create_entity() -> tuple[dict[str, Any], int]:
    """Crea una nueva entidad NGSI-LD."""
    try:
        data = request.get_json()
        entity_id = data.get("id")

        if not entity_id:
            return {"error": "Missing entity id"}, 400

        if entity_id in entities_store:
            return {"error": f"Entity {entity_id} already exists"}, 409

        entities_store[entity_id] = data
        print(f"[CREATED] {entity_id}")
        return {}, 201

    except Exception as e:
        return {"error": str(e)}, 400


@app.route("/ngsi-ld/v1/entities", methods=["GET"])
def list_entities() -> dict[str, Any]:
    """Lista entidades filtradas por tipo."""
    entity_type = request.args.get("type")
    
    if entity_type:
        filtered = [
            e for e in entities_store.values() if e.get("type") == entity_type
        ]
        return jsonify(filtered)
    
    return jsonify(list(entities_store.values()))


@app.route("/ngsi-ld/v1/entities/<path:entity_id>/attrs", methods=["PATCH"])
def update_entity_attrs(entity_id: str) -> tuple[dict[str, Any], int]:
    """Actualiza atributos de una entidad (simula PATCH)."""
    try:
        # Decodificar ID URI-encoded
        from urllib.parse import unquote
        entity_id = unquote(entity_id)
        
        if entity_id not in entities_store:
            return {"error": f"Entity {entity_id} not found"}, 404

        data = request.get_json()
        
        # Simular actualización de atributos dinámicos
        for key, value in data.items():
            entities_store[entity_id][key] = value

        # Guardar en histórico para QuantumLeap
        if entity_id not in historical_store:
            historical_store[entity_id] = []

        historical_store[entity_id].append(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "attrs": data,
            }
        )

        print(f"[UPDATED] {entity_id}: {list(data.keys())}")
        return {}, 204

    except Exception as e:
        return {"error": str(e)}, 400


@app.route("/v2/entities/<path:entity_id>/attrs/<attr_name>", methods=["GET"])
def get_historical_attr(entity_id: str, attr_name: str) -> dict[str, Any]:
    """Simula QuantumLeap: devuelve histórico de un atributo."""
    from urllib.parse import unquote
    entity_id = unquote(entity_id)
    
    if entity_id not in historical_store:
        return jsonify({"values": []})

    values = []
    for entry in historical_store[entity_id]:
        attrs = entry.get("attrs", {})
        if attr_name in attrs:
            attr_value = attrs[attr_name].get("value")
            values.append([entry["timestamp"], attr_value])

    return jsonify({"values": values})


if __name__ == "__main__":
    port = 8000
    print(f"🔌 Mock Orion + QuantumLeap iniciado en http://localhost:{port}")
    print("   Use CTRL+C para detener\n")
    
    # Cargar entidades FIWARE en startup
    initialize_fiware_entities()
    
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
