# Notebooks de démonstration

Style : lapidaire — un titre, une ligne par section, le code fait le reste.

| Notebook | Démontre | Statut |
|---|---|---|
| `01-inventaire-corpus.ipynb` | comptes exacts des sources (APIs officielles) | ✅ exécuté |
| `02-eda-corpus.ipynb` | figures EDA des diapos data | à venir (É3) |
| `03-evaluation-rag.ipynb` | gold set, Run A vs Run B, métriques MLflow | à venir (É3) |
| `04-demo-agent.ipynb` | le parcours d'un coup, brique par brique | à venir (É2/É6) |

Exécution : `cd backend && uv run --with jupyter jupyter nbconvert --execute --inplace ../notebooks/<nb>.ipynb`
