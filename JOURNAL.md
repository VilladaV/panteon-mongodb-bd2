# Selección de revista y normas aplicadas

> Entregable 8 de la guía (§6). Este archivo debe declarar la revista elegida, el enlace
> a su guía de autores y **la lista de las normas que efectivamente se aplicaron** al
> manuscrito. Si la revista no está en la tabla sugerida de la guía (§5.1), aquí se
> justifica la elección.

---

## 1. Revista seleccionada

| Campo | Valor |
|---|---|
| **Nombre** | IEEE/ACM Transactions on Computational Biology and Bioinformatics (**TCBB**) |
| **Editorial** | IEEE Computer Society / ACM |
| **ISSN** | 1545-5963 (impreso) · 1557-9964 (electrónico) |
| **Guía de autores** | <https://www.computer.org/csdl/journal/tb/write-for-us> |
| **Información para autores (PDF oficial)** | <https://ieeexplore.ieee.org/document/5535013> |
| **Plantillas IEEE (Author Center)** | <https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/authoring-tools-and-templates/ieee-article-templates/> |
| **Plantilla LaTeX usada** | `IEEEtran.cls` con `\documentclass[journal]{IEEEtran}` |
| **Estilo bibliográfico** | `IEEEtran.bst` (citación numérica secuencial) |

---

## 2. Justificación de la elección (revista fuera de la tabla de la guía)

TCBB **no** aparece en la tabla de la §5.1 del documento del curso, por lo que la guía
exige justificar la elección. Los argumentos son:

1. **El núcleo del trabajo es ingeniería de datos, no biología descriptiva.** El aporte
   es un modelo documental en MongoDB, un pipeline reproducible en Python y un
   benchmark de almacenamiento; TCBB publica precisamente arquitecturas y métodos
   computacionales aplicados a datos biológicos.
2. **Diseño de esquema no relacional con justificación de alternativas.** La guía del
   curso pide documentar qué se embebe, qué se referencia y qué índices se crean
   (§4.1). Ese debate encaja en el perfil de la revista, orientada a métodos y
   herramientas reproducibles.
3. **Evaluación experimental obligatoria.** TCBB exige resultados medidos; el proyecto
   mide tiempo de carga, espacio en disco (`collStats`) y planes de ejecución
   (`explain("executionStats")`), lo que da material real de *Results* y *Discussion*.

---

## 3. Normas aplicadas al manuscrito

| Elemento | Norma de la revista | Cómo se aplica en este repositorio |
|---|---|---|
| **Documento** | `IEEEtran`, modo *journal*: dos columnas, 10 pt, papel carta (*letterpaper*), márgenes de la clase | `paper/main.tex` |
| **Extensión** | Artículo regular: hasta **14 páginas a doble columna**, incluidas referencias y biografías | Objetivo interno: 8–12 páginas |
| **Idioma** | Inglés | **Desviación autorizada por el curso** (ver §4) |
| **Título** | Conciso, sin abreviaturas no estándar | `\title{}` en `main.tex` |
| **Resumen** | **100–200 palabras** para artículo regular, un solo párrafo, sin referencias ni ecuaciones | Bloque `abstract` |
| **Palabras clave** | Bloque `IEEEkeywords`, en orden alfabético | Bloque `IEEEkeywords` |
| **Secciones** | Numeración romana generada por la clase (`I.`, `II.`, …) | `\section{}` |
| **Figuras** | ≥ 300 dpi, legibles en una columna (~88 mm) o dos (~181 mm); leyenda **debajo**; referencia en texto como `Fig. 1` | `paper/figures/` |
| **Tablas** | Numeración romana (`TABLA I`), título **arriba**, sin líneas verticales | `booktabs` |
| **Ecuaciones** | Numeradas entre paréntesis, alineadas a la derecha | `equation` / `align` |
| **Citas** | Numéricas entre corchetes en orden de aparición, `[1]`, `[2]` | `\cite{}` + `IEEEtran.bst` |
| **Referencias** | Lista numerada al final, generada por BibTeX | `paper/references.bib` |
| **Disponibilidad de datos** | Sección final con enlace al repositorio y forma de reproducción | `\section*{Disponibilidad de datos y código}` |

### Citas obligatorias del curso (§3)

Ambas deben aparecer en el texto, no solo en la bibliografía:

- Orozco-Arias *et al.* (2026), *PanTEon: a cross-kingdom framework…* → `orozco2026panteon`
- PanTEon Database v1.6.1, Zenodo → `panteon2026zenodo`

> Los datos de autoría de `references.bib` se verificaron contra la API de Zenodo
> (`https://zenodo.org/api/records/19372616`) el 2026-10-23. La lista de autores del
> depósito difiere en varios nombres de pila respecto a borradores previos del equipo:
> **Ferrer-Pomer, Iamil**; **Rodrigues de Góes, Fabiana**; **Gómiz-Fernández, Juan**;
> **Llatser Torres, Jordi**. No se deben “corregir” a ojo.

---

## 4. Desviaciones documentadas

| Norma de la revista | Qué se hace en este trabajo | Motivo |
|---|---|---|
| Idioma inglés | Manuscrito en **español** | La guía del curso (§5.1) permite español o inglés |
| Extensión ≤ 14 páginas | Se apunta a 8–12 | El trabajo es un ejercicio académico, no un envío real |
| Proceso de revisión por pares | No aplica | Trabajo de curso |

Estas desviaciones se limitan a lo anterior: **formato, estructura, estilo de citas,
figuras y tablas sí siguen la plantilla IEEE**, porque es lo que se evalúa.

---

## 5. Verificación pendiente antes de la entrega

- [ ] Confirmar en el portal de la revista la **extensión máxima vigente** (el límite de
      14 páginas proviene del documento *Information for Authors*; puede actualizarse).
- [ ] Confirmar el **límite de palabras del resumen** vigente (100–200 aquí).
- [ ] Revisar si TCBB exige *graphical abstract*, ORCID o *author biography*.
- [ ] Verificar el **DOI del preprint de PanTEon** en bioRxiv antes de congelarlo.
- [ ] Compilar `main.tex` sin *warnings* de referencias cruzadas ni de BibTeX.
- [ ] Confirmar que `main.pdf` tenga las fuentes incrustadas (IEEE lo exige).

---

## 6. Historial de cambios

| Fecha | Cambio | Autor |
|---|---|---|
| 2026-10-23 | Creación del archivo; selección de TCBB y normas iniciales | Equipo |
