"""Implementación reutilizable de las consultas analíticas 1--15.

El notebook 02 conserva la presentación y la interpretación de cada consulta,
mientras que este módulo concentra los pipelines de MongoDB para que la misma
lógica se pueda ejecutar en modo muestra o sobre toda la colección.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pymongo import MongoClient


URI_LOCAL = "mongodb://127.0.0.1:27017"
NOMBRE_BASE = "panteon_db"
TAMANO_MUESTRA = 5000


def conectar(uri: str = URI_LOCAL, nombre_base: str = NOMBRE_BASE):
    """Abre la conexión local y devuelve el cliente y la base seleccionada."""

    cliente = MongoClient(uri)
    return cliente, cliente[nombre_base]


def _inicio(modo_prueba: bool, tamano_muestra: int) -> list[dict[str, Any]]:
    """Devuelve el inicio común de las consultas sobre ``sequences``."""

    if modo_prueba:
        return [{"$sample": {"size": tamano_muestra}}]
    return []


def _envolver(resultado: Any, modo_prueba: bool, tamano_muestra: int) -> dict[str, Any]:
    """Añade metadatos para que el notebook documente el modo de ejecución."""

    return {
        "modo": "MUESTRA" if modo_prueba else "BASE COMPLETA",
        "documentos_analizados": tamano_muestra if modo_prueba else "todos",
        "resultado": resultado,
    }


def _encabezado_fasta(documento: dict[str, Any]) -> str:
    """Reconstruye el encabezado del FASTA de PanTEon."""

    clasificacion = documento.get("te_classification") or {}
    clase = clasificacion.get("clase_fasta") or ""
    orden = clasificacion.get("orden_fasta") or ""
    superfamilia = clasificacion.get("superfamilia_fasta") or ""
    especie = documento.get("especie_original") or documento.get("especie") or ""
    return f">{documento.get('id_seq', '')}#{clase}/{orden}/{superfamilia} @{especie}"


def _escribir_fasta(documentos, ruta_salida: str | Path) -> int:
    """Escribe documentos de ``sequences`` en formato FASTA y devuelve el conteo."""

    ruta = Path(ruta_salida)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    exportadas = 0
    with ruta.open("w", encoding="utf-8", newline="\n") as archivo:
        for documento in documentos:
            archivo.write(_encabezado_fasta(documento) + "\n")
            secuencia = documento.get("secuencia") or ""
            for inicio in range(0, len(secuencia), 80):
                archivo.write(secuencia[inicio : inicio + 80] + "\n")
            exportadas += 1
    return exportadas


def _proyecto_biblioteca() -> dict[str, Any]:
    return {
        "_id": 0,
        "id_seq": 1,
        "especie": 1,
        "especie_original": {"$ifNull": ["$especie_original", "$especie"]},
        "te_classification": 1,
        "secuencia": 1,
    }


def consulta_01(db, modo_prueba: bool = True, tamano_muestra: int = TAMANO_MUESTRA):
    """Cuenta los TEs por clase, orden y superfamilia."""

    coleccion = db["sequences"]
    pipeline = _inicio(modo_prueba, tamano_muestra)
    pipeline += [
        {
            "$project": {
                "_id": 0,
                "clase": {"$ifNull": ["$te_classification.clase_fasta", "SIN_DATO"]},
                "orden": {"$ifNull": ["$te_classification.orden_fasta", "SIN_DATO"]},
                "superfamilia": {
                    "$ifNull": [
                        "$te_classification.superfamilia_fasta",
                        "SIN_DATO",
                    ]
                },
            }
        },
        {
            "$facet": {
                "por_clase": [
                    {"$group": {"_id": "$clase", "cantidad_te": {"$sum": 1}}},
                    {"$sort": {"cantidad_te": -1, "_id": 1}},
                    {
                        "$project": {
                            "_id": 0,
                            "clase": "$_id",
                            "cantidad_te": 1,
                        }
                    },
                ],
                "por_orden": [
                    {"$group": {"_id": "$orden", "cantidad_te": {"$sum": 1}}},
                    {"$sort": {"cantidad_te": -1, "_id": 1}},
                    {
                        "$project": {
                            "_id": 0,
                            "orden": "$_id",
                            "cantidad_te": 1,
                        }
                    },
                ],
                "por_superfamilia": [
                    {
                        "$group": {
                            "_id": "$superfamilia",
                            "cantidad_te": {"$sum": 1},
                        }
                    },
                    {"$sort": {"cantidad_te": -1, "_id": 1}},
                    {
                        "$project": {
                            "_id": 0,
                            "superfamilia": "$_id",
                            "cantidad_te": 1,
                        }
                    },
                ],
            }
        },
    ]
    resultado = list(coleccion.aggregate(pipeline, allowDiskUse=True))[0]
    return _envolver(resultado, modo_prueba, tamano_muestra)


def consulta_02(db, modo_prueba: bool = True, tamano_muestra: int = TAMANO_MUESTRA):
    """Cuenta los TEs de cada especie por clase, orden y superfamilia."""

    coleccion = db["sequences"]
    pipeline = _inicio(modo_prueba, tamano_muestra)
    pipeline += [
        {
            "$project": {
                "_id": 0,
                "especie": 1,
                "clase": {"$ifNull": ["$te_classification.clase_fasta", "SIN_DATO"]},
                "orden": {"$ifNull": ["$te_classification.orden_fasta", "SIN_DATO"]},
                "superfamilia": {
                    "$ifNull": [
                        "$te_classification.superfamilia_fasta",
                        "SIN_DATO",
                    ]
                },
            }
        },
        {
            "$facet": {
                "por_clase": [
                    {
                        "$group": {
                            "_id": {"especie": "$especie", "clase": "$clase"},
                            "cantidad_te": {"$sum": 1},
                        }
                    },
                    {"$sort": {"cantidad_te": -1, "_id.especie": 1, "_id.clase": 1}},
                    {
                        "$project": {
                            "_id": 0,
                            "especie": "$_id.especie",
                            "clase": "$_id.clase",
                            "cantidad_te": 1,
                        }
                    },
                ],
                "por_orden": [
                    {
                        "$group": {
                            "_id": {"especie": "$especie", "orden": "$orden"},
                            "cantidad_te": {"$sum": 1},
                        }
                    },
                    {"$sort": {"cantidad_te": -1, "_id.especie": 1, "_id.orden": 1}},
                    {
                        "$project": {
                            "_id": 0,
                            "especie": "$_id.especie",
                            "orden": "$_id.orden",
                            "cantidad_te": 1,
                        }
                    },
                ],
                "por_superfamilia": [
                    {
                        "$group": {
                            "_id": {
                                "especie": "$especie",
                                "superfamilia": "$superfamilia",
                            },
                            "cantidad_te": {"$sum": 1},
                        }
                    },
                    {
                        "$sort": {
                            "cantidad_te": -1,
                            "_id.especie": 1,
                            "_id.superfamilia": 1,
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "especie": "$_id.especie",
                            "superfamilia": "$_id.superfamilia",
                            "cantidad_te": 1,
                        }
                    },
                ],
            }
        },
    ]
    resultado = list(coleccion.aggregate(pipeline, allowDiskUse=True))[0]
    return _envolver(resultado, modo_prueba, tamano_muestra)


def consulta_03(db, modo_prueba: bool = True, tamano_muestra: int = TAMANO_MUESTRA):
    """Compara cantidades por clase y orden dentro de cada reino y phylum."""

    coleccion = db["sequences"]
    pipeline = _inicio(modo_prueba, tamano_muestra)
    pipeline += [
        {
            "$lookup": {
                "from": "species",
                "localField": "species_id",
                "foreignField": "_id",
                "as": "taxon",
            }
        },
        {"$unwind": {"path": "$taxon", "preserveNullAndEmptyArrays": True}},
        {
            "$project": {
                "_id": 0,
                "kingdom": {"$ifNull": ["$kingdom", "SIN_DATO"]},
                "phylum": {
                    "$let": {
                        "vars": {
                            "p": {
                                "$trim": {
                                    "input": {
                                        "$ifNull": ["$taxon.taxonomy.phylum", ""]
                                    }
                                }
                            }
                        },
                        "in": {
                            "$cond": [
                                {"$eq": ["$$p", ""]},
                                "SIN_DATO",
                                "$$p",
                            ]
                        },
                    }
                },
                "clase": {
                    "$ifNull": ["$te_classification.clase_fasta", "SIN_DATO"]
                },
                "orden": {
                    "$ifNull": ["$te_classification.orden_fasta", "SIN_DATO"]
                },
            }
        },
        {
            "$facet": {
                "por_reino": [
                    {
                        "$group": {
                            "_id": {
                                "kingdom": "$kingdom",
                                "clase": "$clase",
                                "orden": "$orden",
                            },
                            "cantidad_te": {"$sum": 1},
                        }
                    },
                    {
                        "$sort": {
                            "_id.kingdom": 1,
                            "cantidad_te": -1,
                            "_id.clase": 1,
                            "_id.orden": 1,
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "kingdom": "$_id.kingdom",
                            "clase": "$_id.clase",
                            "orden": "$_id.orden",
                            "cantidad_te": 1,
                        }
                    },
                ],
                "por_phylum": [
                    {
                        "$group": {
                            "_id": {
                                "phylum": "$phylum",
                                "clase": "$clase",
                                "orden": "$orden",
                            },
                            "cantidad_te": {"$sum": 1},
                        }
                    },
                    {
                        "$sort": {
                            "_id.phylum": 1,
                            "cantidad_te": -1,
                            "_id.clase": 1,
                            "_id.orden": 1,
                        }
                    },
                    {
                        "$project": {
                            "_id": 0,
                            "phylum": "$_id.phylum",
                            "clase": "$_id.clase",
                            "orden": "$_id.orden",
                            "cantidad_te": 1,
                        }
                    },
                ],
            }
        },
    ]
    resultado = list(coleccion.aggregate(pipeline, allowDiskUse=True))[0]
    return _envolver(resultado, modo_prueba, tamano_muestra)


def consulta_04(db, modo_prueba: bool = True, tamano_muestra: int = TAMANO_MUESTRA):
    """Obtiene las diez especies con más y con menos secuencias.

    Solo considera entradas cuyo ``es_especie`` es verdadero en ``species``;
    así se excluyen grupos taxonómicos como ``Homininae`` o ``Metazoa``.
    """

    coleccion = db["sequences"]
    pipeline = _inicio(modo_prueba, tamano_muestra)
    pipeline += [
        {
            "$lookup": {
                "from": "species",
                "localField": "species_id",
                "foreignField": "_id",
                "as": "taxon",
            }
        },
        {"$unwind": "$taxon"},
        {"$match": {"taxon.es_especie": True}},
        {"$group": {"_id": "$especie", "cantidad_te": {"$sum": 1}}},
        {
            "$facet": {
                "mas_te": [
                    {"$sort": {"cantidad_te": -1, "_id": 1}},
                    {"$limit": 10},
                    {"$project": {"_id": 0, "especie": "$_id", "cantidad_te": 1}},
                ],
                "menos_te": [
                    {"$sort": {"cantidad_te": 1, "_id": 1}},
                    {"$limit": 10},
                    {"$project": {"_id": 0, "especie": "$_id", "cantidad_te": 1}},
                ],
            }
        },
    ]
    resultado = list(coleccion.aggregate(pipeline, allowDiskUse=True))[0]
    return _envolver(resultado, modo_prueba, tamano_muestra)


def consulta_05(db, modo_prueba: bool = True, tamano_muestra: int = TAMANO_MUESTRA):
    """Calcula longitud promedio, mínima y máxima por nivel de clasificación."""

    coleccion = db["sequences"]
    pipeline = _inicio(modo_prueba, tamano_muestra)
    pipeline += [
        {
            "$project": {
                "_id": 0,
                "longitud": "$metrics.longitud",
                "clase": {"$ifNull": ["$te_classification.clase_fasta", "SIN_DATO"]},
                "orden": {"$ifNull": ["$te_classification.orden_fasta", "SIN_DATO"]},
                "superfamilia": {
                    "$ifNull": [
                        "$te_classification.superfamilia_fasta",
                        "SIN_DATO",
                    ]
                },
            }
        },
        {"$facet": {}},
    ]
    for nombre, campo in (
        ("por_clase", "clase"),
        ("por_orden", "orden"),
        ("por_superfamilia", "superfamilia"),
    ):
        pipeline[-1]["$facet"][nombre] = [
            {
                "$group": {
                    "_id": f"${campo}",
                    "promedio_longitud": {"$avg": "$longitud"},
                    "longitud_minima": {"$min": "$longitud"},
                    "longitud_maxima": {"$max": "$longitud"},
                    "cantidad_te": {"$sum": 1},
                }
            },
            {"$sort": {"promedio_longitud": -1, "_id": 1}},
            {
                "$project": {
                    "_id": 0,
                    campo: "$_id",
                    "promedio_longitud": 1,
                    "longitud_minima": 1,
                    "longitud_maxima": 1,
                    "cantidad_te": 1,
                }
            },
        ]
    resultado = list(coleccion.aggregate(pipeline, allowDiskUse=True))[0]
    return _envolver(resultado, modo_prueba, tamano_muestra)


def consulta_06(db, modo_prueba: bool = True, tamano_muestra: int = TAMANO_MUESTRA):
    """Calcula el porcentaje GC promedio por orden de TE y por reino."""

    coleccion = db["sequences"]
    pipeline = _inicio(modo_prueba, tamano_muestra)
    pipeline += [
        {
            "$project": {
                "_id": 0,
                "kingdom": {"$ifNull": ["$kingdom", "SIN_DATO"]},
                "orden": {"$ifNull": ["$te_classification.orden_fasta", "SIN_DATO"]},
                "pct_gc": "$metrics.pct_gc",
            }
        },
        {
            "$facet": {
                "por_orden": [
                    {
                        "$group": {
                            "_id": "$orden",
                            "promedio_pct_gc": {"$avg": "$pct_gc"},
                            "cantidad_te": {"$sum": 1},
                        }
                    },
                    {"$sort": {"promedio_pct_gc": -1, "_id": 1}},
                    {
                        "$project": {
                            "_id": 0,
                            "orden": "$_id",
                            "promedio_pct_gc": 1,
                            "cantidad_te": 1,
                        }
                    },
                ],
                "por_reino": [
                    {
                        "$group": {
                            "_id": "$kingdom",
                            "promedio_pct_gc": {"$avg": "$pct_gc"},
                            "cantidad_te": {"$sum": 1},
                        }
                    },
                    {"$sort": {"promedio_pct_gc": -1, "_id": 1}},
                    {
                        "$project": {
                            "_id": 0,
                            "kingdom": "$_id",
                            "promedio_pct_gc": 1,
                            "cantidad_te": 1,
                        }
                    },
                ],
            }
        },
    ]
    resultado = list(coleccion.aggregate(pipeline, allowDiskUse=True))[0]
    return _envolver(resultado, modo_prueba, tamano_muestra)


def consulta_07(db, modo_prueba: bool = True, tamano_muestra: int = TAMANO_MUESTRA):
    """Obtiene el TE más largo y el más corto de cada reino."""

    coleccion = db["sequences"]
    pipeline = _inicio(modo_prueba, tamano_muestra)
    pipeline += [
        {
            "$project": {
                "_id": 0,
                "id_seq": 1,
                "especie": 1,
                "kingdom": 1,
                "clase": "$te_classification.clase_fasta",
                "orden": "$te_classification.orden_fasta",
                "superfamilia": "$te_classification.superfamilia_fasta",
                "longitud": "$metrics.longitud",
            }
        },
        {
            "$facet": {
                "mas_largos": [
                    {"$sort": {"kingdom": 1, "longitud": -1, "id_seq": 1}},
                    {
                        "$group": {
                            "_id": "$kingdom",
                            "registro": {"$first": "$$ROOT"},
                        }
                    },
                    {"$replaceWith": "$registro"},
                    {"$sort": {"kingdom": 1}},
                ],
                "mas_cortos": [
                    {"$sort": {"kingdom": 1, "longitud": 1, "id_seq": 1}},
                    {
                        "$group": {
                            "_id": "$kingdom",
                            "registro": {"$first": "$$ROOT"},
                        }
                    },
                    {"$replaceWith": "$registro"},
                    {"$sort": {"kingdom": 1}},
                ],
            }
        },
    ]
    resultado = list(coleccion.aggregate(pipeline, allowDiskUse=True))[0]
    return _envolver(resultado, modo_prueba, tamano_muestra)


def _documento_de_muestra(coleccion, tamano_muestra: int, proyeccion: dict[str, int]):
    """Selecciona un documento real de una muestra para probar consultas parametrizadas."""

    pipeline = [
        {"$sample": {"size": tamano_muestra}},
        {"$project": proyeccion},
    ]
    return next(coleccion.aggregate(pipeline))


def consulta_08(
    db,
    modo_prueba: bool = True,
    tamano_muestra: int = TAMANO_MUESTRA,
    nombre_secuencia: str | None = None,
):
    """Busca una secuencia y devuelve clasificación, especie y taxonomía."""

    coleccion = db["sequences"]
    filtro: dict[str, Any]
    if modo_prueba and nombre_secuencia is None:
        muestra = _documento_de_muestra(
            coleccion,
            tamano_muestra,
            {"_id": 1, "id_seq": 1},
        )
        nombre_secuencia = muestra["id_seq"]
        # El _id garantiza que el registro consultado pertenece a la muestra.
        filtro = {"_id": muestra["_id"], "id_seq": nombre_secuencia}
    elif modo_prueba:
        # Si el usuario fija un nombre, se hace la búsqueda puntual solicitada.
        # La consulta sigue siendo pequeña porque devuelve como máximo un registro.
        filtro = {"id_seq": nombre_secuencia}
    else:
        nombre_secuencia = nombre_secuencia or "PDB00000001"
        filtro = {"id_seq": nombre_secuencia}

    pipeline = [
        {"$match": filtro},
        {
            "$lookup": {
                "from": "species",
                "localField": "species_id",
                "foreignField": "_id",
                "as": "taxon",
            }
        },
        {"$unwind": {"path": "$taxon", "preserveNullAndEmptyArrays": True}},
        {
            "$project": {
                "_id": 0,
                "id_seq": 1,
                "especie": 1,
                "te_classification": 1,
                "taxonomy": "$taxon.taxonomy",
            }
        },
    ]
    resultado = list(coleccion.aggregate(pipeline, allowDiskUse=True))
    return _envolver(
        {"nombre_secuencia": nombre_secuencia, "registros": resultado},
        modo_prueba,
        tamano_muestra,
    )


def consulta_09(
    db,
    modo_prueba: bool = True,
    tamano_muestra: int = TAMANO_MUESTRA,
    especie: str | None = None,
    superfamilia: str | None = None,
):
    """Lista los identificadores de una superfamilia dentro de una especie."""

    coleccion = db["sequences"]
    if modo_prueba and (especie is None or superfamilia is None):
        pipeline_muestra = [
            {"$sample": {"size": tamano_muestra}},
            {
                "$project": {
                    "_id": 1,
                    "especie": 1,
                    "superfamilia": "$te_classification.superfamilia_fasta",
                }
            },
        ]
        documentos = list(coleccion.aggregate(pipeline_muestra))
        parametro = documentos[0]
        especie = especie or parametro["especie"]
        superfamilia = superfamilia or parametro["superfamilia"]
        ids_muestra = [documento["_id"] for documento in documentos]
        filtro = {
            "_id": {"$in": ids_muestra},
            "especie": especie,
            "te_classification.superfamilia_fasta": superfamilia,
        }
    elif modo_prueba:
        # Con parámetros explícitos se limita primero al grupo solicitado y
        # después se toma una muestra de hasta 5.000 coincidencias.
        filtro = {
            "especie": especie,
            "te_classification.superfamilia_fasta": superfamilia,
        }
    else:
        especie = especie or "Puma concolor"
        superfamilia = superfamilia or "TRNA"
        filtro = {
            "especie": especie,
            "te_classification.superfamilia_fasta": superfamilia,
        }

    pipeline = [
        {"$match": filtro},
    ]
    if modo_prueba and especie is not None and superfamilia is not None and "_id" not in filtro:
        pipeline.append({"$sample": {"size": tamano_muestra}})
    pipeline += [
        {
            "$project": {
                "_id": 0,
                "id_seq": 1,
                "especie": 1,
                "superfamilia": "$te_classification.superfamilia_fasta",
            }
        },
        {"$sort": {"id_seq": 1}},
    ]
    resultado = list(coleccion.aggregate(pipeline, allowDiskUse=True))
    return _envolver(
        {
            "especie": especie,
            "superfamilia": superfamilia,
            "secuencias": resultado,
        },
        modo_prueba,
        tamano_muestra,
    )


def consulta_10(
    db,
    modo_prueba: bool = True,
    tamano_muestra: int = TAMANO_MUESTRA,
    especie: str | None = None,
    ruta_salida: str | Path | None = None,
):
    """Exporta la biblioteca FASTA de una especie."""

    coleccion = db["sequences"]
    especie = especie or "Malus domestica"
    pipeline = [{"$match": {"especie": especie}}]
    if modo_prueba:
        pipeline.append({"$sample": {"size": tamano_muestra}})
    pipeline += [
        {"$sort": {"id_seq": 1}},
        {"$project": _proyecto_biblioteca()},
    ]

    if ruta_salida is not None:
        exportadas = _escribir_fasta(
            coleccion.aggregate(pipeline, allowDiskUse=True), ruta_salida
        )
        return _envolver(
            {
                "especie": especie,
                "ruta": str(ruta_salida),
                "secuencias_exportadas": exportadas,
            },
            modo_prueba,
            tamano_muestra,
        )

    documentos = list(coleccion.aggregate(pipeline, allowDiskUse=True))
    return _envolver(
        {"especie": especie, "secuencias": documentos},
        modo_prueba,
        tamano_muestra,
    )


def consulta_11(
    db,
    modo_prueba: bool = True,
    tamano_muestra: int = TAMANO_MUESTRA,
    kingdom: str | None = None,
    ruta_salida: str | Path | None = None,
):
    """Exporta la biblioteca FASTA de un reino."""

    coleccion = db["sequences"]
    kingdom = kingdom or "Fungi"
    pipeline = [{"$match": {"kingdom": kingdom}}]
    if modo_prueba:
        pipeline.append({"$sample": {"size": tamano_muestra}})
    pipeline += [
        {"$sort": {"id_seq": 1}},
        {"$project": _proyecto_biblioteca()},
    ]

    if ruta_salida is not None:
        exportadas = _escribir_fasta(
            coleccion.aggregate(pipeline, allowDiskUse=True), ruta_salida
        )
        return _envolver(
            {
                "kingdom": kingdom,
                "ruta": str(ruta_salida),
                "secuencias_exportadas": exportadas,
            },
            modo_prueba,
            tamano_muestra,
        )

    documentos = list(coleccion.aggregate(pipeline, allowDiskUse=True))
    return _envolver(
        {"kingdom": kingdom, "secuencias": documentos},
        modo_prueba,
        tamano_muestra,
    )


def consulta_12(
    db,
    modo_prueba: bool = True,
    tamano_muestra: int = TAMANO_MUESTRA,
    limite: int = 5,
):
    """Une secuencias con la taxonomía de su especie mediante ``$lookup``."""

    coleccion = db["sequences"]
    pipeline = _inicio(modo_prueba, tamano_muestra)
    pipeline += [
        {
            "$lookup": {
                "from": "species",
                "localField": "species_id",
                "foreignField": "_id",
                "as": "taxon",
            }
        },
        {"$unwind": {"path": "$taxon", "preserveNullAndEmptyArrays": True}},
        {"$sort": {"id_seq": 1}},
        {"$limit": limite},
        {
            "$project": {
                "_id": 0,
                "id_seq": 1,
                "especie": 1,
                "especie_original": {"$ifNull": ["$especie_original", "$especie"]},
                "taxonomy": {
                    "kingdom": "$taxon.taxonomy.kingdom",
                    "phylum": "$taxon.taxonomy.phylum",
                    "tax_class": "$taxon.taxonomy.tax_class",
                    "tax_order": "$taxon.taxonomy.tax_order",
                    "family": "$taxon.taxonomy.family",
                },
            }
        },
    ]
    muestra = list(coleccion.aggregate(pipeline, allowDiskUse=True))
    total = coleccion.count_documents({"species_id": {"$ne": None}})
    return _envolver(
        {
            "secuencias_con_taxonomia": total,
            "muestra": muestra,
        },
        modo_prueba,
        tamano_muestra,
    )


def consulta_13(
    db,
    modo_prueba: bool = True,
    tamano_muestra: int = TAMANO_MUESTRA,
):
    """Compara especies, secuencias y longitud promedio por ``Source``."""

    coleccion = db["sequences"]
    pipeline = _inicio(modo_prueba, tamano_muestra)
    pipeline += [
        {
            "$lookup": {
                "from": "species",
                "localField": "species_id",
                "foreignField": "_id",
                "as": "taxon",
            }
        },
        {"$unwind": "$taxon"},
        {
            "$group": {
                "_id": "$taxon.library_origin.source",
                "especies": {"$addToSet": "$taxon._id"},
                "secuencias": {"$sum": 1},
                "longitud_total": {"$sum": "$metrics.longitud"},
            }
        },
        {
            "$project": {
                "_id": 0,
                "source": "$_id",
                "especies": {"$size": "$especies"},
                "secuencias": 1,
                "promedio_secuencias_por_especie": {
                    "$divide": ["$secuencias", {"$size": "$especies"}]
                },
                "longitud_promedio": {
                    "$divide": ["$longitud_total", "$secuencias"]
                },
            }
        },
        {"$sort": {"source": 1}},
    ]
    resultado = list(coleccion.aggregate(pipeline, allowDiskUse=True))
    return _envolver(resultado, modo_prueba, tamano_muestra)


def _conteo(cursor) -> int:
    fila = next(cursor, None)
    return fila["n"] if fila else 0


def consulta_14(
    db,
    modo_prueba: bool = True,
    tamano_muestra: int = TAMANO_MUESTRA,
):
    """Ejecuta controles de calidad sobre ``sequences`` y ``species``."""

    secuencias = db["sequences"]
    especies = db["species"]
    total = secuencias.count_documents({})

    sin_species_id = secuencias.count_documents(
        {"$or": [{"species_id": {"$exists": False}}, {"species_id": None}]}
    )
    longitudes_invalidas = secuencias.count_documents(
        {"metrics.longitud": {"$lte": 0}}
    )
    caracteres_invalidos = secuencias.count_documents(
        {"secuencia": {"$regex": "[^ACGTN]"}}
    )
    con_n = secuencias.count_documents({"secuencia": {"$regex": "N"}})

    duplicados = _conteo(
        secuencias.aggregate(
            [
                {"$group": {"_id": "$id_seq", "n": {"$sum": 1}}},
                {"$match": {"n": {"$gt": 1}}},
                {"$count": "n"},
            ]
        )
    )
    taxonomia_faltante = _conteo(
        secuencias.aggregate(
            [
                {
                    "$lookup": {
                        "from": "species",
                        "localField": "species_id",
                        "foreignField": "_id",
                        "as": "taxon",
                    }
                },
                {"$match": {"taxon": {"$size": 0}}},
                {"$count": "n"},
            ]
        )
    )
    especies_sin_secuencias = _conteo(
        especies.aggregate(
            [
                {
                    "$lookup": {
                        "from": "sequences",
                        "localField": "_id",
                        "foreignField": "species_id",
                        "as": "secuencias",
                    }
                },
                {"$match": {"secuencias": {"$size": 0}}},
                {"$count": "n"},
            ]
        )
    )
    no_especies = especies.count_documents({"es_especie": False})
    secuencias_no_especie = _conteo(
        secuencias.aggregate(
            [
                {
                    "$lookup": {
                        "from": "species",
                        "localField": "species_id",
                        "foreignField": "_id",
                        "as": "taxon",
                    }
                },
                {"$unwind": "$taxon"},
                {"$match": {"taxon.es_especie": False}},
                {"$count": "n"},
            ]
        )
    )
    longitud = next(
        secuencias.aggregate(
            [
                {
                    "$group": {
                        "_id": None,
                        "minima": {"$min": "$metrics.longitud"},
                        "maxima": {"$max": "$metrics.longitud"},
                        "promedio": {"$avg": "$metrics.longitud"},
                    }
                }
            ]
        ),
        {"minima": None, "maxima": None, "promedio": None},
    )
    pct_n = next(
        secuencias.aggregate(
            [{"$group": {"_id": None, "promedio": {"$avg": "$metrics.pct_n"}}}]
        ),
        {"promedio": None},
    )
    por_reino = list(
        secuencias.aggregate(
            [
                {"$group": {"_id": "$kingdom", "n": {"$sum": 1}}},
                {"$sort": {"n": -1}},
            ]
        )
    )

    return _envolver(
        {
            "secuencias": total,
            "especies": especies.count_documents({}),
            "especies_validas": especies.count_documents({"es_especie": True}),
            "entradas_no_especie": no_especies,
            "secuencias_no_especie": secuencias_no_especie,
            "sin_species_id": sin_species_id,
            "taxonomia_faltante": taxonomia_faltante,
            "especies_sin_secuencias": especies_sin_secuencias,
            "id_seq_duplicados": duplicados,
            "longitudes_invalidas": longitudes_invalidas,
            "caracteres_invalidos": caracteres_invalidos,
            "con_n": con_n,
            "pct_con_n": round(100 * con_n / total, 2) if total else 0,
            "pct_n_promedio": pct_n.get("promedio"),
            "longitud": {
                "minima": longitud.get("minima"),
                "maxima": longitud.get("maxima"),
                "promedio": longitud.get("promedio"),
            },
            "por_reino": por_reino,
        },
        modo_prueba,
        tamano_muestra,
    )


def consulta_15(
    db,
    modo_prueba: bool = True,
    tamano_muestra: int = TAMANO_MUESTRA,
    id_seq: str | None = None,
    k: int | None = None,
):
    """Recupera el perfil de k-mers de una secuencia para un tamaño k dado."""

    coleccion = db["kmers"]
    if modo_prueba and (id_seq is None or k is None):
        # Tomar una muestra aleatoria para asegurar que los parámetros existan
        pipeline_muestra = [
            {"$sample": {"size": 1}},
            {"$project": {"id_seq": 1, "k": 1}},
        ]
        documentos = list(coleccion.aggregate(pipeline_muestra))
        if documentos:
            parametro = documentos[0]
            id_seq = id_seq or parametro.get("id_seq")
            k = k or parametro.get("k")

    # Valores por defecto para ejecución directa sin modo_prueba
    id_seq = id_seq or "PDB00000001"
    k = k or 6

    filtro = {"id_seq": id_seq, "k": k}

    pipeline = [
        {"$match": filtro},
        {
            "$project": {
                "_id": 0,
                "id_seq": 1,
                "k": 1,
                "valid_windows": 1,
                "counts": 1,
            }
        },
    ]
    
    resultado = list(coleccion.aggregate(pipeline))
    return _envolver(
        {
            "id_seq": id_seq,
            "k": k,
            "perfil": resultado,
        },
        modo_prueba,
        tamano_muestra,
    )


CONSULTAS_10_14 = {
    10: consulta_10,
    11: consulta_11,
    12: consulta_12,
    13: consulta_13,
    14: consulta_14,
}

CONSULTAS_01_09 = {
    1: consulta_01,
    2: consulta_02,
    3: consulta_03,
    4: consulta_04,
    5: consulta_05,
    6: consulta_06,
    7: consulta_07,
    8: consulta_08,
    9: consulta_09,
    15: consulta_15,
}

# Alias conservado para no romper código que ya importe el nombre anterior.
CONSULTAS_02_09 = {
    clave: funcion for clave, funcion in CONSULTAS_01_09.items() if clave >= 2
}
