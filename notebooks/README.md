# Notebooks de démonstration et de mesure

Style : lapidaire — un titre, une ligne par section, le code fait le reste.
Règle de labo : **aucune mesure ne vit uniquement dans une discussion** — toute mesure d'adoption a son notebook exécuté ici et, si la propriété doit durer, son test dans `backend/tests/`.

| Notebook | Démontre | Statut |
|---|---|---|
| `01-inventaire-corpus.ipynb` | comptes exacts des sources (APIs officielles) | ✅ exécuté |
| `02-mesures-embeddings.ipynb` | adoption D-a : dims, vitesse, effet du préfixe d'instruction | ✅ exécuté · garde-fou : `backend/tests/test_embeddings_mesure.py` |
| `03-eda-corpus.ipynb` | figures EDA des diapos data | ✅ exécuté · PNG dans `figures/` |
| `04-evaluation-rag.ipynb` | gold set, Run A vs Run B, métriques MLflow | à venir (É3) |
| `05-demo-agent.ipynb` | le parcours d'un coup, brique par brique | à venir (É6) |
| `06-mesures-llm.ipynb` | reconstruction du banc de mesure de la campagne LLM (journal du 22/08) | à reconstruire |

Exécution : `cd backend && uv run --with jupyter jupyter nbconvert --execute --inplace ../notebooks/<nb>.ipynb`
