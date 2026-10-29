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

GitHub rechaza archivos de más de 100 MB. Si la biblioteca de un reino completo supera ese
límite, se genera un subconjunto con un criterio explícito (por ejemplo, las especies con
al menos 50 secuencias), se documenta el criterio en este archivo y se refleja en el nombre
(`Fungi_min50.fasta`).
