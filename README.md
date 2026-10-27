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
cada secuencia

Línea de base del problema:


| Métrica                                                   | Valor                                         |
| --------------------------------------------------------- | --------------------------------------------- |
| Secuencias en la base                                     | \~240.000                                     |
| *k*-mers posibles por secuencia (*k* = 1…6)               | 4 + 16 + 64 + 256 + 1.024 + 4.096 = **5.460** |
| Pares clave-valor si se guardara de forma densa e ingenua | \~1,3 × 10⁹                                   |


---

## 2. Equipo y reparto del trabajo


| Integrante                     | Parte                                                     | Estado   |
| ------------------------------ | --------------------------------------------------------- | -------- |
| María Camila Prada Cortes      | 1 · Limpieza del CSV, parseo del FASTA, cruce y atributos | Listo    |
| Santiago Jimenez Cotrini       | 2 · motor de k-mers, carga masiva, benchmark y consulta 15 | En curso |
| Cristian Camilo Arenas Salazar | 3 · consultas 1–9 y figuras                               | En curso |
| Johan Andrés Villada Valencia  | 4 · Modelo de datos, repositorio y artículo               | En curso |


---

## 3. Fuente de datos

**PanTEon Database v1.6.1** — Zenodo, licencia **CC BY 4.0**:
[https://zenodo.org/records/19372616](https://zenodo.org/records/19372616)


| Archivo                                | Contenido                         | Tamaño                    | ¿Se versiona? |
| -------------------------------------- | --------------------------------- | ------------------------- | ------------- |
| `PanTEon_Database_v1.6.1.fasta`        | Secuencias de los TEs             | 992.180.168 B (\~946 MiB) | **No**        |
| `PanTEon_Database_metadata_v1.6.1.csv` | Metadatos y taxonomía por especie | 371.391 B (\~363 KiB)     | **No**        |


---

## 4. Estructura del repositorio

```text
panteon-mongodb-bd2/
├── README.md                          # 1 · descripción y reproducción
├── JOURNAL.md                         # 8 · revista y normas aplicadas
├── .gitignore                         # 
│
├── notebooks/
│   ├── 01_exploracion_limpieza_normalizacion_cruce.ipynb   # 2 · limpieza, cruce y atributos
│   ├── 02_consultas_y_figuras.ipynb   # 3 · consultas y figuras de la §4.5
│   └── 03_experimentos_diseno.ipynb   # 4 · evaluación experimental (§4.4)
│
├── database/                          # 5 · mongodump o script regenerador
├── libraries/                         # 6 · bibliotecas .fasta (consultas 10 y 11)
│
├── paper/                             # 7 · artículo
│   ├── main.tex
│   ├── references.bib
│   └── figures/
│
└── docs/
    └── decisiones.md                  # bitácora de decisiones de diseño
```

---

## 5. Rol de cada notebook


| Notebook                                            | Contenido mínimo exigido por la guía                                                                                                                                                                                    |
| --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `01_exploracion_limpieza_normalizacion_cruce.ipynb` | Lectura y validación del FASTA (encabezado, caracteres válidos, `N`, longitudes) · limpieza del CSV (9 columnas) · cruce por especie y reporte de huérfanos en ambos sentidos · atributos derivados (longitud, %GC, %N) |
| `02_consultas_y_figuras.ipynb`                      | Consultas 1–9, cada una con pregunta, código, resultado e interpretación · las 4 figuras de la §4.5 leídas desde MongoDB                                                                         |
| `03_experimentos_diseno.ipynb`                      | Dos estrategias de almacenamiento de *k*-mers · tiempo de carga · `collStats` · 3 consultas con y sin índice usando `explain("executionStats")` · tablas y gráficos comparativos                                        |

Las consultas 10–14 (bibliotecas `.fasta` por especie y reino y comparación Dfam vs.
RM2+MCH) las aporta la parte 1; la consulta 15, la parte 2. Las dos preguntas propias se
formulan entre las partes 1 y 4.


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

> **Pendiente**

### 6.4 Ejecutar el pipeline

> **Pendiente**

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

## 7. Citación

Si usa este repositorio o los datos, cite:

```text
Orozco-Arias S, Ferrer-Pomer I, Rodrigues de Góes F, Gaviria-Orrego S,
Gómiz-Fernández J, Llatser Torres J, Paschoal AR, Guyot R, Gabaldón T. (2026).
PanTEon: a cross-kingdom framework to guide the design of transposable element
classifiers. bioRxiv. https://doi.org/10.64898/2026.04.01.715927

PanTEon Database v1.6.1. Zenodo. https://doi.org/10.5281/zenodo.19372616
```

---

## 8. Licencia

Los datos se usan bajo la licencia **CC BY 4.0** del repositorio original. El código de
este repositorio se distribuye con fines académicos.