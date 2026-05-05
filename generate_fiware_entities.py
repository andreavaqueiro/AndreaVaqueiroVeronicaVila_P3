#!/usr/bin/env python3
"""Generación de entidades FIWARE (NGSI-LD) — solo carga inicial.

Este repo tiene un único pipeline de datos: `simulator.py`.

Este script se mantiene únicamente por compatibilidad/uso puntual para:
- volcar (dump) la topología base a JSON, o
- cargar (load) la topología base en Orion UNA VEZ.

Importante:
- No debe usarse desde endpoints HTTP ni para generar datos “on demand”.
- La simulación en el tiempo se hace con `python3 simulator.py run`.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from typing import Any


def generate_all_entities(streetlights: int = 40, seed: int = 42) -> dict[str, list[dict[str, Any]]]:
    """Genera la topología base (sin side-effects) agrupada por tipo."""
    from simulator import build_topology

    _ids, entities = build_topology(streetlight_count=streetlights, seed=seed)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for ent in entities:
        t = ent.get("type")
        if isinstance(t, str):
            grouped[t].append(ent)
    return dict(grouped)


def dump_entities(path: str, streetlights: int, seed: int) -> None:
    data = generate_all_entities(streetlights=streetlights, seed=seed)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    total = sum(len(v) for v in data.values())
    print(f"💾 Dump generado: {path} ({total} entidades)")


def load_entities(streetlights: int, seed: int, reset: bool) -> None:
    """Carga la topología base en Orion (delegando en el simulador unificado)."""
    from simulator import init_topology

    init_topology(streetlight_count=streetlights, seed=seed, reset=reset)
    print("✅ Topología base cargada en Orion")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Generador (one-shot) de entidades NGSI-LD (delegado a simulator.py)")
    sub = p.add_subparsers(dest="cmd", required=True)

    dump_p = sub.add_parser("dump", help="Vuelca la topología base a un JSON")
    dump_p.add_argument("--output", default="fiware_entities.json", help="Ruta de salida (default: fiware_entities.json)")
    dump_p.add_argument("--streetlights", type=int, default=40, help="Número de farolas (default: 40)")
    dump_p.add_argument("--seed", type=int, default=42, help="Semilla (default: 42)")

    load_p = sub.add_parser("load", help="Carga inicial en Orion (POST /ngsi-ld/v1/entities)")
    load_p.add_argument("--streetlights", type=int, default=40, help="Número de farolas (default: 40)")
    load_p.add_argument("--seed", type=int, default=42, help="Semilla (default: 42)")
    load_p.add_argument("--reset", action="store_true", help="Borra primero las entidades del escenario")

    return p


def main() -> int:
    args = build_arg_parser().parse_args()

    if args.cmd == "dump":
        dump_entities(args.output, streetlights=args.streetlights, seed=args.seed)
        return 0

    if args.cmd == "load":
        load_entities(streetlights=args.streetlights, seed=args.seed, reset=args.reset)
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
