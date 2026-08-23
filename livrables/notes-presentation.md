# Notes de présentation — soutenance P13 (deck v2 : 13 diapos + annexes)

> **Budget** : ~15 min de présentation + 8 min de démo (script : `docs/08-script-demo.md`) + questions.
> **Rituel avant d'entrer** : pile démarrée la veille (`./demarrer.sh`), scénario déroulé une fois (caches chauds), onglets prêts (app 4200, Swagger 8000/docs, MLflow 5001), vidéo de démo chargée, notifications coupées.
> **Le fil rouge** (structure voulue par le mentor) : *l'histoire → le fonctionnement → l'architecture → le déploiement → la preuve → les coûts → la partie 2*. Les détails techniques ne se disent pas : ils se montrent en annexe ou se renvoient à `documentation-technique.md`.

---

## Diapo 1 — Titre *(20 s)*
« IA Engineer junior chez Cavalier Data, missionné à la FFE. Je vais vous raconter comment on a construit et mesuré un coach d'ouvertures pour les jeunes espoirs — et ce qu'on propose pour la suite. »

## Diapo 2 — L'histoire et le besoin *(1 min 30)*
**Rester dans l'histoire** : « 60 000 licenciés, 60 % de jeunes, quelques centaines d'entraîneurs — le goulot est humain. Imaginez Léa, 12 ans, qui veut travailler ses ouvertures ce soir : son entraîneur n'est pas là. Alan m'a commandé un POC en deux semaines : une IA qui l'accompagne *pendant qu'elle joue*. » Énumérer les 4 capacités en une phrase chacune.
**Transition** : « Plutôt que de vous le décrire, je vous le montre. »

## Diapo 3 — L'application en action *(2 min — LA VIDÉO D'ABORD)*
**Lancer la vidéo (3-4 coups, ~1 min)** sans parler par-dessus, puis reprendre : « Ce que vous venez de voir : un seul écran, l'échiquier et le panneau coach. Les coups affichés viennent des maîtres — "Fc5, le fou de f8" — avec leurs statistiques réelles ; l'explication cite ses sources ; les vidéos sont adaptées à la position. »

## Diapo 4 — Le parcours de l'élève *(2 min)*
Dérouler le tableau ligne par ligne, toujours du point de vue de Léa : elle dit qui elle est → elle installe sa position (ses coups ET ceux de l'adversaire, corrigeables — une erreur ne pollue jamais l'analyse) → **c'est elle qui appuie** pour lancer l'IA → elle lit des blocs dont chacun vient d'une source vérifiable → elle questionne → elle sort de la théorie et l'agent change d'outil.
**Phrase clé** : « À aucun moment le système n'invente : il va chercher, il assemble, il cite. »
**Transition** : « Comment c'est construit ? Voici l'architecture. »

## Diapo 5 — L'architecture *(2 min 30 — prendre le temps)*
Suivre le schéma du regard avec le jury, brique par brique, **en donnant l'intérêt de chacune** :
- « La position est **validée** (aucune position illégale n'entre) puis l'ouverture est identifiée. »
- « Le **routeur** décide : en théorie → **Lichess**, la vérité statistique de 2 millions de parties ; hors théorie → **Stockfish**, une évaluation objective pour n'importe quelle position. C'est un seuil déterministe, pas un avis de LLM : testable à 100 %. »
- « La **base vectorielle** apporte le "pourquoi" documentaire — diapo suivante, elle le mérite. »
- « **YouTube** : des vidéos — il y a toujours quelque chose à proposer, même général. »
- « Le **LLM local rédige**. Il ne choisit jamais un coup, il met en mots. »
- « **MongoDB cache tout** : rapidité, et résilience — chaque brique a un plan B, on l'a observé en conditions réelles. »

## Diapo 6 — La base vectorielle *(2 min — le mentor nous attend ici)*
**Définir avant de décrire** : « Une base vectorielle, c'est une base qui range les textes par leur *sens*. Pourquoi ? Parce que "pourquoi le fou vise f7" ne partage aucun mot-clé avec la page qui l'explique. »
Puis les deux temps du schéma : **indexer** (477 fiches → chacune devient un vecteur de 1 024 nombres — français et anglais dans le même espace) et **chercher** (la question devient un vecteur, la **similarité cosinus** mesure l'angle entre les deux : 1 = même sujet, 0 = sans rapport ; on prend les 5 plus proches, dans le rayon de l'ouverture jouée uniquement).
Fermer sur les chiffres : 7–11 ms, séparation 0,29 → 0,50, et « question hors bibliothèque → zéro fiche, réponse honnête ».

## Diapo 7 — Le déploiement *(1 min)*
« Une commande. Sept conteneurs plus le modèle local. Et parce qu'une promesse d'installation ne vaut que mesurée : machine nettoyée, chrono — **application utilisable en 2 min 09**, protocole rejouable versionné. »

## Diapo 8 — Performances et fiabilité *(1 min 30)*
Dérouler la colonne « Mesuré » du tableau — chaque ligne est une promesse à Léa tenue. Puis le mot de théorie (le mentor l'a demandé) : « Un LLM prédit le mot suivant : il est fait pour être *plausible*, pas pour être *vrai*. Toute l'architecture découle de cette phrase : les faits viennent d'ailleurs, le LLM met en mots des faits qu'on lui annote. »

## Diapo 9 — La démarche *(1 min 30)*
« Trois moments où la mesure a **changé ma décision** » — raconter court : le LLM (le plan initial est tombé devant les chiffres du local), le gold set (1,0 partout = étalon trop facile : une découverte), l'abstention (un seuil ne sépare pas 0,618 de 0,619 → une règle déterministe : 5/5 pièges, zéro sacrifice). Fermer : « aucun chiffre de ce deck n'existe en dehors d'un notebook ou d'un run versionné. »

## Diapo 10 — Coûts *(45 s — seule diapo de coûts)*
« Le POC a coûté 0 € en services — le poste payant prévu a été supprimé par la mesure. À l'échelle : moins de 10 centimes par élève et par mois si on passait au cloud. Les vrais postes d'industrialisation sont l'hébergement UE et la supervision. »

## Diapo 11 — Partie 2 : l'étude d'analyse vidéo *(2 min — c'est un livrable demandé, ne pas l'écraser)*
« La demande : indexer les vidéos par **position**, pas par titre — "cette position est expliquée à 4 min 32". Trois choses à retenir : le bénéfice est chiffré (×50 à ×100 contre l'indexation humaine) ; **la limite dure est juridique** — les CGU interdisent de stocker les vidéos, donc le MVP se fait sur les licences Creative Commons et les transcripts d'abord ; l'architecture est en **MCP** : quatre serveurs d'outils réutilisables par tout agent futur de la FFE, et un pipeline batch assumé pour la masse. Build MVP 15-20 k€, opex ~100 $/mois, et une roadmap avec des critères d'arrêt chiffrés. L'étude complète est jointe. »

## Diapo 12 — Pistes *(30 s)*
En choisir deux à l'oral : le gold set v2 (la suite de la leçon de mesure) et le MVP analyse vidéo. « Le reste est listé. »

## Diapo 13 — Conclusion → démo *(30 s puis démo en direct)*
« La promesse : un retour de niveau entraîneur, à la demande — et chaque objectif est mesuré et tenu. Je vous propose maintenant de le voir en vrai. » → Démo (`docs/08-script-demo.md`) : choix du camp → Italienne par le sélecteur → question libre → 4.g4?! bascule moteur. Si le jury est curieux : la question scandinave — l'agent répond « ma bibliothèque est vide pour ce sujet, je ne peux pas t'expliquer » : l'honnêteté en direct.

---

## Les annexes (ne les montrer QUE sur question)
- **A — Données** : figures EDA, manifeste signé, ETL chiffré.
- **B — Évaluation** : gold set, runs A/B, capture MLflow.
- **C — Abstention** : l'histoire complète avec la figure des 25 scores.
- **D — LLM** : la campagne mesurée.
- **E — Modèle de données** : Milvus + MongoDB, le FEN pivot.

## Les 5 récits à avoir en poche
1. **« Bc5 illégal »** : une capture m'a fait croire à un coup illégal — l'arbitre a prouvé qu'il était légal (fou f8, pas c8). Le garde-fou marchait ; la *lisibilité* non → « Fc5 (fou f8) » dans l'interface. Une alerte utilisateur devenue amélioration.
2. **Le gold set trop facile** : recall 1,0 partout = l'étalon mesure le routage. Savoir *ce que sa mesure mesure*, c'est la compétence.
3. **Les trois itérations de l'abstention** : préjudice mesuré → seuil impossible (à un millième) → règle déterministe. Chaque étape a sa donnée.
4. **La panne instructive** : Milvus en recharge → l'agent a dégradé proprement en réel.
5. **Le conteneur gelé** : `docker restart` ne relit pas le `.env` — vécu, documenté, neutralisé par `demarrer.sh`.

## Questions à anticiper (liste complète : `docs/07-questions-examinateur.md`)
- *« Pourquoi ne pas laisser le LLM choisir les coups ? »* — il est fait pour être plausible, pas vrai ; ici 0/56 illégal par construction, python-chess valide tout.
- *« Votre recall de 1,0 n'est-il pas suspect ? »* — si, et c'est ma diapo 9 : l'étalon était trop facile, découvert en mesurant, v2 en axe.
- *« Que se passe-t-il hors des 8 ouvertures ? »* — règle des rayons : l'agent le dit honnêtement, garde stats et moteur ; l'élargissement est une piste chiffrée.
- *« Pourquoi MCP pour la partie 2 ? »* — des serveurs d'outils réutilisables par tout agent futur de la FFE, indépendamment du framework — et l'honnêteté d'assumer un pipeline batch pour la masse.
