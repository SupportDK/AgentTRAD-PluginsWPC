# AgentTRAD — WP connect plugin translator

Claude Code agent that translates the strings (`.po`/`.pot`) of the **WP connect**
plugins into any language, **reusing first** the translations that already exist
in the project (translation memory) and translating only the new strings.

## Usage

1. Drop the plugin source file into [`pot/`](pot/), named with the plugin slug:
   `pot/<slug>.pot` (English template) or `pot/<slug>.po` (with empty `msgstr`).
2. Run the command with one or more languages:

   ```
   /traducir <slug> <language> [language2 language3 ...]
   ```

   Examples:
   - `/traducir wp-connect-foo fr`
   - `/traducir wp-connect-foo fr de it`  (multi-language in a single run)
3. Each `<slug>-<language>.po` is written to the project root (and feeds the
   registry), and all of them are bundled into `languages.zip` (inside a
   `languages/` folder, ready for WordPress).

## How it works

1. **Look at the registry first**: it builds a memory from every `.po` of the
   target language and reuses the **exact matches** as-is (consistency across
   plugins).
2. **Only translate what it doesn't know**: strings missing from the registry are
   translated while preserving placeholders (`%s`, `%1$s`), HTML, plurals and
   whitespace, and without touching brand names (`WP connect`, `Notion`,
   `Airtable`...).
3. **Verify** that no string is left empty.

Every generated `.po` becomes part of the registry for the next translations of
the same language.

## Structure

```
.claude/
├── agents/traductor-plugins.md   Subagent with the methodology
└── commands/traducir.md          /traducir command
scripts/
├── tm_match.py                   Reuses from the registry + lists pending
├── tm_apply.py                   Applies the new translations to the .po
└── tm_pack.py                    Bundles the generated .po files into languages.zip
pot/                              Source files to translate
*.po                              Translation registry (memory)
```

## Requirements

- Python 3 with [`polib`](https://pypi.org/project/polib/): `pip install polib`
