# Modelo documental en MongoDB para elementos transponibles y perfiles de *k*-mers

**Proyecto del segundo corte — Bases de Datos II**
Programa de Ingeniería de Sistemas · Universidad Autónoma de Manizales
Docente: Simón Gaviria Orrego

---

## 1. Descripción

Este repositorio contiene el diseño, la implementación y la evaluación de una base de
datos documental en **MongoDB** que integra las dos fuentes de **PanTEon Database
v1.6.1**:

- un archivo **FASTA** con ~240.000 secuencias de elementos transponibles (TEs),
- un archivo **CSV** con la taxonomía y el origen de la biblioteca de cada especie,

y que además calcula, almacena y expone los **perfiles de *k*-mers (*k* = 1 … 6)** de
cada secuencia.

El objetivo del curso no es solo cargar los datos: se evalúa **cómo se piensa el
problema** — qué alternativas se consideran, cuáles se descartan, por qué, y cómo se
demuestra experimentalmente que el diseño funciona. Por eso el repositorio incluye
también un **benchmark de almacenamiento** y un **artículo científico** en formato IEEE.

Línea de base del problema:

| Métrica | Valor |
|---|---|
| Secuencias en la base | ~240.000 |
| *k*-mers posibles por secuencia (*k* = 1…6) | 4 + 16 + 64 + 256 + 1.024 + 4.096 = **5.460** |
| Pares clave-valor si se guardara de forma densa e ingenua | ~1,3 × 10⁹ |

---

## 2. Autores

| Integrante | Rol principal | Contacto |
|---|---|---|
| Johan Andrés Villada Valencia | Arquitectura de datos, repositorio y artículo | — |
| _Por completar_ | Ingeniería de datos, limpieza y calidad biológica | — |
| _Por completar_ | Motor de *k*-mers, carga masiva y benchmark | — |
| _Por completar_ | Consultas analíticas y visualización | — |

---

## 3. Fuente de datos

**PanTEon Database v1.6.1** — Zenodo, licencia **CC BY 4.0**:
<https://zenodo.org/records/19372616>

| Archivo | Contenido | Tamaño | ¿Se versiona? |
|---|---|---|---|
| `PanTEon_Database_v1.6.1.fasta` | Secuencias de los TEs | 992.180.168 B (~946 MiB) | **No** |
| `PanTEon_Database_metadata_v1.6.1.csv` | Metadatos y taxonomía por especie | 371.391 B (~363 KiB) | **No** |

El resto de archivos del repositorio de Zenodo (`.zip` de modelos entrenados y la
*benchmark edition*) **no** son necesarios para este proyecto.

> El FASTA supera el límite de 100 MB por archivo de GitHub, por eso los datos crudos
> van en `data_raw/`, que está en `.gitignore`.

---

## 4. Estructura del repositorio

```text
panteon-mongodb-bd2/
├── README.md                          # Entregable 1 · descripción y reproducción
├── JOURNAL.md                         # Entregable 8 · revista y normas aplicadas
├── .gitignore                         # bloquea datos crudos y artefactos de compilación
│
├── notebooks/
│   ├── 01_pipeline_extraccion.ipynb   # Entregable 2 · limpieza, cruce, k-mers y carga
│   ├── 02_consultas_y_figuras.ipynb   # Entregable 3 · consultas y figuras de la §4.5
│   └── 03_experimentos_diseno.ipynb   # Entregable 4 · evaluación experimental (§4.4)
│
├── database/                          # Entregable 5 · mongodump o script regenerador
├── libraries/                         # Entregable 6 · bibliotecas .fasta (consultas 10 y 11)
│
├── paper/                             # Entregable 7 · artículo
│   ├── main.tex
│   ├── references.bib
│   └── figures/
│
└── docs/
    └── decisiones.md                  # bitácora de decisiones de diseño (insumo del paper)
```

---

## 5. Rol de cada notebook

| Notebook | Contenido mínimo exigido por la guía |
|---|---|
| `01_pipeline_extraccion.ipynb` | Lectura y validación del FASTA (encabezado, caracteres válidos, `N`, longitudes) · limpieza del CSV (9 columnas) · cruce por especie y reporte de huérfanos en ambos sentidos · atributos derivados (longitud, %GC, %N) · cálculo de *k*-mers *k* = 1…6 · carga con `insert_many`/`bulk_write` |
| `02_consultas_y_figuras.ipynb` | Consultas 1–15 + 2 preguntas propias, cada una con pregunta, código, resultado e interpretación · las 4 figuras de la §4.5 leídas desde MongoDB |
| `03_experimentos_diseno.ipynb` | Dos estrategias de almacenamiento de *k*-mers · tiempo de carga · `collStats` · 3 consultas con y sin índice usando `explain("executionStats")` · tablas y gráficos comparativos |

---

## 6. Reproducción desde cero

### 6.1 Requisitos

```bash
pip install pymongo pandas biopython numpy matplotlib seaborn
```

- Python ≥ 3.10
- MongoDB ≥ 7.0 (servidor local o instancia accesible)
- Entorno previsto: **Google Colab** (autorizado por el docente) o local

### 6.2 Descargar los datos

```bash
mkdir -p data_raw

curl -L -o data_raw/PanTEon_Database_v1.6.1.fasta \
  "https://zenodo.org/api/records/19372616/files/PanTEon_Database_v1.6.1.fasta/content"

curl -L -o data_raw/PanTEon_Database_metadata_v1.6.1.csv \
  "https://zenodo.org/api/records/19372616/files/PanTEon_Database_metadata_v1.6.1.csv/content"
```

Verificación de integridad (MD5 publicado por Zenodo):

```text
222bfd9899d866ca06cda062fc3c52ff  PanTEon_Database_v1.6.1.fasta
7f4ea0ef9c242d2ccf4c0ee723c9f08c  PanTEon_Database_metadata_v1.6.1.csv
```

### 6.3 Levantar MongoDB

> **Pendiente de documentar por el equipo.** Debe quedar aquí el procedimiento exacto
> (comando `mongod --dbpath … --logpath …`, variables de conexión y cómo se restaura el
> respaldo del entregable 5). Sin este paso el README no cumple el requisito de
> reproducibilidad.

### 6.4 Ejecutar el pipeline

> **Pendiente de documentar por el equipo**: orden de ejecución de los notebooks,
> tiempo estimado y salidas esperadas.

### 6.5 Compilar el artículo

```bash
cd paper
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

El resultado es `paper/main.pdf`.

---

## 7. Flujo de trabajo (GitFlow parcial)

Se usa un GitFlow reducido, sin ramas `release/*` ni `hotfix/*`:

| Rama | Propósito |
|---|---|
| `main` | Solo versiones entregables (hitos y entrega final) |
| `develop` | Integración del trabajo del equipo; rama por defecto durante el desarrollo |
| `feature/pipeline-limpieza` | Notebook 01 y bibliotecas `.fasta` |
| `feature/kmers-benchmark` | Notebook 03 y motor de *k*-mers |
| `feature/consultas-visualizacion` | Notebook 02 y figuras |
| `feature/modelo-paper` | Modelo de datos, `docs/`, `paper/` y `JOURNAL.md` |

Reglas mínimas:

1. Nadie hace *commit* directo a `main`.
2. Cada `feature/*` sale de `develop` y vuelve a `develop` por *pull request*.
3. `main` solo recibe `develop` cuando el hito está cerrado y compila.
4. Mensajes de *commit* en formato Conventional Commits: `feat:`, `fix:`, `docs:`,
   `chore:`, `refactor:`.

---

## 8. Mapa de entregables

| # | Entregable | Ruta en el repo | Estado |
|---|---|---|---|
| 1 | README con descripción e instrucciones | `README.md` | 🟡 esqueleto |
| 2 | Notebook del pipeline de extracción | `notebooks/01_pipeline_extraccion.ipynb` | ⏳ pendiente |
| 3 | Consultas, resultados y figuras §4.5 | `notebooks/02_consultas_y_figuras.ipynb` | ⏳ pendiente |
| 4 | Experimentos de la §4.4 | `notebooks/03_experimentos_diseno.ipynb` | ⏳ pendiente |
| 5 | Respaldo `mongodump` o script regenerador | `database/` | ⏳ pendiente |
| 6 | Bibliotecas `.fasta` (≥ 1 especie y ≥ 1 reino) | `libraries/` | ⏳ pendiente |
| 7 | Artículo en PDF + fuentes `.tex` y `.bib` | `paper/` | 🟡 esqueleto |
| 8 | `JOURNAL.md` con revista y normas | `JOURNAL.md` | ✅ |

Leyenda: ✅ listo · 🟡 esqueleto · ⏳ pendiente.

---

## 9. Uso de herramientas de IA

La guía del curso (§7) permite IA **solo para contextualización** (entender conceptos,
el dominio biológico o la documentación de herramientas). El modelo de datos, el código
y el texto del artículo son elaborados por el equipo. Cualquier código, herramienta o
texto de terceros debe citarse.

---

## 10. Citación

Si usa este repositorio o los datos, cite:

```text
Orozco-Arias S, Ferrer-Pomer I, Rodrigues de Góes F, Gaviria-Orrego S,
Gómiz-Fernández J, Llatser Torres J, Paschoal AR, Guyot R, Gabaldón T. (2026).
PanTEon: a cross-kingdom framework to guide the design of transposable element
classifiers. bioRxiv. https://doi.org/10.64898/2026.04.01.715927

PanTEon Database v1.6.1. Zenodo. https://doi.org/10.5281/zenodo.19372616
```

---

## 11. Licencia

Los datos se usan bajo la licencia **CC BY 4.0** del repositorio original. El código de
este repositorio se distribuye con fines académicos.
