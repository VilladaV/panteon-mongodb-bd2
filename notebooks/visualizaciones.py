"""Pipelines de MongoDB para las cuatro figuras obligatorias.

El notebook 02 se encarga de convertir estos resultados en figuras y
exportarlas. Este módulo concentra únicamente la extracción de datos para
que la validación con una muestra y la ejecución completa utilicen la misma
lógica.
"""

from __future__ import annotations

from typing import Any


TAMANO_MUESTRA = 5000
REINOS_FIGURAS = ("Animalia", "Plantae", "Fungi")

# Orden fijo: facilita comparar las cuatro figuras y mantiene un criterio
# reproducible incluso cuando una muestra no contiene todos los órdenes.
ORDENES_FIGURAS = (
    "LTR",
    "LINE",
    "TIR",
    "HELITRON",
    "MITE",
    "SINE",
    "DIRS",
    "PLE",
    "CRYPTON",
    "RETROPOSON",
    "MAVERICK",
)

DINUCLEOTIDOS = (
    "AA",
    "AC",
    "AG",
    "AT",
    "CA",
    "CC",
    "CG",
    "CT",
    "GA",
    "GC",
    "GG",
    "GT",
    "TA",
    "TC",
    "TG",
    "TT",
)


def _inicio(modo_prueba: bool, tamano_muestra: int) -> list[dict[str, Any]]:
    """Añade una muestra aleatoria solo cuando se solicita el modo de prueba."""

    if modo_prueba:
        return [{"$sample": {"size": tamano_muestra}}]
    return []


def _ejecutar(
    coleccion,
    pipeline: list[dict[str, Any]],
    modo_prueba: bool,
    tamano_muestra: int,
) -> dict[str, Any]:
    """Ejecuta un pipeline y conserva metadatos de reproducibilidad."""

    datos = list(coleccion.aggregate(pipeline, allowDiskUse=True))
    return {
        "modo": "MUESTRA" if modo_prueba else "BASE COMPLETA",
        "documentos_analizados": tamano_muestra if modo_prueba else "todos",
        "datos": datos,
    }


def figura_01_composicion(
    db,
    modo_prueba: bool = True,
    tamano_muestra: int = TAMANO_MUESTRA,
) -> dict[str, Any]:
    """Cuenta TEs por orden dentro de Animalia, Plantae y Fungi."""

    pipeline = _inicio(modo_prueba, tamano_muestra)
    pipeline += [
        {
            "$project": {
                "_id": 0,
                "reino": {"$ifNull": ["$kingdom", "SIN_DATO"]},
                "orden": {
                    "$ifNull": [
                        "$te_classification.orden_fasta",
                        "SIN_DATO",
                    ]
                },
            }
        },
        {"$match": {"reino": {"$in": list(REINOS_FIGURAS)}}},
        {
            "$group": {
                "_id": {"reino": "$reino", "orden": "$orden"},
                "cantidad_te": {"$sum": 1},
            }
        },
        {
            "$project": {
                "_id": 0,
                "reino": "$_id.reino",
                "orden": "$_id.orden",
                "cantidad_te": 1,
            }
        },
        {"$sort": {"reino": 1, "cantidad_te": -1, "orden": 1}},
    ]
    return _ejecutar(db["sequences"], pipeline, modo_prueba, tamano_muestra)


def figura_02_longitud(
    db,
    modo_prueba: bool = True,
    tamano_muestra: int = TAMANO_MUESTRA,
) -> dict[str, Any]:
    """Devuelve una longitud por documento para el boxplot de cada orden."""

    pipeline = _inicio(modo_prueba, tamano_muestra)
    pipeline += [
        {
            "$project": {
                "_id": 0,
                "orden": {
                    "$ifNull": [
                        "$te_classification.orden_fasta",
                        "SIN_DATO",
                    ]
                },
                "longitud": "$metrics.longitud",
            }
        },
        {
            "$match": {
                "orden": {"$in": list(ORDENES_FIGURAS)},
                "longitud": {"$gt": 0},
            }
        },
    ]
    return _ejecutar(db["sequences"], pipeline, modo_prueba, tamano_muestra)


def figura_03_gc(
    db,
    modo_prueba: bool = True,
    tamano_muestra: int = TAMANO_MUESTRA,
) -> dict[str, Any]:
    """Calcula GC promedio y dispersión por reino."""

    pipeline = _inicio(modo_prueba, tamano_muestra)
    pipeline += [
        {
            "$project": {
                "_id": 0,
                "reino": {"$ifNull": ["$kingdom", "SIN_DATO"]},
                "pct_gc": "$metrics.pct_gc",
            }
        },
        {
            "$match": {
                "reino": {"$in": list(REINOS_FIGURAS)},
                "pct_gc": {"$gte": 0},
            }
        },
        {
            "$group": {
                "_id": "$reino",
                "promedio_pct_gc": {"$avg": "$pct_gc"},
                "desviacion_pct_gc": {"$stdDevPop": "$pct_gc"},
                "cantidad_te": {"$sum": 1},
            }
        },
        {
            "$project": {
                "_id": 0,
                "reino": "$_id",
                "promedio_pct_gc": 1,
                "desviacion_pct_gc": 1,
                "cantidad_te": 1,
            }
        },
        {"$sort": {"promedio_pct_gc": -1, "reino": 1}},
    ]
    return _ejecutar(db["sequences"], pipeline, modo_prueba, tamano_muestra)


def figura_04_dinucleotidos(
    db,
    modo_prueba: bool = True,
    tamano_muestra: int = TAMANO_MUESTRA,
) -> dict[str, Any]:
    """Promedia las frecuencias de los 16 dinucleótidos por orden de TE.

    ``counts`` es un diccionario disperso: si una clave no existe, su conteo
    es cero. Por eso se generan explícitamente las 16 claves para cada
    secuencia antes de calcular ``count / valid_windows``. El promedio final
    se hace sobre las frecuencias por secuencia, no sobre los conteos globales.
    """

    pipeline: list[dict[str, Any]] = [
        {"$match": {"k": 2, "valid_windows": {"$gt": 0}}}
    ]
    if modo_prueba:
        pipeline.append({"$sample": {"size": tamano_muestra}})

    pipeline += [
        {
            "$lookup": {
                "from": "sequences",
                "localField": "sequence_id",
                "foreignField": "_id",
                "as": "secuencia",
            }
        },
        {"$unwind": "$secuencia"},
        {
            "$project": {
                "orden": {
                    "$ifNull": [
                        "$secuencia.te_classification.orden_fasta",
                        "SIN_DATO",
                    ]
                },
                "valid_windows": 1,
                "pares": {
                    "$objectToArray": {"$ifNull": ["$counts", {}]}
                },
                "dinucleotidos": {"$literal": list(DINUCLEOTIDOS)},
            }
        },
        {"$match": {"orden": {"$in": list(ORDENES_FIGURAS)}}},
        {"$unwind": "$dinucleotidos"},
        {
            "$set": {
                "conteo": {
                    "$let": {
                        "vars": {
                            "coincidencia": {
                                "$arrayElemAt": [
                                    {
                                        "$filter": {
                                            "input": "$pares",
                                            "as": "par",
                                            "cond": {
                                                "$eq": [
                                                    "$$par.k",
                                                    "$dinucleotidos",
                                                ]
                                            },
                                        }
                                    },
                                    0,
                                ]
                            }
                        },
                        "in": {"$ifNull": ["$$coincidencia.v", 0]},
                    }
                }
            }
        },
        {
            "$set": {
                "frecuencia_secuencia": {
                    "$divide": ["$conteo", "$valid_windows"]
                }
            }
        },
        {
            "$group": {
                "_id": {
                    "orden": "$orden",
                    "dinucleotido": "$dinucleotidos",
                },
                "frecuencia_promedio": {"$avg": "$frecuencia_secuencia"},
                "secuencias_validas": {"$sum": 1},
            }
        },
        {
            "$project": {
                "_id": 0,
                "orden": "$_id.orden",
                "dinucleotido": "$_id.dinucleotido",
                "frecuencia_promedio": 1,
                "secuencias_validas": 1,
            }
        },
        {"$sort": {"orden": 1, "dinucleotido": 1}},
    ]
    return _ejecutar(db["kmers"], pipeline, modo_prueba, tamano_muestra)


FIGURAS = {
    1: figura_01_composicion,
    2: figura_02_longitud,
    3: figura_03_gc,
    4: figura_04_dinucleotidos,
}
