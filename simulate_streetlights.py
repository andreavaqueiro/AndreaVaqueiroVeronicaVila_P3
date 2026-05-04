#!/usr/bin/env python3
"""Simula cambios dinámicos de estado en farolas (para visualización).

Actualiza:
- Estados (on/off/fault)
- Intensidad lumínica según demanda de peatones
- Consumo de potencia
- Timestamps de última actualización
"""

from __future__ import annotations

import os
import sys
import random
import time
from datetime import datetime
from typing import Dict, List

import requests

ORION_BASE_URL = os.getenv("ORION_BASE_URL", "http://localhost:1026").rstrip("/")
SIM_ITERATIONS = int(os.getenv("SIM_ITERATIONS", 10))
SIM_SLEEP_SECONDS = int(os.getenv("SIM_SLEEP_SECONDS", 2))

HEADERS_LD_JSON = {
    "Content-Type": "application/ld+json",
    "Accept": "application/ld+json",
}


def get_all_streetlights() -> List[Dict]:
    """Obtiene todas las farolas actuales."""
    url = f"{ORION_BASE_URL}/ngsi-ld/v1/entities?type=Streetlight"
    try:
        resp = requests.get(url, headers=HEADERS_LD_JSON, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return []
    except Exception as e:
        print(f"Error obteniendo farolas: {e}")
        return []


def update_streetlight(sl_id: str, updates: Dict) -> bool:
    """Actualiza atributos de una farola."""
    url = f"{ORION_BASE_URL}/ngsi-ld/v1/entities/{sl_id}/attrs"
    
    try:
        resp = requests.patch(url, headers=HEADERS_LD_JSON, json=updates, timeout=10)
        return resp.status_code in (200, 204)
    except Exception as e:
        print(f"Error actualizando {sl_id}: {e}")
        return False


def get_all_crowd_flows() -> List[Dict]:
    """Obtiene todos los observadores de flujo peatonal."""
    url = f"{ORION_BASE_URL}/ngsi-ld/v1/entities?type=CrowdFlowObserved"
    try:
        resp = requests.get(url, headers=HEADERS_LD_JSON, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return []
    except Exception as e:
        print(f"Error obteniendo flujos: {e}")
        return []


def simulate_iteration(iteration: int) -> None:
    """Simula una iteración de cambios en farolas y peatones."""
    
    # Obtener flujos de peatones y calcular demanda
    crowds = get_all_crowd_flows()
    total_people = random.randint(0, 50)
    
    # Determinar intensidad recomendada según peatones
    if total_people > 30:
        base_intensity = 100
        reason = "Alta demanda peatonal"
    elif total_people > 10:
        base_intensity = 60
        reason = "Demanda moderada"
    else:
        base_intensity = 20
        reason = "Modo ahorro"
    
    print(f"[Iteración {iteration+1}] Peatones: {total_people}, Intensidad base: {base_intensity}%, Razón: {reason}")
    
    # Actualizar flujos de peatones
    for crowd in crowds:
        crowd_people = random.randint(0, total_people)
        updates = {
            "peopleCount": {
                "type": "Property",
                "value": crowd_people
            },
            "occupancy": {
                "type": "Property",
                "value": min(crowd_people / 50, 1.0)
            }
        }
        update_streetlight(crowd['id'], updates)
    
    # Actualizar farolas
    streetlights = get_all_streetlights()
    
    for sl in streetlights:
        # Probabilidad de fallos aleatorios (1%)
        rand = random.random()
        
        if rand < 0.01:
            # Simular fallo
            new_status = "fault"
            new_intensity = random.randint(0, 30)
        elif rand < 0.05:
            # Simular apagado
            new_status = "off"
            new_intensity = 0
        else:
            # Funcionamiento normal
            new_status = "on"
            # Variar intensidad alrededor de la base
            variation = random.randint(-10, 10)
            new_intensity = max(0, min(100, base_intensity + variation))
        
        # Calcular consumo
        current_power = new_intensity * 0.75 if new_status == "on" else 0
        
        # Preparer actualización
        updates = {
            "status": {
                "type": "Property",
                "value": new_status
            },
            "illuminanceLevel": {
                "type": "Property",
                "value": new_intensity,
                "unitCode": "P1"
            },
            "powerConsumption": {
                "type": "Property",
                "value": current_power,
                "unitCode": "W"
            },
            "lastUpdate": {
                "type": "Property",
                "value": datetime.utcnow().isoformat() + "Z"
            }
        }
        
        update_streetlight(sl['id'], updates)
    
    # Dormir entre iteraciones
    time.sleep(SIM_SLEEP_SECONDS)


def main() -> int:
    print(f"Usando ORION_BASE_URL={ORION_BASE_URL}")
    print(f"Simulando {SIM_ITERATIONS} iteraciones con {SIM_SLEEP_SECONDS}s entre cada una")
    print("")
    
    try:
        for i in range(SIM_ITERATIONS):
            simulate_iteration(i)
    except KeyboardInterrupt:
        print("\n\nSimulación interrumpida por usuario")
        return 0
    
    print("\nSimulación finalizada.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except requests.RequestException as exc:
        print(f"Error de red o HTTP: {exc}", file=sys.stderr)
        raise SystemExit(1)
