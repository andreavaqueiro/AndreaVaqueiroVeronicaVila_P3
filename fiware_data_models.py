#!/usr/bin/env python3
"""FIWARE Smart Data Models para Iluminación Urbana Inteligente (NGSI-LD).

Implementa las entidades FIWARE según el estándar NGSI-LD:
- Streetlight
- StreetlightGroup
- StreetlightControlCabinet
- StreetlightFeeder
- StreetlightModel
- CrowdFlowObserved
- TrafficFlowObserved
- ItemFlowObserved

Fuentes:
- https://github.com/smart-data-models/dataModel.Streetlighting
- https://github.com/smart-data-models/dataModel.Transportation
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from enum import Enum


# ═══════════════════════════════════════════════════════════════════════════
# ENUMERACIONES Y TIPOS
# ═══════════════════════════════════════════════════════════════════════════

class StreetlightStatus(str, Enum):
    """Estados posibles de una farola."""
    ON = "on"
    OFF = "off"
    FAULT = "fault"
    DIMMED = "dimmed"


class PowerState(str, Enum):
    """Estados de energía."""
    NORMAL = "normal"
    LOW_POWER = "lowPower"
    FAILURE = "failure"
    MAINTENANCE = "maintenance"


# ═══════════════════════════════════════════════════════════════════════════
# CLASES BASE PARA NGSI-LD
# ═══════════════════════════════════════════════════════════════════════════

class NGSILDProperty:
    """Propiedad NGSI-LD con tipo y valor."""
    def __init__(self, value: Any, type_: str = "Property"):
        self.value = value
        self.type = type_

    def to_dict(self) -> dict:
        return {"value": self.value, "type": self.type}


class NGSILDGeoProperty:
    """Propiedad geográfica NGSI-LD (GeoJSON)."""
    def __init__(self, lon: float, lat: float):
        self.coordinates = [lon, lat]

    def to_dict(self) -> dict:
        return {
            "type": "GeoProperty",
            "value": {
                "type": "Point",
                "coordinates": self.coordinates
            }
        }


class NGSILDRelationship:
    """Relación NGSI-LD entre entidades."""
    def __init__(self, object_: str):
        self.object = object_

    def to_dict(self) -> dict:
        return {"type": "Relationship", "object": self.object}


# ═══════════════════════════════════════════════════════════════════════════
# MODELO STREETLIGHT
# ═══════════════════════════════════════════════════════════════════════════

class Streetlight:
    """Entidad FIWARE Streetlight - Farola individual."""

    def __init__(
        self,
        id_: str,
        location: tuple[float, float],  # (lon, lat)
        status: StreetlightStatus = StreetlightStatus.ON,
        power_state: PowerState = PowerState.NORMAL,
        luminous_intensity: int = 100,
        power_consumption: float = 120.0,
        illuminance_level: int = 100,
        ref_streetlight_model: Optional[str] = None,
        ref_streetlight_group: Optional[str] = None,
        ref_control_cabinet: Optional[str] = None,
        ref_feeder: Optional[str] = None,
        date_observed: Optional[str] = None,
        custom_properties: Optional[dict] = None
    ):
        """
        Inicializar una entidad Streetlight.
        
        Args:
            id_: Identificador único (ej: "urn:ngsi-ld:Streetlight:coruña:001")
            location: Tupla (longitud, latitud)
            status: Estado de la farola (on/off/fault/dimmed)
            power_state: Estado de energía (normal/lowPower/failure/maintenance)
            luminous_intensity: Intensidad luminosa (0-100%)
            power_consumption: Consumo de potencia en W
            illuminance_level: Nivel de iluminancia en lux
            ref_streetlight_model: Referencia al modelo técnico
            ref_streetlight_group: Referencia al grupo de farolas
            ref_control_cabinet: Referencia al armario de control
            ref_feeder: Referencia a la línea de alimentación
            date_observed: Fecha de observación (ISO 8601)
            custom_properties: Propiedades adicionales
        """
        self.id = id_
        self.type = "Streetlight"
        self.location = location
        self.status = status
        self.power_state = power_state
        self.luminous_intensity = luminous_intensity
        self.power_consumption = power_consumption
        self.illuminance_level = illuminance_level
        self.ref_streetlight_model = ref_streetlight_model
        self.ref_streetlight_group = ref_streetlight_group
        self.ref_control_cabinet = ref_control_cabinet
        self.ref_feeder = ref_feeder
        self.date_observed = date_observed or datetime.utcnow().isoformat() + "Z"
        self.custom_properties = custom_properties or {}

    def to_ngsi_ld(self) -> dict:
        """Convertir a formato NGSI-LD."""
        entity = {
            "id": self.id,
            "type": self.type,
            "location": NGSILDGeoProperty(self.location[0], self.location[1]).to_dict(),
            "status": NGSILDProperty(self.status.value).to_dict(),
            "powerState": NGSILDProperty(self.power_state.value).to_dict(),
            "luminousIntensity": NGSILDProperty(self.luminous_intensity).to_dict(),
            "powerConsumption": NGSILDProperty(self.power_consumption).to_dict(),
            "illuminanceLevel": NGSILDProperty(self.illuminance_level).to_dict(),
            "dateObserved": NGSILDProperty(self.date_observed).to_dict(),
        }

        # Añadir referencias si existen
        if self.ref_streetlight_model:
            entity["refStreetlightModel"] = NGSILDRelationship(
                self.ref_streetlight_model
            ).to_dict()
        if self.ref_streetlight_group:
            entity["refStreetlightGroup"] = NGSILDRelationship(
                self.ref_streetlight_group
            ).to_dict()
        if self.ref_control_cabinet:
            entity["refControlCabinet"] = NGSILDRelationship(
                self.ref_control_cabinet
            ).to_dict()
        if self.ref_feeder:
            entity["refFeeder"] = NGSILDRelationship(self.ref_feeder).to_dict()

        # Añadir propiedades personalizadas
        for key, value in self.custom_properties.items():
            entity[key] = NGSILDProperty(value).to_dict()

        return entity


# ═══════════════════════════════════════════════════════════════════════════
# MODELO STREETLIGHT GROUP
# ═══════════════════════════════════════════════════════════════════════════

class StreetlightGroup:
    """Entidad FIWARE StreetlightGroup - Grupo de farolas."""

    def __init__(
        self,
        id_: str,
        location: tuple[float, float],  # Centroide del grupo
        description: str = "",
        streetlight_ids: Optional[list[str]] = None,
        ref_control_cabinet: Optional[str] = None,
        ref_feeder: Optional[str] = None,
        power_state: PowerState = PowerState.NORMAL,
        date_observed: Optional[str] = None,
    ):
        """
        Inicializar un grupo de farolas.
        
        Args:
            id_: Identificador único
            location: Centroide del grupo (lon, lat)
            description: Descripción (ej: "Centro histórico", "Paseo Marítimo")
            streetlight_ids: Lista de IDs de farolas del grupo
            ref_control_cabinet: Referencia al armario de control
            ref_feeder: Referencia a la línea de alimentación
            power_state: Estado de energía del grupo
            date_observed: Fecha de observación
        """
        self.id = id_
        self.type = "StreetlightGroup"
        self.location = location
        self.description = description
        self.streetlight_ids = streetlight_ids or []
        self.ref_control_cabinet = ref_control_cabinet
        self.ref_feeder = ref_feeder
        self.power_state = power_state
        self.date_observed = date_observed or datetime.utcnow().isoformat() + "Z"

    def to_ngsi_ld(self) -> dict:
        """Convertir a formato NGSI-LD."""
        entity = {
            "id": self.id,
            "type": self.type,
            "location": NGSILDGeoProperty(self.location[0], self.location[1]).to_dict(),
            "description": NGSILDProperty(self.description).to_dict(),
            "powerState": NGSILDProperty(self.power_state.value).to_dict(),
            "dateObserved": NGSILDProperty(self.date_observed).to_dict(),
        }

        # Añadir lista de farolas
        if self.streetlight_ids:
            entity["hasStreetlight"] = {
                "type": "Relationship",
                "object": self.streetlight_ids
            }

        if self.ref_control_cabinet:
            entity["refControlCabinet"] = NGSILDRelationship(
                self.ref_control_cabinet
            ).to_dict()
        if self.ref_feeder:
            entity["refFeeder"] = NGSILDRelationship(self.ref_feeder).to_dict()

        return entity


# ═══════════════════════════════════════════════════════════════════════════
# MODELO STREETLIGHT CONTROL CABINET
# ═══════════════════════════════════════════════════════════════════════════

class StreetlightControlCabinet:
    """Entidad FIWARE StreetlightControlCabinet - Armario de control."""

    def __init__(
        self,
        id_: str,
        location: tuple[float, float],  # (lon, lat)
        description: str = "",
        status: StreetlightStatus = StreetlightStatus.ON,
        power_state: PowerState = PowerState.NORMAL,
        ref_feeder: Optional[str] = None,
        date_observed: Optional[str] = None,
    ):
        """
        Inicializar un armario de control.
        
        Args:
            id_: Identificador único
            location: Ubicación del armario (lon, lat)
            description: Descripción del armario
            status: Estado del armario
            power_state: Estado de energía
            ref_feeder: Referencia a la línea de alimentación
            date_observed: Fecha de observación
        """
        self.id = id_
        self.type = "StreetlightControlCabinet"
        self.location = location
        self.description = description
        self.status = status
        self.power_state = power_state
        self.ref_feeder = ref_feeder
        self.date_observed = date_observed or datetime.utcnow().isoformat() + "Z"

    def to_ngsi_ld(self) -> dict:
        """Convertir a formato NGSI-LD."""
        entity = {
            "id": self.id,
            "type": self.type,
            "location": NGSILDGeoProperty(self.location[0], self.location[1]).to_dict(),
            "description": NGSILDProperty(self.description).to_dict(),
            "status": NGSILDProperty(self.status.value).to_dict(),
            "powerState": NGSILDProperty(self.power_state.value).to_dict(),
            "dateObserved": NGSILDProperty(self.date_observed).to_dict(),
        }

        if self.ref_feeder:
            entity["refFeeder"] = NGSILDRelationship(self.ref_feeder).to_dict()

        return entity


# ═══════════════════════════════════════════════════════════════════════════
# MODELO STREETLIGHT FEEDER
# ═══════════════════════════════════════════════════════════════════════════

class StreetlightFeeder:
    """Entidad FIWARE StreetlightFeeder - Línea de alimentación."""

    def __init__(
        self,
        id_: str,
        description: str = "",
        voltage: float = 230.0,
        amperage: float = 100.0,
        power_state: PowerState = PowerState.NORMAL,
        date_observed: Optional[str] = None,
    ):
        """
        Inicializar una línea de alimentación.
        
        Args:
            id_: Identificador único
            description: Descripción de la línea
            voltage: Voltaje en V
            amperage: Amperaje en A
            power_state: Estado de energía
            date_observed: Fecha de observación
        """
        self.id = id_
        self.type = "StreetlightFeeder"
        self.description = description
        self.voltage = voltage
        self.amperage = amperage
        self.power_state = power_state
        self.date_observed = date_observed or datetime.utcnow().isoformat() + "Z"

    def to_ngsi_ld(self) -> dict:
        """Convertir a formato NGSI-LD."""
        return {
            "id": self.id,
            "type": self.type,
            "description": NGSILDProperty(self.description).to_dict(),
            "voltage": NGSILDProperty(self.voltage).to_dict(),
            "amperage": NGSILDProperty(self.amperage).to_dict(),
            "powerState": NGSILDProperty(self.power_state.value).to_dict(),
            "dateObserved": NGSILDProperty(self.date_observed).to_dict(),
        }


# ═══════════════════════════════════════════════════════════════════════════
# MODELO STREETLIGHT MODEL
# ═══════════════════════════════════════════════════════════════════════════

class StreetlightModel:
    """Entidad FIWARE StreetlightModel - Modelo técnico de farola."""

    def __init__(
        self,
        id_: str,
        description: str = "",
        brand: str = "",
        model_name: str = "",
        lamp_type: str = "LED",
        luminous_flux: int = 3000,
        color_temperature: int = 4000,
        life_expectancy: int = 50000,
        date_observed: Optional[str] = None,
    ):
        """
        Inicializar un modelo de farola.
        
        Args:
            id_: Identificador único
            description: Descripción del modelo
            brand: Marca del fabricante
            model_name: Nombre del modelo
            lamp_type: Tipo de lámpara (LED, HPS, etc.)
            luminous_flux: Flujo luminoso en lúmenes
            color_temperature: Temperatura de color en K
            life_expectancy: Vida esperada en horas
            date_observed: Fecha de observación
        """
        self.id = id_
        self.type = "StreetlightModel"
        self.description = description
        self.brand = brand
        self.model_name = model_name
        self.lamp_type = lamp_type
        self.luminous_flux = luminous_flux
        self.color_temperature = color_temperature
        self.life_expectancy = life_expectancy
        self.date_observed = date_observed or datetime.utcnow().isoformat() + "Z"

    def to_ngsi_ld(self) -> dict:
        """Convertir a formato NGSI-LD."""
        return {
            "id": self.id,
            "type": self.type,
            "description": NGSILDProperty(self.description).to_dict(),
            "brand": NGSILDProperty(self.brand).to_dict(),
            "modelName": NGSILDProperty(self.model_name).to_dict(),
            "lampType": NGSILDProperty(self.lamp_type).to_dict(),
            "luminousFlux": NGSILDProperty(self.luminous_flux).to_dict(),
            "colorTemperature": NGSILDProperty(self.color_temperature).to_dict(),
            "lifeExpectancy": NGSILDProperty(self.life_expectancy).to_dict(),
            "dateObserved": NGSILDProperty(self.date_observed).to_dict(),
        }


# ═══════════════════════════════════════════════════════════════════════════
# MODELO CROWD FLOW OBSERVED
# ═══════════════════════════════════════════════════════════════════════════

class CrowdFlowObserved:
    """Entidad FIWARE CrowdFlowObserved - Flujo de peatones observado."""

    def __init__(
        self,
        id_: str,
        location: tuple[float, float],  # (lon, lat)
        people_count: int = 0,
        occupancy: float = 0.0,
        max_occupancy: int = 1000,
        ref_streetlight_group: Optional[str] = None,
        description: str = "",
        date_observed: Optional[str] = None,
    ):
        """
        Inicializar un flujo de peatones observado.
        
        Args:
            id_: Identificador único
            location: Ubicación de la observación (lon, lat)
            people_count: Cantidad de personas
            occupancy: Ocupación relativa (0-1)
            max_occupancy: Ocupación máxima esperada
            ref_streetlight_group: Referencia al grupo de farolas cercano
            description: Descripción de la zona
            date_observed: Fecha de observación
        """
        self.id = id_
        self.type = "CrowdFlowObserved"
        self.location = location
        self.people_count = people_count
        self.occupancy = occupancy
        self.max_occupancy = max_occupancy
        self.ref_streetlight_group = ref_streetlight_group
        self.description = description
        self.date_observed = date_observed or datetime.utcnow().isoformat() + "Z"

    def to_ngsi_ld(self) -> dict:
        """Convertir a formato NGSI-LD."""
        entity = {
            "id": self.id,
            "type": self.type,
            "location": NGSILDGeoProperty(self.location[0], self.location[1]).to_dict(),
            "peopleCount": NGSILDProperty(self.people_count).to_dict(),
            "occupancy": NGSILDProperty(self.occupancy).to_dict(),
            "maxOccupancy": NGSILDProperty(self.max_occupancy).to_dict(),
            "description": NGSILDProperty(self.description).to_dict(),
            "dateObserved": NGSILDProperty(self.date_observed).to_dict(),
        }

        if self.ref_streetlight_group:
            entity["refStreetlightGroup"] = NGSILDRelationship(
                self.ref_streetlight_group
            ).to_dict()

        return entity


# ═══════════════════════════════════════════════════════════════════════════
# MODELO TRAFFIC FLOW OBSERVED
# ═══════════════════════════════════════════════════════════════════════════

class TrafficFlowObserved:
    """Entidad FIWARE TrafficFlowObserved - Flujo de tráfico observado."""

    def __init__(
        self,
        id_: str,
        location: tuple[float, float],  # (lon, lat)
        vehicle_count: int = 0,
        vehicle_type: str = "mixed",
        ref_streetlight_group: Optional[str] = None,
        description: str = "",
        date_observed: Optional[str] = None,
    ):
        """
        Inicializar un flujo de tráfico observado.
        
        Args:
            id_: Identificador único
            location: Ubicación de la observación (lon, lat)
            vehicle_count: Cantidad de vehículos
            vehicle_type: Tipo de vehículo (car, bus, truck, mixed, etc.)
            ref_streetlight_group: Referencia al grupo de farolas cercano
            description: Descripción de la zona
            date_observed: Fecha de observación
        """
        self.id = id_
        self.type = "TrafficFlowObserved"
        self.location = location
        self.vehicle_count = vehicle_count
        self.vehicle_type = vehicle_type
        self.ref_streetlight_group = ref_streetlight_group
        self.description = description
        self.date_observed = date_observed or datetime.utcnow().isoformat() + "Z"

    def to_ngsi_ld(self) -> dict:
        """Convertir a formato NGSI-LD."""
        entity = {
            "id": self.id,
            "type": self.type,
            "location": NGSILDGeoProperty(self.location[0], self.location[1]).to_dict(),
            "vehicleCount": NGSILDProperty(self.vehicle_count).to_dict(),
            "vehicleType": NGSILDProperty(self.vehicle_type).to_dict(),
            "description": NGSILDProperty(self.description).to_dict(),
            "dateObserved": NGSILDProperty(self.date_observed).to_dict(),
        }

        if self.ref_streetlight_group:
            entity["refStreetlightGroup"] = NGSILDRelationship(
                self.ref_streetlight_group
            ).to_dict()

        return entity


# ═══════════════════════════════════════════════════════════════════════════
# MODELO ITEM FLOW OBSERVED
# ═══════════════════════════════════════════════════════════════════════════

class ItemFlowObserved:
    """Entidad FIWARE ItemFlowObserved - Flujo genérico de elementos."""

    def __init__(
        self,
        id_: str,
        location: tuple[float, float],  # (lon, lat)
        item_count: int = 0,
        item_type: str = "generic",
        ref_streetlight_group: Optional[str] = None,
        description: str = "",
        date_observed: Optional[str] = None,
    ):
        """
        Inicializar un flujo de elementos observado.
        
        Args:
            id_: Identificador único
            location: Ubicación de la observación (lon, lat)
            item_count: Cantidad de elementos
            item_type: Tipo de elemento (generic, person, vehicle, bike, etc.)
            ref_streetlight_group: Referencia al grupo de farolas cercano
            description: Descripción de la zona
            date_observed: Fecha de observación
        """
        self.id = id_
        self.type = "ItemFlowObserved"
        self.location = location
        self.item_count = item_count
        self.item_type = item_type
        self.ref_streetlight_group = ref_streetlight_group
        self.description = description
        self.date_observed = date_observed or datetime.utcnow().isoformat() + "Z"

    def to_ngsi_ld(self) -> dict:
        """Convertir a formato NGSI-LD."""
        entity = {
            "id": self.id,
            "type": self.type,
            "location": NGSILDGeoProperty(self.location[0], self.location[1]).to_dict(),
            "itemCount": NGSILDProperty(self.item_count).to_dict(),
            "itemType": NGSILDProperty(self.item_type).to_dict(),
            "description": NGSILDProperty(self.description).to_dict(),
            "dateObserved": NGSILDProperty(self.date_observed).to_dict(),
        }

        if self.ref_streetlight_group:
            entity["refStreetlightGroup"] = NGSILDRelationship(
                self.ref_streetlight_group
            ).to_dict()

        return entity
