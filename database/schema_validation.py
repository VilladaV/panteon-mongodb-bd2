"""Aplica validación ``$jsonSchema`` a las tres colecciones de ``panteon_db``.

Requiere una base ya poblada y un servidor MongoDB accesible en localhost:27017.
Se ejecuta una sola vez después de la carga inicial:

    python database/schema_validation.py

El script usa ``collMod`` para no recrear las colecciones y termina validando cada
colección con ``db.validate_collection``. Debe ejecutarse después de la carga y de
``migrar_especie_original.py``, que añade el nombre original del FASTA.
"""

from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["panteon_db"]

# 1. Reglas para 'species' (2.790 docs)
schema_species = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "especie",
            "especie_original",
            "es_especie",
            "taxonomy",
            "library_origin",
        ],
        "properties": {
            "especie": {"bsonType": "string"},
            "especie_original": {"bsonType": "string"},
            "es_especie": {"bsonType": "bool"},
            "taxonomy": {
                "bsonType": "object",
                "required": ["kingdom"],
                "properties": {
                    "kingdom": {"enum": ["Animalia", "Plantae", "Fungi"]},
                    "phylum": {"bsonType": ["string", "null"]},
                    "tax_class": {"bsonType": ["string", "null"]},
                    "tax_order": {"bsonType": ["string", "null"]},
                    "family": {"bsonType": ["string", "null"]},
                },
            },
            "library_origin": {
                "bsonType": "object",
                "required": ["source"],
                "properties": {
                    "source": {"enum": ["Dfam", "RM2+MCH"]},
                    "source_2": {"bsonType": ["string", "null"]},
                    "notes": {"bsonType": ["string", "null"]},
                },
            },
        },
    }
}

# 2. Reglas para 'sequences' (239.946 docs)
schema_sequences = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "id_seq",
            "species_id",
            "especie",
            "especie_original",
            "kingdom",
            "te_classification",
            "metrics",
            "secuencia",
        ],
        "properties": {
            "id_seq": {"bsonType": "string"},
            "species_id": {"bsonType": "objectId"},
            "especie": {"bsonType": "string"},
            "especie_original": {"bsonType": "string"},
            "kingdom": {"enum": ["Animalia", "Plantae", "Fungi"]},
            "te_classification": {
                "bsonType": "object",
                "required": [
                    "clase_fasta",
                    "orden_fasta",
                    "superfamilia_fasta",
                ],
                "properties": {
                    "clase_fasta": {"enum": ["CLASSI", "CLASSII"]},
                    "orden_fasta": {"bsonType": "string"},
                    "superfamilia_fasta": {"bsonType": "string"},
                },
            },
            "metrics": {
                "bsonType": "object",
                "required": [
                    "longitud",
                    "n_count",
                    "gc_count",
                    "pct_n",
                    "pct_gc",
                ],
                "properties": {
                    "longitud": {"bsonType": ["int", "long"], "minimum": 1},
                    "n_count": {"bsonType": ["int", "long"], "minimum": 0},
                    "gc_count": {"bsonType": ["int", "long"], "minimum": 0},
                    "pct_n": {
                        "bsonType": ["double", "int"],
                        "minimum": 0,
                        "maximum": 100,
                    },
                    "pct_gc": {
                        "bsonType": ["double", "int"],
                        "minimum": 0,
                        "maximum": 100,
                    },
                },
            },
            "secuencia": {"bsonType": "string"},
        },
    }
}

# 3. Reglas para 'kmers' (1.439.676 docs)
schema_kmers = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "sequence_id",
            "id_seq",
            "k",
            "valid_windows",
            "counts",
        ],
        "properties": {
            "sequence_id": {"bsonType": "objectId"},
            "id_seq": {"bsonType": "string"},
            "k": {"bsonType": ["int", "long"], "minimum": 1, "maximum": 6},
            "valid_windows": {"bsonType": ["int", "long"], "minimum": 0},
            "counts": {"bsonType": "object"},
        },
    }
}


def main():
    # Aplicar a las colecciones ya creadas con collMod
    for coll_name, validator in [
        ("species", schema_species),
        ("sequences", schema_sequences),
        ("kmers", schema_kmers),
    ]:
        db.command(
            "collMod",
            coll_name,
            validator=validator,
            validationLevel="strict",
            validationAction="error",
        )
        res = db.validate_collection(coll_name)
        print(
            f"{coll_name}: valid={res['valid']}, "
            f"errors={len(res.get('errors', []))}"
        )

    client.close()


if __name__ == "__main__":
    main()
