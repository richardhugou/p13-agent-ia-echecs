# Notes de présentation — soutenance P13 (deck 19 diapos + démo)

> **Budget** : ~20 min de présentation + 8 min de démo (script détaillé : `docs/08-script-demo.md`) + questions.
> **Rituel avant d'entrer** : pile démarrée la veille (`./demarrer.sh`), scénario déroulé une fois (caches chauds), onglets prêts (app 4200, Swagger 8000/docs, MLflow 5001), notifications coupées, screencast plan B à portée.
> **Le fil rouge à marteler** : *rien de ce que l'agent affirme ne sort du LLM — coups, évaluations et sources viennent de systèmes vérifiables, et chaque chiffre de ce deck sort d'un run rejouable.*

---

## Diapo 1 — Qui nous sommes *(45 s)*
**Message** : poser la fiction et ta posture.
- « IA Engineer junior chez Cavalier Data, missionné à la FFE auprès de la DTN jeunes. Alan, mon responsable technique, est le sponsor. »
- « La commande : un POC en deux semaines, avant les championnats d'Europe jeunes. Deux semaines — ce cadre explique chacun de mes arbitrages. »
**Transition** : « Commençons par le problème qu'on m'a posé. »

## Diapo 2 — Le contexte et le besoin *(1 min)*
**Message** : le goulot d'étranglement est humain, la boucle produit en découle.
- 60 000 licenciés, ~60 % de jeunes, quelques centaines d'entraîneurs — cours à 30–60 €/h.
- Les 4 capacités attendues : coups reconnus par la théorie, explications sourcées, vidéos adaptées, évaluation objective hors théorie.
**Phrase clé** : « Une IA qui accompagne l'élève *pendant qu'il joue* — pas un chatbot à côté de l'échiquier. »
**Transition** : « Chaque capacité pose une question technique — voici les quatre réponses. »

## Diapo 3 — Le parcours d'un coup *(1 min 30)*
**Message** : définir « agent » sans jargon.
- Dérouler les 4 lignes du tableau : FEN → base masters → Stockfish → RAG + LLM.
- **Phrase clé** (à dire lentement) : « Les trois sources à chaque coup, dans cet ordre, parce que chaque étape fabrique l'entrée de la suivante. Ce déroulé conditionnel répété, c'est ça, un agent. »
**Transition** : « Un tiers de ce deck parle de données — c'est voulu : c'est là que se joue la fiabilité. »

## Diapos 4 à 7 — Les données *(4 min pour le bloc)*
**Diapo 4 (sources)** : insister sur deux choses — le **FEN comme clé de jointure** de tout le système, et le **manifeste signé** (« pas de manifeste signé, pas d'extraction » : 161 pages retenues sur 3 251 disponibles, arbitrages tracés). Les trois figures sont issues du notebook d'EDA — chiffres rejouables.
**Diapo 5 (formats)** : passer vite — « cinq formats hétérogènes, donc normalisation obligatoire : FEN pour les positions, SAN pour les coups, JSON en interne ».
**Diapo 6 (traitement)** : le pipeline est **rejouable et idempotent** ; donner le rapport réel : 156 pages → 477 fiches, moyenne 244 tokens — « sous ma cible de 300–500 : mesuré, documenté, assumé ». 1 doublon écarté.
**Diapo 7 (modèle de données)** : « Milvus pour chercher par le sens, MongoDB pour les caches et la traçabilité — et toujours le FEN comme clé. » Ne pas lire les tableaux.
**Transition** : « Les vidéos, dernière source, ont une contrainte juridique intéressante. »

## Diapo 8 — Les vidéos *(45 s)*
- Métadonnées seules via l'API officielle, jamais les fichiers (CGU) ; filtres durée 4–30 min + titre ; cache 7 jours.
- **Semer la partie 2** : « Cette interdiction de télécharger est LA limite structurante de l'étude d'analyse vidéo que je présenterai en partie 2. »

## Diapo 9 — Les briques *(1 min)*
**Message** : la règle d'or.
- « Nous n'entraînons aucun modèle — choix assumé pour deux semaines. Notre valeur ajoutée : l'orchestration et l'évaluation. »
- **Phrase clé** : « Le LLM n'est **jamais** la source de vérité : les coups viennent de Lichess filtrés par python-chess, les évaluations de Stockfish, les sources sont ajoutées par le code. »
- Le routeur théorie/moteur est **déterministe** (seuil de parties) — testable à 100 %, pas un caprice de LLM.

## Diapo 10 — Le choix du LLM *(1 min)*
**Message** : une décision **révisée par la mesure** — assume-le fièrement, c'est une force.
- « Mon plan initial : Haiku via API. J'ai monté un banc de mesure de 4 modèles locaux : qwen3.5:4b tient en 3,2 Go de RAM, répond en 3 à 7 s, en bon français avec mes garde-fous. Le poste payant a disparu. »
- Trois étages : local titulaire, API en option qualité (une variable d'environnement), gabarit déterministe en repli toujours juste.

## Diapo 11 — L'orchestration *(1 min 30)*
- Suivre le graphe du regard avec le jury : valider → identifier → routeur → théorie OU moteur → contexte → vidéos → synthèse.
- « Chaque nœud a un plan B — et je ne le promets pas : je l'ai **observé** en conditions réelles, un jour où Milvus rechargeait ses collections, l'agent a répondu sans fiches avec une note d'incident. »
**Transition** : « Maintenant : comment je prouve que ça marche. »

## Diapo 12 — Le protocole d'évaluation *(1 min 30)*
**Message** : la discipline avant les chiffres.
- Gold set : 25 questions étiquetées à la main, **figé avant tout réglage** — 15 directes, 5 par position, 5 pièges où la bonne réponse est de s'abstenir.
- « Aucun chiffre des diapos suivantes n'a d'autre origine que MLflow ou un notebook exécuté et versionné. »
- Mesure d'adoption exemple : le préfixe d'instruction fait passer la séparation cible/hors-sujet de 0,29 à 0,50.

## Diapo 13 — Mesure de la performance *(2 min)*
**Message** : les objectifs, tous mesurés, tous tenus.
- Dérouler la colonne « Mesuré » : **0/56** coup illégal · recall **1,0** · abstention **5/5 par construction** · sources **100 % par construction** · recherche **7–11 ms** · agent **p95 6,1 s** (LLM local compris) · **0,00 €**.
- Sur recall 1,0 : anticiper l'objection AVANT le jury — « un score parfait doit inquiéter : il révèle que mon étalon v1 mesure le routage, pas la finesse — j'y reviens. »
- Montrer la capture MLflow : « voici le cahier d'expériences. »

## Diapo 14 — Les itérations *(2 min 30 — la diapo la plus importante)*
**Message** : la démarche expérimentale, avec ses surprises.
1. **Run A vs Run B** : « les deux réussissent le routage — la mesure a montré que mon gold set était trop facile. C'est une découverte, pas un échec : la vraie différence est qualitative (ce que reçoit le rédacteur), et le gold set v2 à labels fins est mon axe. »
2. **L'abstention — raconter les trois itérations** (c'est ton meilleur récit de démarche) :
   - « Mesure de bout en bout : une question sur la Scandinave — hors corpus — faisait citer 5 fiches d'autres ouvertures. Trompeur pour un enfant. »
   - « Premier réflexe : un seuil de score. Mais la photo des 25 questions montre le piège à 0,619 et une question légitime à 0,618 — un millième d'écart. Et les vraies questions d'élèves scorent bas : "Pourquoi joue-t-on 3.Fc4 ?" = 0,629. Un seuil assez haut pour tout bloquer aurait privé la démo de ses fiches. »
   - « La parade retenue est **déterministe** : la règle des rayons signés. Le corpus n'est consulté que dans un rayon établi par la position ou nommé dans la question. Hors manifeste → zéro fiche, réponse honnête. Une citation trompeuse devient *impossible par construction*. Le seuil n'est plus qu'un filet à 0,58. Vérifié : 5/5 pièges bloqués, 0 question légitime sacrifiée. »

## Diapo 15 — Déploiement *(1 min)*
- « Une commande. » Test d'installation fraîche **mesuré** : app utilisable en **2 min 09**, bibliothèque à 2 min 28 — protocole rejouable versionné.
- Front en nginx multi-étages : image de 78 Mo (« on ne livre pas la cuisine avec le plat »).

## Diapo 16 — Trajectoire d'industrialisation *(45 s)*
- « L'architecture ne change pas, elle se redimensionne. » Hébergement UE, public mineur (RGPD), comptes = V1 assumée hors POC.

## Diapo 17 — Coûts *(45 s — seule diapo de coûts, ne pas en reparler ailleurs)*
- « Le POC a coûté 0 € en services : données libres, moteur et modèles locaux. Le poste payant prévu a été supprimé par la mesure. »
- Échelle : nul en local ; en cloud ≈ 0,25 centime/réponse → < 0,10 €/élève/mois.

## Diapo 18 — Pistes *(45 s)*
- En choisir DEUX à l'oral : gold set v2 (la suite logique de la leçon de la diapo 14) et l'analyse vidéo → FEN (le pont vers la partie 2). Le reste : « je vous laisse la liste. »

## Diapo 19 — Conclusion → démo *(30 s puis démo)*
- « La promesse : un retour de niveau entraîneur, à la demande. Les objectifs sont mesurés et tenus. Je vous propose de voir Léa jouer. »
- **Enchaîner sur la démo** (`docs/08-script-demo.md`) : 1.e4 → l'Italienne (fiches + vidéos + « Fc5 (fou f8) ») → question libre → 4.g4?! → bascule moteur −1,47. Si le jury est curieux : montrer la question scandinave — l'agent répond « ma bibliothèque est vide pour ce sujet, je ne peux pas t'expliquer » : l'honnêteté en direct.

---

## Les 5 récits à avoir en poche (si une question s'y prête)

1. **« Bc5 illégal »** : une capture m'a fait croire à un coup illégal — l'arbitre (python-chess) a prouvé qu'il était légal (fou f8, pas c8). Le garde-fou marchait ; la *lisibilité* non. D'où « Fc5 (fou f8) » dans l'interface : une alerte utilisateur transformée en amélioration UX.
2. **Le gold set trop facile** : recall 1,0 partout = l'étalon mesure le routage. Savoir *ce que sa mesure mesure* est la compétence — v2 à labels fins en axe.
3. **Les trois itérations de l'abstention** (diapo 14) : préjudice mesuré → seuil impossible (0,618 vs 0,619) → règle déterministe. Chaque étape a sa donnée.
4. **La panne instructive** : Milvus en recharge → l'agent a dégradé proprement en réel. Depuis, le script d'attente « bibliothèque prête ».
5. **Le conteneur gelé** : `docker restart` ne relit pas le `.env` — il faut recréer. Vécu, documenté, neutralisé par `demarrer.sh`.

## Questions à anticiper
→ La liste complète travaillée : `docs/07-questions-examinateur.md`. Les trois plus probables :
- *« Pourquoi ne pas laisser le LLM choisir les coups ? »* — coups illégaux et blunders mesurés dans la littérature ; ici 0/56 par construction, python-chess valide tout.
- *« Votre recall de 1,0 n'est-il pas suspect ? »* — si, et c'est ma diapo 14 : l'étalon était trop facile, je l'ai découvert en mesurant, v2 en axe.
- *« Que se passe-t-il hors des 8 ouvertures ? »* — règle des rayons : l'agent le dit honnêtement et s'appuie sur stats + moteur ; l'élargissement (500 codes ECO) est chiffré en piste.
