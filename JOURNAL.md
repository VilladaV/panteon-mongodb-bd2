# Selección de revista y normas aplicadas

---

## 1. Revista seleccionada


| Campo                                      | Valor                                                                                                                                                                                                                                                                  |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Nombre**                                 | IEEE/ACM Transactions on Computational Biology and Bioinformatics (**TCBB**)                                                                                                                                                                                           |
| **Editorial**                              | IEEE Computer Society / ACM                                                                                                                                                                                                                                            |
| **ISSN**                                   | 1545-5963 (impreso) · 1557-9964 (electrónico)                                                                                                                                                                                                                          |
| **Guía de autores**                        | [https://www.computer.org/csdl/journal/tb/write-for-us](https://www.computer.org/csdl/journal/tb/write-for-us)                                                                                                                                                         |
| **Información para autores (PDF oficial)** | [https://ieeexplore.ieee.org/document/5535013](https://ieeexplore.ieee.org/document/5535013)                                                                                                                                                                           |
| **Plantillas IEEE (Author Center)**        | [https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/authoring-tools-and-templates/ieee-article-templates/](https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/authoring-tools-and-templates/ieee-article-templates/) |
| **Plantilla LaTeX usada**                  | `IEEEtran.cls` con `\documentclass[journal]{IEEEtran}`                                                                                                                                                                                                                 |
| **Estilo bibliográfico**                   | `IEEEtran.bst` (citación numérica secuencial)                                                                                                                                                                                                                          |


---

## 2. Justificación de la elección

1. **El núcleo del trabajo es ingeniería de datos, no biología descriptiva.** El aporte
 es un modelo documental en MongoDB, un pipeline reproducible en Python y un
 benchmark de almacenamiento; TCBB publica precisamente arquitecturas y métodos
 computacionales aplicados a datos biológicos.
2. **Diseño de esquema no relacional con justificación de alternativas.** La guía del  
 curso pide documentar qué se embebe, qué se referencia y qué índices se crean. Ese debate encaja en el perfil de la revista, orientada a métodos y  
 herramientas reproducibles.
3. **Evaluación experimental obligatoria.** TCBB exige resultados medidos; el proyecto
 mide tiempo de carga, espacio en disco (`collStats`) y planes de ejecución
 (`explain("executionStats")`), lo que da material real de *Results* y *Discussion*.

---

## 3. Normas aplicadas al manuscrito


| Elemento                    | Norma de la revista                                                                                                  | Cómo se aplica en este repositorio              |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| **Documento**               | `IEEEtran`, modo *journal*: dos columnas, 10 pt, papel carta (*letterpaper*), márgenes de la clase                   | `paper/main.tex`                                |
| **Extensión**               | Artículo regular: hasta **14 páginas a doble columna**, incluidas referencias y biografías                           | Objetivo interno: 8–12 páginas                  |
| **Idioma**                  | Inglés                                                                                                               | **Desviación autorizada por el curso** (ver §4) |
| **Título**                  | Conciso, sin abreviaturas no estándar                                                                                | `\title{}` en `main.tex`                        |
| **Resumen**                 | **100–200 palabras** para artículo regular, un solo párrafo, sin referencias ni ecuaciones                           | Bloque `abstract`                               |
| **Palabras clave**          | Bloque `IEEEkeywords`, en orden alfabético                                                                           | Bloque `IEEEkeywords`                           |
| **Secciones**               | Numeración romana generada por la clase (`I.`, `II.`, …)                                                             | `\section{}`                                    |
| **Figuras**                 | ≥ 300 dpi, legibles en una columna (\~88 mm) o dos (\~181 mm); leyenda **debajo**; referencia en texto como `Fig. 1` | `paper/figures/`                                |
| **Tablas**                  | Numeración romana (`TABLA I`), título **arriba**, sin líneas verticales                                              | `booktabs`                                      |
| **Ecuaciones**              | Numeradas entre paréntesis, alineadas a la derecha                                                                   | `equation` / `align`                            |
| **Citas**                   | Numéricas entre corchetes en orden de aparición, `[1]`, `[2]`                                                        | `\cite{}` + `IEEEtran.bst`                      |
| **Referencias**             | Lista numerada al final, generada por BibTeX                                                                         | `paper/references.bib`                          |
| **Disponibilidad de datos** | Sección final con enlace al repositorio y forma de reproducción                                                      | `\section*{Disponibilidad de datos y código}`   |


### Citas obligatorias del curso (§3)

- Orozco-Arias *et al.* (2026), *PanTEon: a cross-kingdom framework…* → `orozco2026panteon`
- PanTEon Database v1.6.1, Zenodo → `panteon2026zenodo`

---

## 4. Desviaciones documentadas


| Norma de la revista           | Qué se hace en este trabajo | Motivo                                                    |
| ----------------------------- | --------------------------- | --------------------------------------------------------- |
| Idioma inglés                 | Manuscrito en **español**   | Consistencia y facil entendimiento en el grupo de trabajo |
| Extensión ≤ 14 páginas        | Se apunta a 8–12            | El trabajo es un ejercicio académico, no un envío real    |
| Proceso de revisión por pares | No aplica                   | Trabajo de curso                                          |


Estas desviaciones se limitan a lo anterior: **formato, estructura, estilo de citas,
figuras y tablas sí siguen la plantilla IEEE**, porque es lo que se evalúa.

---

---

## 5. Historial de cambios


| Fecha      | Cambio                                                     | Autor  |
| ---------- | ---------------------------------------------------------- | ------ |
| 2026-10-23 | Creación del archivo; selección de TCBB y normas iniciales | Equipo |
