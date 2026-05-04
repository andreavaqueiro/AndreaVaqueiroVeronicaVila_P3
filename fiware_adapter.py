#!/usr/bin/env python3
"""Adaptador FIWARE para consumo en el frontend.

Proporciona endpoints para consumir entidades FIWARE NGSI-LD
compatible con el dashboard de Leaflet.
"""

from __future__ import annotations

import json
from typing import Any, Optional
from generate_fiware_entities import (
    generate_streetlights,
    generate_streetlight_groups,
    generate_crowd_flows,
    generate_traffic_flows,
    generate_item_flows,
    generate_control_cabinets,
    generate_feeders,
    generate_streetlight_models,
)


class FIWAREAdapter:
    """Adaptador para convertir entidades FIWARE a formato consumible."""

    def __init__(self):
        """Inicializar el adaptador con todas las entidades."""
        self.streetlights = generate_streetlights()
        self.groups = generate_streetlight_groups()
        self.crowd_flows = generate_crowd_flows()
        self.traffic_flows = generate_traffic_flows()
        self.item_flows = generate_item_flows()
        self.cabinets = generate_control_cabinets()
        self.feeders = generate_feeders()
        self.models = generate_streetlight_models()

    def streetlights_to_frontend(self) -> list[dict]:
        """Convertir farolas FIWARE a formato para Leaflet."""
        result = []
        for sl in self.streetlights:
            ngsi = sl.to_ngsi_ld()
            result.append({
                "id": ngsi["id"],
                "type": ngsi["type"],
                "lat": ngsi["location"]["value"]["coordinates"][1],
                "lng": ngsi["location"]["value"]["coordinates"][0],
                "status": ngsi["status"]["value"],
                "intensity": ngsi["luminousIntensity"]["value"],
                "power": ngsi["powerConsumption"]["value"],
                "illuminanceLevel": ngsi["illuminanceLevel"]["value"],
                "powerState": ngsi["powerState"]["value"],
                "dateObserved": ngsi["dateObserved"]["value"],
                "refGroup": ngsi.get("refStreetlightGroup", {}).get("object"),
                "refCabinet": ngsi.get("refControlCabinet", {}).get("object"),
            })
        return result

    def crowd_flows_to_frontend(self) -> list[dict]:
        """Convertir flujos peatonales FIWARE a formato consumible."""
        result = []
        for cf in self.crowd_flows:
            ngsi = cf.to_ngsi_ld()
            result.append({
                "id": ngsi["id"],
                "type": ngsi["type"],
                "location": ngsi["location"]["value"]["coordinates"],
                "peopleCount": ngsi["peopleCount"]["value"],
                "occupancy": ngsi["occupancy"]["value"],
                "description": ngsi["description"]["value"],
                "dateObserved": ngsi["dateObserved"]["value"],
            })
        return result

    def traffic_flows_to_frontend(self) -> list[dict]:
        """Convertir flujos de tráfico FIWARE a formato consumible."""
        result = []
        for tf in self.traffic_flows:
            ngsi = tf.to_ngsi_ld()
            result.append({
                "id": ngsi["id"],
                "type": ngsi["type"],
                "location": ngsi["location"]["value"]["coordinates"],
                "vehicleCount": ngsi["vehicleCount"]["value"],
                "vehicleType": ngsi["vehicleType"]["value"],
                "description": ngsi["description"]["value"],
                "dateObserved": ngsi["dateObserved"]["value"],
            })
        return result

    def item_flows_to_frontend(self) -> list[dict]:
        """Convertir flujos genéricos FIWARE a formato consumible."""
        result = []
        for if_ in self.item_flows:
            ngsi = if_.to_ngsi_ld()
            result.append({
                "id": ngsi["id"],
                "type": ngsi["type"],
                "location": ngsi["location"]["value"]["coordinates"],
                "itemCount": ngsi["itemCount"]["value"],
                "itemType": ngsi["itemType"]["value"],
                "description": ngsi["description"]["value"],
                "dateObserved": ngsi["dateObserved"]["value"],
            })
        return result

    def get_streetlight_statistics(self) -> dict[str, Any]:
        """Calcular estadísticas de farolas."""
        total = len(self.streetlights)
        on_count = sum(1 for s in self.streetlights if s.status.value == "on")
        off_count = sum(1 for s in self.streetlights if s.status.value == "off")
        fault_count = sum(1 for s in self.streetlights if s.status.value == "fault")
        
        total_power = sum(s.power_consumption for s in self.streetlights if s.status.value == "on")
        total_energy = (total_power * 6) / 1000  # kWh para 6 horas

        return {
            "total": total,
            "on": on_count,
            "off": off_count,
            "fault": fault_count,
            "totalPowerConsumption": round(total_power, 2),
            "totalEnergyConsumption6h": round(total_energy, 2),
        }

    def get_group_statistics(self, group_id: str) -> dict[str, Any]:
        """Calcular estadísticas de un grupo."""
        group_lights = [s for s in self.streetlights 
                       if s.ref_streetlight_group == group_id]
        
        if not group_lights:
            return {}

        on_count = sum(1 for s in group_lights if s.status.value == "on")
        total_intensity = sum(s.luminous_intensity for s in group_lights if s.status.value == "on")
        avg_intensity = total_intensity / on_count if on_count > 0 else 0
        total_power = sum(s.power_consumption for s in group_lights if s.status.value == "on")

        return {
            "groupId": group_id,
            "total": len(group_lights),
            "on": on_count,
            "averageIntensity": round(avg_intensity, 2),
            "totalPowerConsumption": round(total_power, 2),
        }


def export_fiware_adapter_example():
    """Exportar ejemplo de adaptador FIWARE."""
    adapter = FIWAREAdapter()

    # Estructura de datos
    data = {
        "streetlights": adapter.streetlights_to_frontend(),
        "crowdFlows": adapter.crowd_flows_to_frontend(),
        "trafficFlows": adapter.traffic_flows_to_frontend(),
        "itemFlows": adapter.item_flows_to_frontend(),
        "statistics": adapter.get_streetlight_statistics(),
    }

    with open("fiware_adapter_example.json", "w") as f:
        json.dump(data, f, indent=2)

    print("💾 Adaptador FIWARE exportado a fiware_adapter_example.json")
    print()
    print("📊 Estadísticas:")
    print(json.dumps(data["statistics"], indent=2))


if __name__ == "__main__":
    export_fiware_adapter_example()
