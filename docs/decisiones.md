# Bitácora de decisiones y modelo de datos

> Documento de trabajo del equipo.

---

## 1. Avance del pipeline de limpieza

**Responsable:** María Camila Prada Cortes.
**Notebook:** `notebooks/01_exploracion_limpieza_normalizacion_cruce.ipynb` (74 celdas).
**Commits:** `30a2a2d`, `803aced`, `34532a6` sobre `develop`.

### 1.1 Etapas implementadas


| #   | Etapa                                                                     | Resultado                             |
| --- | ------------------------------------------------------------------------- | ------------------------------------- |
| 1   | Lectura y exploración del CSV                                             | 2.790 filas × 13 columnas             |
| 2   | Conteo de vacíos y de valores por columna                                 | ver §2                                |
| 3   | Selección de las 9 columnas del proyecto                                  | `df_csv_9col` (2.790 × 9)             |
| 4   | Normalización de `Species` (`strip`)                                      | 0 cambios: el CSV no traía espacios   |
| 5   | Marcadores `"No …"` en `Order` → `null`                                   | 19 celdas convertidas (29 → 48 nulos) |
| 6   | Lectura del FASTA con `SeqIO`                                             | 239.946 registros                     |
| 7   | Parseo del encabezado (`separar_cadena`)                                  | 0 encabezados malformados             |
| 8   | Construcción de `df_secuencias` (8 columnas, sin la secuencia)            | 239.946 × 8                           |
| 9   | Atributos derivados: `longitud`, `n_count`, `gc_count`, `pct_n`, `pct_gc` | completos                             |
| 10  | Normalización de especies y cruce con el CSV                              | 2.790 ↔ 2.790, 0 huérfanos            |
| 11  | Normalización de superfamilia `tRNA` → `TRNA`                             | 66 → 65 valores distintos             |
| 12  | Bandera `es_especie` (desde `Notes`)                                      | 2.746 verdaderas / 44 falsas          |


### 1.2 Encabezado del FASTA

Formato confirmado en los datos reales:

```
>PDB00000001#CLASSII/HELITRON/HELITRON @Halicephalobus mephisto
 └── id_seq ─┘└── clase/orden/superfamilia ──┘└──── especie ────┘
```

`separar_cadena` corta por el **primer** `@` y el **primer** `#`, y luego por `/`.
Los tres niveles siempre están presentes (0 fallos en 239.946 registros), aunque en
21.544 secuencias (8,98 %) la superfamilia repite el orden, es decir, no hay nivel
específico asignado.

>  **identificadores:** no todos siguen el patrón `PDB…`. Hay registros con
> nombre original de la familia, por ejemplo `PumCon-1.141#CLASSII/TIR/TC1MARINER`.
> El campo `id_seq` debe aceptar ambos formatos (STRING, no patrón fijo).

---

## 2. Hallazgos de calidad en los datos

### 2.1 Vacíos del CSV (2.790 filas)


| Columna                        | Nulos                   | %               |
| ------------------------------ | ----------------------- | --------------- |
| `Phylum`                       | 3                       | 0,11 %          |
| `Class`                        | 49                      | 1,76 %          |
| `Order`                        | 29 → 48 tras normalizar | 1,04 % → 1,72 % |
| `Family`                       | 76                      | 2,72 %          |
| `Notes`                        | 6                       | 0,22 %          |
| `Source 2`                     | 2.740                   | 98,2 %          |
| `Kingdom`, `Species`, `Source` | 0                       | 0 %             |


### 2.2 Marcadores de ausencia

Además de los nulos reales, `Order` traía texto que significa "sin dato":
`No trobat` (7), `No order` (5), `No ordre NCBI` (2), `No Orden No trobat` (2),
y 3 variantes con `incertae sedis`. Se convierten a `null`.

### 2.3 Columnas desalineadas (hallazgo, no error del parser)

Hay filas donde el valor no corresponde a la columna:


| Fila | Columna | Valor                | Por qué está mal            |
| ---- | ------- | -------------------- | --------------------------- |
| 10   | `Order` | `Amplistromataceae`  | es un nombre de **familia** |
| 2210 | `Class` | `Ramicandelaberales` | es un nombre de **orden**   |
| 2577 | `Class` | `Pleistophoridae`    | es un nombre de **familia** |


No se corrigieron: son datos de origen y se reportan como parte del análisis de calidad
(consulta 14 y sección III-A del artículo).

### 2.4 Entradas que no son especies

44 filas de `Species` son en realidad grupos taxonómicos superiores
(`Metazoa`, `Mammalia`, `Primates`, `Rodentia`, `Rattus`, `Danio`, …), marcadas en
`Notes` como `Dfam no especie` (34) o `No especie Repbase` (10).
**No se eliminan**: el FASTA contiene secuencias de esos grupos.

---

## 3. Decisiones tomadas


| #    | Decisión                                                              | Alternativa descartada                                       | Por qué                                                                                                     | Quién  |
| ---- | --------------------------------------------------------------------- | ------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- | ------ |
| D-01 | Conservar **9 de 13** columnas del CSV                                | Guardar el CSV completo                                      | La guía descarta explícitamente `Library?`, `Selected`, `TE_count`, `MCH_Parameters`                        | Camila |
| D-02 | `Order` con marcadores `"No …"` → `null`                              | Dejarlos como texto                                          | Un marcador de ausencia no debe competir en los `$group`                                                    | Camila |
| D-03 | Unificar `tRNA` → `TRNA` en superfamilia                              | Dejarlas separadas                                           | Misma entidad con dos grafías; 56 registros quedaban aislados                                               | Camila |
| D-04 | Normalizar especies con `strip()` + eliminar `.`                      | Usar el nombre crudo                                         | Es la única forma en que cruzan las 2.790                                                                   | Camila |
| D-05 | `es_especie` como bandera booleana                                    | Borrar las 44 filas                                          | Tienen secuencias en el FASTA; además se necesitan para la consulta 14                                      | **-**  |
| D-06 | Tres colecciones: `species`, `sequences`, `kmers`                     | Documento único con todo                                     | Los perfiles de k-mers concentran la mayor parte del volumen (3,47 GB) y no se usan en las consultas analíticas | Equipo |
| D-07 | Referencia `species_id` + *extended reference* (`especie`, `especie_original`, `kingdom`) | Solo referencia, o taxonomía completa embebida               | Evita un `$lookup` en las consultas por reino y en la exportación `.fasta`; solo se paga en consultas 12/13 | Equipo |
| D-08 | k-mers en colección aparte, un documento por secuencia y por `k`      | Embebidos en `sequences`, o un documento único con los 6 `k` | Permite traer solo el `k` pedido (consulta 15) y comparar estrategias en la §4.4                            | Equipo |
| D-09 | Diccionario **disperso** (`counts` solo con k-mers presentes)         | Arreglo denso de 5.460 posiciones                            | En secuencias cortas la mayoría de k-mers no aparece; el denso paga ceros                                   | Equipo |
| D-10 | Descartar ventanas con bases fuera de `A`, `C`, `G` y `T` y registrar `valid_windows`      | Contar `N` como base, o descartar la secuencia completa      | 22,85 % de las secuencias tiene alguna `N`; descartarlas perdería un cuarto del corpus                      | Equipo |
| D-11 | `_id` ObjectId + `id_seq` como campo indexado                         | Usar `id_seq` como `_id`                                     | Lo exige la guía (§4.1)                                                                                     | Equipo |
| D-12 | `tax_class` / `tax_order` vs. `clase_fasta` / `orden_fasta`           | `class` / `order` en ambos niveles                           | Evita la colisión que advierte la guía                                                                      | Equipo |


---

## 4. Modelo de datos

Arquitectura documental híbrida: tres colecciones unidas por `_id`.

```
species (2.790)  ──1:N──►  sequences (239.946)  ──1:N──►  kmers (≤ 1.439.676)
```

### 4.1 `species` — una por especie


| Campo                     | Tipo          | Contenido                              |
| ------------------------- | ------------- | -------------------------------------- |
| `_id`                     | ObjectId      | Llave primaria                         |
| `especie`                 | string        | Nombre normalizado · **índice único**  |
| `especie_original`        | string        | Nombre del FASTA para exportar         |
| `es_especie`              | bool          | `false` para los 44 grupos taxonómicos |
| `taxonomy.kingdom`        | string        | Animalia, Plantae, Fungi               |
| `taxonomy.phylum`         | string \| null |                                        |
| `taxonomy.tax_class`      | string \| null | `Class` del CSV                        |
| `taxonomy.tax_order`      | string \| null | `Order` del CSV                        |
| `taxonomy.family`         | string \| null |                                        |
| `library_origin.source`   | string        | Dfam o RM2+MCH                         |
| `library_origin.source_2` | string \| null |                                        |
| `library_origin.notes`    | string \| null |                                        |


### 4.2 `sequences` — una por secuencia


| Campo                                  | Tipo     | Contenido                                         |
| -------------------------------------- | -------- | ------------------------------------------------- |
| `_id`                                  | ObjectId | Llave primaria                                    |
| `id_seq`                               | string   | ID del encabezado · **índice único**              |
| `species_id`                           | ObjectId | Referencia a `species._id`                        |
| `especie`                              | string   | Clave normalizada para filtrar y cruzar           |
| `especie_original`                     | string   | Desnormalizado para reconstruir el `.fasta`       |
| `kingdom`                              | string   | Desnormalizado para consultas 3, 6, 7, 11         |
| `te_classification.clase_fasta`        | string   | CLASSI, CLASSII                                   |
| `te_classification.orden_fasta`        | string   | LTR, LINE, TIR, …                                 |
| `te_classification.superfamilia_fasta` | string   | COPIA, GYPSY, …                                   |
| `metrics.longitud`                     | int      |                                                   |
| `metrics.n_count`                      | int      |                                                   |
| `metrics.gc_count`                     | int      |                                                   |
| `metrics.pct_n`                        | double   |                                                   |
| `metrics.pct_gc`                       | double   |                                                   |
| `secuencia`                            | string   | Cadena completa, necesaria para exportar `.fasta` |


### 4.3 `kmers` — un documento por secuencia y por `k`


| Campo           | Tipo     | Contenido                                      |
| --------------- | -------- | ---------------------------------------------- |
| `_id`           | ObjectId | Llave primaria                                 |
| `sequence_id`   | ObjectId | Referencia a `sequences._id`                   |
| `id_seq`        | string   | Desnormalizado para la consulta 15             |
| `k`             | int      | 1 a 6                                          |
| `valid_windows` | int      | Ventanas sin `N`; denominador para frecuencias |
| `counts`        | object   | Solo k-mers con conteo > 0                  |


### 4.4 Índices definidos

El script `database/indices.js` crea todos los índices de la tabla. En la corrida del
benchmark ya existían los dos de `kmers`; los de `species` y `sequences` se crean al
ejecutar el script. La justificación con `explain("executionStats")` se hace en la
instancia con datos (README §6.5).


| Colección   | Índice                                      | Consulta que lo justifica  |
| ----------- | ------------------------------------------- | -------------------------- |
| `species`   | `{especie: 1}` único                        | Cruce y `$lookup` (12, 13) |
| `species`   | `{taxonomy.kingdom: 1}`                     | 3, 6                       |
| `sequences` | `{id_seq: 1}` único                         | 8, 15                      |
| `sequences` | `{species_id: 1}`                           | 2, 4, 9, 12                |
| `sequences` | `{especie: 1}`                              | 2, 10                      |
| `sequences` | `{kingdom: 1}`                              | 3, 6, 7, 11                |
| `sequences` | `{te_classification.clase_fasta: 1}`        | 1, 5                       |
| `sequences` | `{te_classification.orden_fasta: 1}`        | 1, 5, 6                    |
| `sequences` | `{te_classification.superfamilia_fasta: 1}` | 1, 5, 9                    |
| `kmers`     | `{id_seq: 1, k: 1}` único                   | 15                         |
| `kmers`     | `{k: 1, valid_windows: 1}`                  | Q3 del benchmark           |
| `kmers`     | `{sequence_id: 1}`                          | `$lookup` de la Figura 4   |


**Estado de implementación (2026-10-29).** El notebook 03 elimina los índices secundarios
de `kmers` antes de medir la línea base y, al terminar, recrea `{id_seq: 1, k: 1}` (único)
y `{k: 1, valid_windows: 1}` con los mismos nombres y opciones de `database/indices.js`.
El resto de los índices se concentra en ese script, que se ejecuta después de la carga y
puede repetirse sin conflicto.


---

## 5. Decisiones de diseño: cierre

### D-13 · `$jsonSchema` (2026-10-29)

**Contexto.** Se pregunta si se usa validación de esquema y para qué colecciones.  
La base ya estaba poblada cuando se definió la validación, así que debía aplicarse sin  
recrear las colecciones.

**Alternativas.** A) Validar solo en la aplicación, con comprobaciones en Python antes de
cada inserción; B) crear las colecciones desde cero con validador; C) aplicar `collMod`
sobre las colecciones existentes.

**Decisión.** C) Validación estricta en las tres colecciones con
`validationLevel: "strict"` y `validationAction: "error"`, mediante el script
`database/schema_validation.py`.

**Reglas definidas.**

- `species`: exige `especie`, `especie_original`, `es_especie`, `taxonomy` y
  `library_origin`; `kingdom` ∈ {Animalia, Plantae, Fungi}; `source` ∈ {Dfam, RM2+MCH};
  los seis campos del CSV con ausentes aceptan `["string", "null"]`.
- `sequences`: exige `id_seq`, `species_id`, `especie`, `especie_original`, `kingdom`,
  `te_classification`, `metrics` y `secuencia`; `clase_fasta` ∈ {CLASSI, CLASSII};
  `longitud` ≥ 1; conteos ≥ 0; porcentajes en [0, 100].
- `kmers`: exige `sequence_id`, `id_seq`, `k`, `valid_windows` y `counts`; `k` ∈ [1, 6];
  `valid_windows` ≥ 0; `counts` se declara como objeto abierto porque el diccionario es
  disperso.

**Consecuencias.** Cualquier inserción o actualización que incumpla las reglas se rechaza.
El script termina con `db.validate_collection` y reporta `valid=true` si los documentos
existentes cumplen el esquema.

**Estado.** Script definido y listo para ejecutar con la base cargada; la secuencia de
ejecución está en README §6.5. Evidencia: `database/schema_validation.py` y
`database/migrar_especie_original.py`.

### D-14 · Nombre normalizado vs. nombre original de la especie (2026-10-29)

**Contexto.** La llave de cruce `especie` se guarda sin puntos (`Coccomyxa sp obi`), pero
el encabezado del FASTA conserva el punto (`@Coccomyxa sp. obi`). Si se exporta la
biblioteca con la llave normalizada, el encabezado no reproduce el original.

**Alcance real.** En PanTEon v1.6.1 solo cuatro especies cambian al quitar el punto:
*Beta vulgaris* subsp. *vulgaris* (296 secuencias), *Abrus pulchellus* subsp.
*cantoniensis* (178), *Marchantia polymorpha* subsp. *montivagans* (48) y *Coccomyxa*
sp. *obi* (11). Son 533 secuencias de 239.946; no hay colisiones después de normalizar.

**Decisión.** Mantener `especie` como llave normalizada y añadir `especie_original` en
`species` y `sequences`. Las consultas 10 y 11 usan `especie_original` para el encabezado
y `especie` para filtrar y cruzar. Es la opción con menos cambios: no toca los *k*-mers
ni obliga a recargar la base; solo agrega un campo en dos colecciones y actualiza cuatro
nombres.

**Implementación.** `notebooks/01_exploracion_limpieza_normalizacion_cruce.ipynb` conserva
el nombre del FASTA antes de normalizar. Para una base ya cargada,
`database/migrar_especie_original.py` copia `especie` a `especie_original` en todos los
documentos y aplica el mapeo de `database/especies_originales.csv`; el esquema lo exige.

### D-15 · Preguntas propias (2026-10-29)

**Contexto.** Se exige al menos dos preguntas propias además de las 15 consultas  
obligatorias. Debían ser respondibles con el modelo cargado y no repetir los conteos de  
las consultas 1–9.

**Alternativas consideradas.** A) Sesgo por bases `N`; B) concentración de secuencias en
pocas especies; C) composición por origen de la biblioteca; D) dinucleótidos
discriminantes entre órdenes.

**Decisión.** C y D.

**Justificación.** C extiende la consulta 13 y evalúa un posible factor de confusión
(Dfam frente a RM2+MCH) que afecta la validez de las comparaciones entre reinos. D
extiende la Figura 4 y conecta los perfiles de *k*-mers con el objetivo de PanTEon de
diseñar clasificadores de TEs.

**Consecuencias.** C requiere un `$lookup` de `sequences` a `species`; D reutiliza la
agregación de la Figura 4 sobre `kmers` con *k* = 2 y cálculo de rangos/correlaciones en
Python. Ninguna modifica el modelo de datos.

**Estado.** Ejecutadas sobre el respaldo completo de la base. La pregunta 1 encontró
31.592 secuencias de Dfam y 208.354 de RM2+MCH, con composiciones distintas (Dfam: TIR
36,77 % y LTR 34,77 %; RM2+MCH: LTR 52,02 % y LINE 30,10 %), pero confundidas con el reino:
Dfam es 99,88 % Animalia. Al restringir la comparación a Animalia, el patrón TIR/SINE
frente a LINE persiste, pero el sesgo residual por phylum y especie no desaparece. La
pregunta 2 encontró que TT, GG, AA, AT y CC son los dinucleótidos de mayor rango, y que
TIR–HELITRON (0,982) y LTR–LINE (0,962) forman los pares de órdenes más parecidos; los
valores de borde y las correlaciones que dependen de MAVERICK (58 secuencias), CRYPTON
(112) y RETROPOSON (113) son descriptivos y no estimaciones estables. Resultados en
`paper/borrador.md` §IV-E; el cálculo se reproduce con `notebooks/preguntas_propias.py`.

### D-16 · Protocolo del benchmark e índices de `kmers` (2026-10-29)

**Contexto.** La primera corrida midió la línea base sin índices con los índices
`{id_seq, k}` y `{k, valid_windows}` ya creados, así que Q1 y Q2 de la estrategia A dieron
0 ms. Además, el notebook creaba esos índices sin nombre y sin la opción `unique`; al
ejecutar después `database/indices.js`, MongoDB rechazaba la creación por conflicto de
opciones y la colección quedaba sin la restricción de unicidad que exige el modelo.

**Alternativas.** A) Reportar solo el espacio y no medir tiempos; B) crear los índices del
benchmark en colecciones temporales aparte; C) eliminar los índices secundarios antes de
la línea base y recrearlos al final con los nombres y opciones de producción.

**Decisión.** C). El notebook 03 elimina los índices secundarios de `kmers`, hace un
calentamiento y tres repeticiones por consulta, reporta la mediana de
`executionTimeMillis`, `totalDocsExamined` y `totalKeysExamined`, y recrea
`uq_kmers_id_seq_k` (único) e `ix_kmers_k_valid_windows` con los mismos nombres de
`indices.js`.

**Consecuencias.** El orden README §6.4 → §6.5 deja de fallar y la unicidad de
`{id_seq, k}` queda garantizada. Si el notebook se interrumpe después de eliminar los
índices, hay que volver a ejecutarlo o correr `indices.js` antes de usar la base. La
corrida preliminar no permite concluir que Q3 empeore con índice: la diferencia de A
(569 → 555 ms) es de 2,5 % y la de B (535 → 1.217 ms) puede deberse al `FETCH` de
documentos de 33,5 KB; sin `totalDocsExamined`/`totalKeysExamined` es una hipótesis. La
tabla definitiva debe salir de la corrida completa del notebook.

### D-17 · Consultas 10–14, bibliotecas y control de calidad (2026-10-29)

**Contexto.** Las consultas 10–14 cubren la exportación de bibliotecas `.fasta`, la unión
con la taxonomía, la comparación por `Source` y un control de calidad definido por el
equipo. La guía no fija los controles exactos de la consulta 14 ni el tamaño de las
bibliotecas que se versionan.

**Decisión.** Las consultas 10 y 11 escriben el FASTA por streaming, filtran por `especie`
o `kingdom` y reconstruyen el encabezado con `especie_original`. Se versionan
`Malus_domestica.fasta` (1.627 secuencias, 6,6 MB) y `Fungi.fasta` (19.797 secuencias,
74,0 MB). La consulta 14 comprueba referencias huérfanas, `id_seq` duplicados, longitudes
inválidas, caracteres fuera de `{A,C,G,T,N}`, especies sin secuencias y contenido `N`; no
modifica documentos.

**Consecuencias.** Las bibliotecas de Plantae y Animalia superan el límite de 100 MB por
archivo de GitHub y se generan localmente con la misma función. Las 44 entradas que no son
especie se conservan en el corpus y la consulta 4 las excluye cuando el análisis pide
especies. Los conteos de control son 0 huérfanos, 0 duplicados, 0 longitudes inválidas y
0 caracteres inválidos; 54.837 secuencias (22,85 %) contienen al menos una `N`. La etiqueta
`Angiosperma` (418 especies, 116.441 secuencias) se conserva como `Phylum` aunque no sea un
phylum; el hallazgo se documenta en §IV-A y no se reasigna en la base.

**Evidencia.** Notebook `02`, celdas de las consultas 10–14; `notebooks/consultas_analiticas.py`;
`libraries/Malus_domestica.fasta`; `libraries/Fungi.fasta`; y tabla VI del artículo.

---

## 6. Plantilla para nuevas entradas

```text
D-XX · 2026-MM-DD · <título corto>

Contexto:      qué problema obligó a decidir.
Alternativas:  A) …  B) …
Decisión:      cuál se tomó.
Justificación: por qué esa y no las otras.
Consecuencias: qué consulta o índice se ve afectado.
Evidencia:     notebook/celda, resultado de explain o tabla del benchmark.
```
