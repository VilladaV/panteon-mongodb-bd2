# Bitácora de decisiones de diseño

> **Para qué sirve.** La guía del curso (§8) advierte que *“las decisiones de diseño se
> olvidan si no se documentan en el momento”*. Cada fila de esta tabla es,
> literalmente, un párrafo de la sección **III-B (Modelo de datos y decisiones de
> diseño)** del artículo. Se llena **cuando se decide**, no al final.
>
> Regla de oro: si una decisión no tiene una alternativa descartada y una razón, todavía
> no está tomada; está pendiente.

---

## 1. Decisiones registradas

| # | Fecha | Decisión | Alternativas consideradas | Por qué se eligió | Impacto (consulta / índice / benchmark) | Responsable |
|---|---|---|---|---|---|---|
| D-01 | | | | | | |
| D-02 | | | | | | |
| D-03 | | | | | | |

---

## 2. Decisiones pendientes de tomar

Las preguntas de la §4.1 de la guía, convertidas en tareas. Marcar solo cuando exista
una fila correspondiente en la tabla de arriba.

- [ ] **Entidades y colecciones.** ¿Qué entidades se identifican y en qué colección
      queda cada una? (candidatas: `sequences`, `species`/`taxonomy`, `kmer_profiles`)
- [ ] **Embebido vs. referencia.** ¿Qué se embebe y qué se referencia? Justificar por
      patrón de acceso, no por intuición.
- [ ] **Representación de la jerarquía del TE.** ¿Objeto anidado
      `te_classification: {class, order, superfamily}` o tres campos planos?
      *Ojo con la colisión con `Class`/`Order` taxonómicos del CSV.*
- [ ] **Representación de la taxonomía de la especie.** ¿Embebida en la secuencia,
      en colección aparte, o ambas (desnormalización justificada)?
- [ ] **Representación de los *k*-mers.** ¿Conteos o frecuencias? ¿Arreglo denso,
      diccionario disperso, un documento por *k* o colección aparte? ¿Embebidos o
      separados? *(Esta decisión es la que se evalúa en la §4.4.)*
- [ ] **Política de caracteres ambiguos.** ¿Qué pasa con una ventana de longitud *k*
      que contiene `N` u otro carácter fuera de `{A, C, G, T}`? Debe quedar definido y
      documentado, y reportarse en la consulta 14.
- [ ] **Valores faltantes y nombres inconsistentes.** Regla de normalización de especies
      (espacios, mayúsculas) y criterio para registros que no cruzan.
- [ ] **Índices.** ¿Qué índice crea cada consulta? Cada índice debe tener una consulta
      que lo justifique y una medición con `explain("executionStats")`.
- [ ] **Validación de esquema.** ¿Se usa `$jsonSchema`? ¿En qué colecciones y con qué
      nivel de rigor (`validationLevel`, `validationAction`)?
- [ ] **Identificadores.** `_id` ObjectId generado por MongoDB + campo `panteon_id`
      (`PDB…`) indexado. Definir si es único.

---

## 3. Estructura sugerida de una entrada

```text
D-XX · 2026-MM-DD · <título corto de la decisión>

Contexto:      qué problema obligó a decidir.
Alternativas:  A) …  B) …  C) …
Decisión:      cuál se tomó.
Justificación: por qué esa y no las otras (criterio medible si es posible).
Consecuencias: qué se gana, qué se pierde, qué consulta o índice se ve afectado.
Evidencia:     enlace al notebook/celda, al resultado de explain o a la tabla del benchmark.
```

---

## 4. Registro de experimentos

> Insumo directo de la §4.4 y de la sección IV-B del artículo. Un experimento sin
> condiciones registradas no es reproducible.

| Exp. | Fecha | Hipótesis | Estrategia A | Estrategia B | Métricas | Resultado | Conclusión |
|---|---|---|---|---|---|---|---|
| E-01 | | | | | tiempo de carga · `collStats` · 3 consultas con/sin índice | | |
