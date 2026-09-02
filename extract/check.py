#!/usr/bin/env python3
"""Comprueba que content/*.md contiene exactamente las mismas palabras que el texto del PDF (págs. 6-105),
descontando cabecera corrida y números de página. Compara multiconjuntos de palabras (las notas al pie
cambian de sitio). Imprime las palabras cuyo recuento difiere."""
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HEADER = "Masies de Morella. Vida i costums en la Dena dels Llivis"
WORD = re.compile(r"[0-9A-Za-zÀ-ÿ·]+")


def words(s):
    return Counter(w.lower() for w in WORD.findall(s))


pdf = Counter()
for i in range(6, 106):
    t = (ROOT / f"extract/text/p{i:03d}.raw.txt").read_text(encoding="utf-8")
    t = t.replace(HEADER, "")
    t = re.sub(r"^\s*-\s*\d+\s*-\s*$", "", t, flags=re.M)
    t = re.sub(r"(?<=[A-Za-zÀ-ÿ”’])\d{1,2}\b", "", t)            # llamada de nota pegada a la palabra
    pdf += words(t)

md = Counter()
for f in sorted((ROOT / "content").glob("*.md")):
    t = f.read_text(encoding="utf-8")
    t = re.sub(r"^---.*?---", "", t, flags=re.S)                 # frontmatter
    t = re.sub(r"<[^>]+>", "", t)                                # html (anclas, figuras perdidas)
    t = re.sub(r"\]\([^)]*\)", "]", t)                           # rutas de imagen
    t = re.sub(r"\[\^\d+\]:?", "", t)                            # notas
    t = re.sub(r"^#+ \d+\.\d+ ", "", t, flags=re.M)              # números de apartado reasignados
    t = t.replace("Il·lustració perduda en l’original", "")
    t = t.replace("²", "2")
    md += words(t)

diff = {w: (pdf[w], md[w]) for w in set(pdf) | set(md) if pdf[w] != md[w] and not (w.isdigit() and len(w) == 1)}
print(f"palabras PDF={sum(pdf.values())}  MD={sum(md.values())}  distintas={len(diff)}")
for w, (a, b) in sorted(diff.items(), key=lambda x: -abs(x[1][0] - x[1][1]))[:40]:
    print(f"  {w!r:30} pdf={a} md={b}")


# --- 2) orden de las palabras --------------------------------------------------------------------------
# Compara la secuencia de palabras del cuerpo (sin notas al pie) del PDF con la del Markdown.
import difflib

raw_seq, md_seq = [], []
for i in range(6, 106):
    t = (ROOT / f"extract/text/p{i:03d}.raw.txt").read_text(encoding="utf-8")
    t = t.replace(HEADER, "")
    t = re.sub(r"^\s*-\s*\d+\s*-\s*$", "", t, flags=re.M)
    t = re.sub(r"(?<=[A-Za-zÀ-ÿ”’])\d{1,2}\b", "", t)
    raw_seq += [w.lower() for w in WORD.findall(t)]
notes = []
for f in sorted((ROOT / "content").glob("*.md")):
    t = f.read_text(encoding="utf-8")
    t = re.sub(r"^---.*?---", "", t, flags=re.S)
    notes += re.findall(r"^\[\^\d+\]: (.*)$", t, flags=re.M)
    t = re.sub(r"^\[\^\d+\]: .*$", "", t, flags=re.M)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"\]\([^)]*\)", "]", t)
    t = re.sub(r"\[\^\d+\]", "", t)
    t = re.sub(r"^#+ \d+\.\d+ ", "", t, flags=re.M)
    t = t.replace("Il·lustració perduda en l’original", "").replace("²", "2")
    md_seq += [w.lower() for w in WORD.findall(t)]
note_words = Counter(w.lower() for n in notes for w in WORD.findall(re.sub(r"[*_\\]", "", n)))

sm = difflib.SequenceMatcher(a=raw_seq, b=md_seq, autojunk=False)
problems = 0
for op, i1, i2, j1, j2 in sm.get_opcodes():
    if op == "equal":
        continue
    a, b = raw_seq[i1:i2], md_seq[j1:j2]
    core = [w for w in a if not (w.isdigit() and len(w) <= 2)]
    if op == "delete" and all(note_words[w] > 0 for w in core):
        continue                      # nota al pie (cambia de sitio) o número de nota: esperado
    if not b and not core:
        continue
    if "".join(a).replace("2", "") == "".join(b).replace("2", ""):
        continue                      # guion de clítico (posar-lo) o exponente (m²)
    problems += 1
    if problems <= 25:
        print(f"  {op:8} pdf[{i1}]: {' '.join(a)[:70]!r}  |  md: {' '.join(b)[:70]!r}")
print(f"desajustes de orden: {problems}")
