---
description: Traduce las cadenas de un plugin a uno o varios idiomas, reutilizando el registro y empaquetando el resultado en languages.zip
argument-hint: <plugin> <idioma> [idioma2 idioma3 ...]
---

Traduce el plugin **`$1`** a los idiomas indicados: **`$2 $3 $4 $5 $6`** (ignora
los que estén vacíos; el primer argumento es el plugin y el resto son idiomas).

Lanza el subagente `traductor-plugins` (vía la herramienta Agent) pasándole esta
instrucción: «Traduce el plugin `$1` a los idiomas `$2 $3 $4 $5 $6` (descarta los
vacíos). Para cada idioma sigue tu procedimiento: reutiliza primero las
coincidencias exactas del registro con `tm_match.py`, traduce únicamente las
cadenas pendientes, aplícalas con `tm_apply.py` y verifica que no queden cadenas
vacías. Cuando termines TODOS los idiomas, empaqueta los `.po` generados en
`languages.zip` con `tm_pack.py` y limpia los temporales.»

Antes de lanzarlo:
- El archivo de origen debe existir en `pot/$1.pot` o `pot/$1.po`. Si no existe,
  díselo al usuario y no sigas.

Cuando el subagente termine, muéstrame su resumen: por cada idioma cuántas
cadenas se reutilizaron del registro y cuántas se tradujeron nuevas, y la ruta de
`languages.zip`.
