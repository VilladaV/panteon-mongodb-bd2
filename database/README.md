# Base de datos

Esta carpeta contiene los scripts que acompañan la carga y la validación de
`panteon_db`.

| Archivo | Uso |
|---|---|
| `migrar_especie_original.py` | Añade `especie_original` a `species` y `sequences` para exportar el encabezado exacto del FASTA. |
| `especies_originales.csv` | Mapeo de los cuatro nombres que llevan punto en el FASTA. |
| `schema_validation.py` | Aplica `$jsonSchema` a `species`, `sequences` y `kmers` con `collMod`. |
| `indices.js` | Crea los índices de la Tabla II del artículo. |

## Respaldo y restauración

El respaldo completo no se versiona porque supera los 1,5 GB comprimidos y
contiene los datos de PanTEon. Para generarlo desde una base ya cargada:

```bash
mongodump --db panteon_db --archive=panteon_db.archive --gzip
```

Para restaurarlo en una instancia local:

```bash
mongorestore --gzip --archive=panteon_db.archive
```

La vía recomendada para reproducir sin respaldo es descargar el FASTA y el CSV
desde Zenodo y ejecutar `notebooks/01_exploracion_limpieza_normalizacion_cruce.ipynb`;
el notebook vuelve a calcular los *k*-mers y deja las tres colecciones listas.

## Orden de ejecución

```bash
python database/migrar_especie_original.py
python database/schema_validation.py
mongosh panteon_db database/indices.js
```

Los scripts de Python requieren `pymongo` y una instancia MongoDB escuchando en
`mongodb://localhost:27017/`. `indices.js` requiere `mongosh`.
