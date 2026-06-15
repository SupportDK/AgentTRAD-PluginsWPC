#!/usr/bin/env python3
"""
tm_pack.py — Bundles the generated .po files of a plugin into a zip.

Given a plugin slug and a list of languages, it collects every
"<slug>-<lang>.po" already generated in the project root and compresses them
into "languages.zip", inside a "languages/" folder (the layout WordPress
expects for plugin translations).

Usage:
  python3 scripts/tm_pack.py <slug> <lang1> [<lang2> ...] [--out languages.zip]
"""
import argparse
import os
import sys
import zipfile


def norm_lang(value):
    if not value:
        return ""
    return value.replace("-", "_").split("_")[0].strip().lower()


def main():
    ap = argparse.ArgumentParser(description="Bundle a plugin's .po files into languages.zip")
    ap.add_argument("slug", help="plugin slug (base name without language suffix)")
    ap.add_argument("langs", nargs="+", help="language codes to include")
    ap.add_argument("--out", default="languages.zip", help="output zip path (default: languages.zip)")
    args = ap.parse_args()

    files = []
    missing = []
    for lang in args.langs:
        po = f"{args.slug}-{norm_lang(lang)}.po"
        if os.path.isfile(po):
            files.append(po)
        else:
            missing.append(po)

    if missing:
        for m in missing:
            print(f"WARNING: not found, skipped: {m}", file=sys.stderr)
    if not files:
        sys.exit("ERROR: no .po files to bundle.")

    with zipfile.ZipFile(args.out, "w", zipfile.ZIP_DEFLATED) as zf:
        for po in files:
            # Store inside a languages/ folder
            zf.write(po, arcname=os.path.join("languages", os.path.basename(po)))

    print(f"Created {args.out} with {len(files)} file(s):")
    for po in files:
        print(f"  - languages/{os.path.basename(po)}")


if __name__ == "__main__":
    main()
