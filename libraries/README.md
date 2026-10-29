# Bibliotecas `.fasta`

Las consultas 10 y 11 exportan subconjuntos de `sequences` en el mismo formato del
FASTA de PanTEon:

```text
>ID#CLASE/ORDEN/SUPERFAMILIA @Especie original
ACGT...
```

El nombre de la especie se toma de `especie_original` para conservar los puntos que la
llave normalizada elimina. Los archivos se nombran con la especie o el reino consultado,
por ejemplo `Malus_domestica.fasta` o `Fungi.fasta`, y **sí se versionan** (entregable 6).

## Archivos generados

| Archivo | Consulta | Filtro | Secuencias | Tamaño |
|---|---|---|---:|---:|
| `Malus_domestica.fasta` | 10 | `especie = "Malus domestica"` | 1.627 | 6,6 MB |
| `Fungi.fasta` | 11 | `kingdom = "Fungi"` | 19.797 | 74,0 MB |

Las dos bibliotecas se generan desde `sequences` y conservan el encabezado original. Para
otra especie o reino basta cambiar el parámetro en la consulta 10 o 11 del notebook 02.

GitHub rechaza archivos de más de 100 MB. Si la biblioteca de un reino completo supera ese
límite, se genera un subconjunto con un criterio explícito (por ejemplo, las especies con
al menos 50 secuencias), se documenta el criterio en este archivo y se refleja en el nombre
(`Fungi_min50.fasta`). Las bibliotecas completas de Plantae y Animalia superan ese límite;
por eso aquí se versiona Fungi, que sí cabe completo, y las otras dos se generan localmente
con la misma función.
