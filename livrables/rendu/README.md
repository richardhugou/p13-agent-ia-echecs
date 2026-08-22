# Sources de rendu des présentations

Les fichiers HTML sont la source ; le PDF se régénère en une commande (Chrome requis) :

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --no-pdf-header-footer --print-to-pdf=sortie.pdf "file://$PWD/presentation-soutenance.html"
```

| Fichier | Contenu | Contenu maître |
|---|---|---|
| `presentation-soutenance.html` | le deck 19 diapos (design « échiquier boisé ») | `livrables/presentation-soutenance.md` |
| `manuel-prive.html` | le manuel pédagogique 45 pages | autonome |
