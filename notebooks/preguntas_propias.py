"""Cálculo reproducible de las dos preguntas propias.

Uso, con MongoDB activo y la base cargada:

    python notebooks/preguntas_propias.py

El script imprime las tablas y los rankings que se reportan en la sección IV-E del
artículo. La pregunta 1 usa `sequences` + `species` y se repite solo con Animalia para
separar el efecto del reino; la pregunta 2 reutiliza la agregación de la Figura 4
(`kmers` con k = 2), calcula rangos y correlaciones en Python y conserva el tamaño de
muestra de los órdenes que fijan los extremos.
"""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations

import numpy as np
from pymongo import MongoClient

from visualizaciones import DINUCLEOTIDOS, figura_04_dinucleotidos

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "panteon_db"


def pregunta_1(db, kingdom: str | None = None) -> dict[str, object]:
    """Composición por orden dentro de cada `library_origin.source`.

    Si se pasa ``kingdom``, la comparación se restringe a ese reino. Sirve para
    repetir Dfam frente a RM2+MCH dentro de Animalia, donde ambas fuentes tienen
    datos y el reino deja de ser una covariable.
    """

    pipeline = [
        {
            "$lookup": {
                "from": "species",
                "localField": "species_id",
                "foreignField": "_id",
                "as": "sp",
            }
        },
        {"$unwind": {"path": "$sp", "preserveNullAndEmptyArrays": True}},
    ]
    if kingdom is not None:
        pipeline.append({"$match": {"sp.taxonomy.kingdom": kingdom}})
    pipeline += [
        {
            "$group": {
                "_id": {
                    "source": "$sp.library_origin.source",
                    "orden": "$te_classification.orden_fasta",
                },
                "n": {"$sum": 1},
            }
        },
        {
            "$group": {
                "_id": "$_id.source",
                "total": {"$sum": "$n"},
                "ordenes": {"$push": {"orden": "$_id.orden", "n": "$n"}},
            }
        },
        {"$unwind": "$ordenes"},
        {
            "$project": {
                "_id": 0,
                "source": "$_id",
                "orden": "$ordenes.orden",
                "n": "$ordenes.n",
                "pct": {
                    "$multiply": [
                        {"$divide": ["$ordenes.n", "$total"]},
                        100,
                    ]
                },
            }
        },
        {"$sort": {"source": 1, "pct": -1}},
    ]
    filas = list(db["sequences"].aggregate(pipeline, allowDiskUse=True))
    totales = defaultdict(int)
    especies = defaultdict(set)
    for fila in filas:
        totales[fila["source"]] += fila["n"]

    por_reino = list(
        db["sequences"].aggregate(
            [
                {
                    "$lookup": {
                        "from": "species",
                        "localField": "species_id",
                        "foreignField": "_id",
                        "as": "sp",
                    }
                },
                {"$unwind": {"path": "$sp", "preserveNullAndEmptyArrays": True}},
                {
                    "$group": {
                        "_id": {
                            "source": "$sp.library_origin.source",
                            "kingdom": "$kingdom",
                        },
                        "n": {"$sum": 1},
                    }
                },
                {"$sort": {"_id.source": 1, "n": -1}},
            ],
            allowDiskUse=True,
        )
    )

    # Conteo de especies por fuente, sin depender del tamaño de la muestra.
    for doc in db["sequences"].aggregate(
        [
            {
                "$lookup": {
                    "from": "species",
                    "localField": "species_id",
                    "foreignField": "_id",
                    "as": "sp",
                }
            },
            {"$unwind": {"path": "$sp", "preserveNullAndEmptyArrays": True}},
            {
                "$group": {
                    "_id": {
                        "source": "$sp.library_origin.source",
                        "species_id": "$species_id",
                    }
                }
            },
        ],
        allowDiskUse=True,
    ):
        especies[doc["_id"]["source"]].add(doc["_id"]["species_id"])

    return {
        "filas": filas,
        "por_reino": por_reino,
        "totales": dict(totales),
        "especies": {k: len(v) for k, v in especies.items()},
    }


def pregunta_1_especies(db) -> list[dict]:
    """Composición por orden dentro de cada fuente, solo con `es_especie = true`.

    Reproduce la restricción que se cita en la §IV-E: elimina los 44 grupos
    taxonómicos que no son especie antes de agrupar.
    """

    pipeline = [
        {
            "$lookup": {
                "from": "species",
                "localField": "species_id",
                "foreignField": "_id",
                "as": "sp",
            }
        },
        {"$unwind": {"path": "$sp", "preserveNullAndEmptyArrays": True}},
        {"$match": {"sp.es_especie": True}},
        {
            "$group": {
                "_id": {
                    "source": "$sp.library_origin.source",
                    "orden": "$te_classification.orden_fasta",
                },
                "n": {"$sum": 1},
            }
        },
        {
            "$group": {
                "_id": "$_id.source",
                "total": {"$sum": "$n"},
                "ordenes": {"$push": {"orden": "$_id.orden", "n": "$n"}},
            }
        },
        {"$unwind": "$ordenes"},
        {
            "$project": {
                "_id": 0,
                "source": "$_id",
                "orden": "$ordenes.orden",
                "n": "$ordenes.n",
                "pct": {
                    "$multiply": [
                        {"$divide": ["$ordenes.n", "$total"]},
                        100,
                    ]
                },
            }
        },
        {"$sort": {"source": 1, "pct": -1}},
    ]
    return list(db["sequences"].aggregate(pipeline, allowDiskUse=True))


def pregunta_2(db, modo_prueba: bool = False) -> dict[str, object]:
    """Matriz orden × dinucleótido, rangos y correlaciones."""

    datos = figura_04_dinucleotidos(db, modo_prueba)["datos"]
    matriz: dict[str, np.ndarray] = {}
    tamanos: dict[str, int] = {}
    for fila in datos:
        matriz.setdefault(fila["orden"], np.zeros(len(DINUCLEOTIDOS)))
        tamanos[fila["orden"]] = int(fila["secuencias_validas"])
        j = DINUCLEOTIDOS.index(fila["dinucleotido"])
        matriz[fila["orden"]][j] = fila["frecuencia_promedio"]

    ordenes = list(matriz)
    rangos = []
    for j, dinucleotido in enumerate(DINUCLEOTIDOS):
        valores = np.array([matriz[o][j] for o in ordenes])
        rango = float(valores.max() - valores.min())
        media = float(valores.mean())
        i_min = int(valores.argmin())
        i_max = int(valores.argmax())
        rangos.append(
            {
                "dinucleotido": dinucleotido,
                "rango": rango,
                "rango_relativo": rango / media if media else 0.0,
                "media": media,
                "orden_min": ordenes[i_min],
                "min": float(valores[i_min]),
                "n_orden_min": tamanos.get(ordenes[i_min], 0),
                "orden_max": ordenes[i_max],
                "max": float(valores[i_max]),
                "n_orden_max": tamanos.get(ordenes[i_max], 0),
            }
        )

    correlaciones = []
    for a, b in combinations(matriz, 2):
        correlaciones.append(
            {
                "a": a,
                "b": b,
                "r": float(np.corrcoef(matriz[a], matriz[b])[0, 1]),
            }
        )

    return {
        "matriz": {k: v.tolist() for k, v in matriz.items()},
        "rangos": sorted(rangos, key=lambda x: x["rango"], reverse=True),
        "correlaciones": sorted(correlaciones, key=lambda x: x["r"], reverse=True),
        "tamanos": tamanos,
    }


def main() -> None:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    q1 = pregunta_1(db)
    print("Pregunta 1 · Source × orden")
    for fila in q1["filas"]:
        print(
            f"{fila['source']:10s} {fila['orden']:12s} "
            f"{fila['n']:7d} {fila['pct']:6.2f}%"
        )
    print("Totales:", q1["totales"])
    print("Especies:", q1["especies"])
    print("Source × reino")
    for fila in q1["por_reino"]:
        print(f"{fila['_id']['source']:10s} {fila['_id']['kingdom']:10s} {fila['n']:7d}")

    print("\nPregunta 1 · solo es_especie = true")
    for fila in pregunta_1_especies(db):
        print(
            f"{fila['source']:10s} {fila['orden']:12s} "
            f"{fila['n']:7d} {fila['pct']:6.2f}%"
        )

    q1_animalia = pregunta_1(db, kingdom="Animalia")
    print("\nPregunta 1 · solo Animalia")
    for fila in q1_animalia["filas"]:
        print(
            f"{fila['source']:10s} {fila['orden']:12s} "
            f"{fila['n']:7d} {fila['pct']:6.2f}%"
        )
    print("Totales Animalia:", q1_animalia["totales"])
    print("Especies Animalia:", q1_animalia["especies"])

    q2 = pregunta_2(db, modo_prueba=False)
    print("\nPregunta 2 · rango por dinucleótido")
    for fila in q2["rangos"]:
        print(
            f"{fila['dinucleotido']}  R={fila['rango']:.4f}  "
            f"RR={fila['rango_relativo']:.4f}  "
            f"min={fila['orden_min']} ({fila['min']:.4f}, "
            f"n={fila['n_orden_min']})  "
            f"max={fila['orden_max']} ({fila['max']:.4f}, "
            f"n={fila['n_orden_max']})"
        )
    print("\nCorrelaciones más altas")
    for fila in q2["correlaciones"][:10]:
        print(f"{fila['a']:12s} {fila['b']:12s} {fila['r']: .4f}")

    client.close()


if __name__ == "__main__":
    main()
