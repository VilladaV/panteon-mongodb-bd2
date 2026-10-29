# Bibliotecas `.fasta`

Las consultas 10 y 11 exportan subconjuntos de `sequences` en el mismo formato del
FASTA de PanTEon:

```text
>ID#CLASE/ORDEN/SUPERFAMILIA @Especie original
ACGT...
```

El nombre de la especie se toma de `especie_original` para conservar los puntos que la
llave normalizada elimina. Los archivos se nombran con la especie o el reino consultado,
por ejemplo `Malus_domestica.fasta` o `Fungi.fasta`, y no se versionan si superan el
tamaño razonable para Git; se regeneran desde MongoDB con el notebook 02.
