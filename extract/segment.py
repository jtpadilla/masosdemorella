#!/usr/bin/env python3
"""Imprime el Markdown reconstruido correspondiente a una o varias páginas impresas del original:
   python3 extract/segment.py 23 24
Sirve para cotejar contra extract/render/p-0NN.png (página física = impresa + 5)."""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
docs = []
for f in sorted((ROOT / "content").glob("*.md")):
    t = re.sub(r"^---.*?---\n", "", f.read_text(encoding="utf-8"), flags=re.S)
    docs.append((f.name, t))
full = "\n".join(t for _, t in docs)
anchor = re.compile(r'<a id="p(\d+)" class="pag" data-p="\d+"></a>')
pos = {int(m.group(1)): m.start() for m in anchor.finditer(full)}
for n in map(int, sys.argv[1:]):
    start = pos[n]
    nxt = min((p for k, p in pos.items() if k > n), default=len(full))
    seg = anchor.sub("¶", full[start:nxt]).strip()
    print(f"═══════ p{n} (física {n+5}) ═══════")
    print(seg)
    print()
