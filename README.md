# AgentTRAD — Traductor de plugins WP Connect

Agente de Claude Code para traducir las cadenas (`.po`/`.pot`) de los plugins de
**WP Connect** a cualquier idioma, **reutilizando primero** las traducciones que
ya existen en el proyecto (memoria de traducción) y traduciendo solo las cadenas
nuevas.

## Uso

1. Deja el archivo de origen del plugin en [`pot/`](pot/) con el slug como nombre:
   `pot/<slug>.pot` (plantilla en inglés) o `pot/<slug>.po` (con `msgstr` vacíos).
2. Ejecuta el comando:

   ```
   /traducir <slug> <idioma>
   ```

   Ejemplo: `/traducir wp-connect-foo fr`
3. El resultado se genera en la raíz como `<slug>-<idioma>.po`.

## Cómo funciona

1. **Mira primero el registro**: construye una memoria con todos los `.po` del
   mismo idioma destino y reutiliza las **coincidencias exactas** tal cual
   (consistencia entre plugins).
2. **Solo traduce lo que no conoce**: las cadenas ausentes del registro se
   traducen respetando marcadores (`%s`, `%1$s`), HTML, plurales, espacios y sin
   tocar nombres de marca (`WP connect`, `Notion`, `Airtable`...).
3. **Verifica** que no quede ninguna cadena vacía.

Cada `.po` generado pasa a formar parte del registro para las siguientes
traducciones del mismo idioma.

## Estructura

```
.claude/
├── agents/traductor-plugins.md   Subagente con la metodología
└── commands/traducir.md          Comando /traducir
scripts/
├── tm_match.py                   Reutiliza del registro + lista pendientes
└── tm_apply.py                   Vuelca las traducciones nuevas al .po
pot/                              Archivos de origen a traducir
*.po                              Registro de traducciones (memoria)
```

## Requisitos

- Python 3 con [`polib`](https://pypi.org/project/polib/): `pip install polib`
