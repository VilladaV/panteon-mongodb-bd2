// Índices del modelo PanTEon.
// Uso: mongosh panteon_db database/indices.js
// Requiere que las tres colecciones ya estén cargadas.

const panteon = db.getSiblingDB("panteon_db");

// species
panteon.species.createIndex(
  { especie: 1 },
  { unique: true, name: "uq_species_especie" }
);
panteon.species.createIndex(
  { "taxonomy.kingdom": 1 },
  { name: "ix_species_kingdom" }
);

// sequences
panteon.sequences.createIndex(
  { id_seq: 1 },
  { unique: true, name: "uq_sequences_id_seq" }
);
panteon.sequences.createIndex(
  { species_id: 1 },
  { name: "ix_sequences_species_id" }
);
panteon.sequences.createIndex(
  { especie: 1 },
  { name: "ix_sequences_especie" }
);
panteon.sequences.createIndex(
  { kingdom: 1 },
  { name: "ix_sequences_kingdom" }
);
panteon.sequences.createIndex(
  { "te_classification.clase_fasta": 1 },
  { name: "ix_sequences_clase" }
);
panteon.sequences.createIndex(
  { "te_classification.orden_fasta": 1 },
  { name: "ix_sequences_orden" }
);
panteon.sequences.createIndex(
  { "te_classification.superfamilia_fasta": 1 },
  { name: "ix_sequences_superfamilia" }
);

// kmers
panteon.kmers.createIndex(
  { id_seq: 1, k: 1 },
  { unique: true, name: "uq_kmers_id_seq_k" }
);
panteon.kmers.createIndex(
  { sequence_id: 1 },
  { name: "ix_kmers_sequence_id" }
);
panteon.kmers.createIndex(
  { k: 1, valid_windows: 1 },
  { name: "ix_kmers_k_valid_windows" }
);

print("Índices creados o ya existentes.");
