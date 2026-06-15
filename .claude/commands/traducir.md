---
description: Traduce las cadenas de un plugin a un idioma, reutilizando el registro de traducciones existente
argument-hint: <plugin> <idioma>
---

Traduce el plugin **`$1`** al idioma **`$2`**.

Lanza el subagente `traductor-plugins` (vía la herramienta Agent) pasándole esta
instrucción: «Traduce el plugin `$1` al idioma `$2` siguiendo tu procedimiento:
reutiliza primero las coincidencias exactas del registro con `tm_match.py`,
traduce únicamente las cadenas pendientes, aplícalas con `tm_apply.py`, verifica
que no queden cadenas vacías y limpia los temporales.»

Antes de lanzarlo:
- El archivo de origen debe existir en `pot/$1.pot` o `pot/$1.po` (plantilla del
  plugin con las cadenas en inglés). Si no existe, díselo al usuario y no sigas.

Cuando el subagente termine, muéstrame su resumen: cuántas cadenas se
reutilizaron del registro, cuántas se tradujeron nuevas y la ruta del `.po`
generado (`$1-$2.po`).
