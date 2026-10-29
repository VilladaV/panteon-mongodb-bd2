"""Añade ``especie_original`` a ``species`` y ``sequences``.

La llave de cruce sigue siendo ``especie``, sin puntos. El campo nuevo conserva
el nombre tal como aparece en el encabezado del FASTA y se usa solo para
exportar bibliotecas. En PanTEon v1.6.1 solo cuatro nombres difieren; el archivo
``especies_originales.csv`` contiene ese mapeo.

Uso:
    python database/migrar_especie_original.py
"""

from __future__ import annotations

import csv
from pathlib import Path

from pymongo import MongoClient

BASE = Path(__file__).resolve().parent
MAPEO = BASE / "especies_originales.csv"
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "panteon_db"


def main() -> None:
    with MAPEO.open(encoding="utf-8-sig", newline="") as archivo:
        diferencias = {
            fila["especie"]: fila["especie_original"] for fila in csv.DictReader(archivo)
        }

    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    # Primero se copia la llave normalizada; así todos los documentos tienen el campo.
    db.species.update_many(
        {"especie_original": {"$exists": False}},
        [{"$set": {"especie_original": "$especie"}}],
    )
    db.sequences.update_many(
        {"especie_original": {"$exists": False}},
        [{"$set": {"especie_original": "$especie"}}],
    )

    # Luego se corrigen los cuatro nombres que llevan punto en el FASTA.
    for especie, original in diferencias.items():
        db.species.update_many(
            {"especie": especie}, {"$set": {"especie_original": original}}
        )
        db.sequences.update_many(
            {"especie": especie}, {"$set": {"especie_original": original}}
        )

    print(f"Especies corregidas: {len(diferencias)}")
    print(f"species con el campo: {db.species.count_documents({'especie_original': {'$exists': True}})}")
    print(f"sequences con el campo: {db.sequences.count_documents({'especie_original': {'$exists': True}})}")
    client.close()


if __name__ == "__main__":
    main()
