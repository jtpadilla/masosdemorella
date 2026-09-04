# Capa HD (opcional, ara buida)

Reprodueix els noms de fitxer d'`assets/images/` amb una versió de **més
resolució** de la mateixa fotografia, quan aparega al fons familiar.

```
assets/images/13-era-del-mas-de-julian.jpg      ← la que es publica (2896×2172)
assets/images-hd/13-era-del-mas-de-julian.jpg   ← la mateixa, més gran (si la tenim)
```

**Regles**

- Mateix nom de fitxer, exactament. És l'única cosa que les relaciona.
- Només si **supera en píxels** la d'`assets/images/`. Si no, no s'afig.
- No es toca `source/` (originals intocables) ni `extract/` (regenerable).

**Qui la usa**

`site/src/pages/il-lustracions.astro`: l'enllaç «Obri la imatge a resolució
original» apunta a la versió HD quan existeix; la miniatura de 640 px continua
eixint d'`assets/images/`, que ja hi basta.

**Qui NO la usa**

`site/scripts/llibre.mjs` (EPUB i PDF) llig només `assets/images/`. Si algun dia
es vol el llibre amb les HD, cal canviar-ho ahí a posta.

**Estat**: buida. Comprovat el 2026-09-04 contra l'arxiu familiar
(`franciscapublicaciones/multimedia/`): les 26 fotografies que hi coincideixen ja
tenen ací la **mateixa resolució** i **menys compressió**. No hi ha res a millorar.
