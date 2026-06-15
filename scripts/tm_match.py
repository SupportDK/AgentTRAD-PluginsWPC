#!/usr/bin/env python3
"""
tm_match.py — Fase determinista del traductor de plugins.

Dado un archivo de origen (.pot o .po con msgstr vacíos) y un idioma destino:
  1. Construye una memoria de traducción (registro) con TODOS los .po del
     mismo idioma que ya existen en el proyecto.
  2. Para cada cadena del origen, si existe una coincidencia EXACTA en el
     registro, copia esa traducción tal cual (reutilización).
  3. Las cadenas que no estén en el registro quedan vacías y se listan en un
     archivo "<salida>.pending.json" para que el agente las traduzca.

Uso:
  python3 scripts/tm_match.py <origen|slug> <idioma> [--out RUTA] [--registry-dir DIR]

Ejemplos:
  python3 scripts/tm_match.py pot/wp-connect-foo.pot fr
  python3 scripts/tm_match.py wp-connect-foo es        # busca el .pot por slug
"""
import argparse
import json
import os
import sys

try:
    import polib
except ImportError:
    sys.exit("ERROR: falta 'polib'. Instálalo con: pip install polib")


def norm_lang(value):
    """Normaliza un código de idioma: 'es_ES' -> 'es', 'pt-BR' -> 'pt'."""
    if not value:
        return ""
    return value.replace("-", "_").split("_")[0].strip().lower()


def key_of(entry):
    """Clave única de una cadena: (contexto, msgid)."""
    return (entry.msgctxt or "", entry.msgid)


def resolve_input(arg):
    """Si 'arg' es un archivo, lo devuelve. Si es un slug, lo busca."""
    if os.path.isfile(arg):
        return arg
    base = arg
    for ext in (".pot", ".po"):
        if base.endswith(ext):
            base = base[: -len(ext)]
    candidates = [
        f"pot/{base}.pot", f"pot/{base}.po",
        f"{base}.pot", f"{base}.po",
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    sys.exit(f"ERROR: no encuentro el origen para '{arg}'. Probé: {candidates}")


def base_slug(path, lang):
    """Deriva el slug base quitando extensión y sufijo de idioma previo."""
    name = os.path.splitext(os.path.basename(path))[0]
    for suffix in (f"-{lang}", f"_{lang}", f"-{norm_lang(lang)}", f"_{norm_lang(lang)}"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    return name


def build_registry(registry_dir, lang, exclude_paths):
    """Lee todos los .po del idioma destino y devuelve {clave: entrada}."""
    target = norm_lang(lang)
    tm = {}
    files_used = []
    exclude = {os.path.abspath(p) for p in exclude_paths}
    for root, _dirs, files in os.walk(registry_dir):
        # Ignorar carpetas internas
        if any(part in root for part in (".claude", "scripts", "__pycache__")):
            continue
        for fn in files:
            if not fn.endswith(".po"):
                continue
            full = os.path.abspath(os.path.join(root, fn))
            if full in exclude:
                continue
            try:
                po = polib.pofile(full)
            except Exception:
                continue
            header_lang = norm_lang(po.metadata.get("Language", ""))
            name_match = norm_lang(fn.rsplit("-", 1)[-1].replace(".po", "")) == target
            if header_lang != target and not name_match:
                continue
            used = False
            for e in po:
                if e.obsolete:
                    continue
                has_tr = bool(e.msgstr) or any(e.msgstr_plural.values())
                if not has_tr:
                    continue
                k = key_of(e)
                # No sobrescribir: el primero que aparezca manda (estable).
                if k not in tm:
                    tm[k] = e
                    used = True
                elif not (tm[k].msgstr or any(tm[k].msgstr_plural.values())):
                    tm[k] = e
            if used:
                files_used.append(os.path.relpath(full, registry_dir))
    return tm, files_used


def main():
    ap = argparse.ArgumentParser(description="Reutiliza traducciones del registro y lista pendientes.")
    ap.add_argument("origen", help="archivo .pot/.po de origen o slug del plugin")
    ap.add_argument("idioma", help="código de idioma destino (es, fr, de, it, pt...)")
    ap.add_argument("--out", help="ruta del .po de salida")
    ap.add_argument("--registry-dir", default=".", help="carpeta raíz del registro (def: .)")
    args = ap.parse_args()

    src_path = resolve_input(args.origen)
    lang = args.idioma.strip()
    slug = base_slug(src_path, lang)
    out_path = args.out or f"{slug}-{norm_lang(lang)}.po"
    pending_path = f"{out_path}.pending.json"

    src = polib.pofile(src_path)
    tm, files_used = build_registry(args.registry_dir, lang, exclude_paths=[src_path, out_path])

    out = polib.POFile()
    out.metadata = dict(src.metadata)
    out.metadata["Language"] = norm_lang(lang)
    out.metadata.setdefault("MIME-Version", "1.0")
    out.metadata.setdefault("Content-Type", "text/plain; charset=UTF-8")
    out.metadata.setdefault("Content-Transfer-Encoding", "8bit")

    reused = 0
    pending = []
    for e in src:
        if e.obsolete:
            continue
        new = polib.POEntry(
            msgid=e.msgid,
            msgid_plural=e.msgid_plural,
            msgctxt=e.msgctxt,
            occurrences=e.occurrences,
            comment=e.comment,
            flags=[f for f in e.flags if f != "fuzzy"],
        )
        hit = tm.get(key_of(e))
        if hit is not None:
            if e.msgid_plural:
                new.msgstr_plural = dict(hit.msgstr_plural) if hit.msgstr_plural else {0: hit.msgstr, 1: hit.msgstr}
            else:
                new.msgstr = hit.msgstr
            reused += 1
        else:
            if e.msgid_plural:
                new.msgstr_plural = {0: "", 1: ""}
            pending.append({
                "msgctxt": e.msgctxt,
                "msgid": e.msgid,
                "msgid_plural": e.msgid_plural or None,
                "references": " ".join(f"{f}:{l}" for f, l in e.occurrences) if e.occurrences else "",
            })
        out.append(new)

    out.save(out_path)
    with open(pending_path, "w", encoding="utf-8") as f:
        json.dump(pending, f, ensure_ascii=False, indent=2)

    total = reused + len(pending)
    print(f"Origen      : {src_path}")
    print(f"Idioma      : {lang}  (normalizado: {norm_lang(lang)})")
    print(f"Registro    : {len(files_used)} archivo(s), {len(tm)} cadenas en memoria")
    print(f"Salida      : {out_path}")
    print(f"Pendientes  : {pending_path}")
    print("-" * 48)
    print(f"Total cadenas : {total}")
    print(f"Reutilizadas  : {reused}")
    print(f"A traducir    : {len(pending)}")
    if total:
        print(f"Cobertura     : {reused * 100 // total}% desde el registro")


if __name__ == "__main__":
    main()
