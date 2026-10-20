# Métriques d'affinité

**Module id:** module01-01-affinity-metrics
**Lab:** affinity-metrics
**Tracks:** A (implémentation) · B (lab dans le navigateur)

## Slide 1 — Métriques d'affinité

Avant de fusionner des cellules ou de réduire une netlist, il faut savoir lesquelles vont ensemble. Ce score, c'est l'affinité. Vous allez comparer le poids d'arête et le score par voisins communs. Les deux sont testés sur le même petit graphe, pour voir qui fusionne en premier. Ensuite, vous verrez un graphe où ces deux scores ne sont pas d'accord. Enfin, un troisième score traite les vraies netlists, où un seul net touche de nombreuses cellules.

## Slide 2 — Un petit graphe pondéré

![Un petit graphe pondéré](assets/steps/01-raw-graph.png)

Cinq cellules, de A à E, reliées par des arêtes pondérées. Les arêtes lourdes A–B et D–E pèsent toutes les deux cinq ; le pont qui passe par C est plus faible. C'est l'affinité qui va décider quelles paires veulent former un cluster en premier.

## Slide 3 — L'affinité par poids d'arête classe les paires

![L'affinité par poids d'arête classe les paires](assets/steps/02-edge-rank.png)

L'affinité par poids d'arête se contente de trier les arêtes existantes. A–B et D–E sont à égalité à cinq ; le départage place A–B en premier. Ce classement est la priorité de fusion la plus simple.

## Slide 4 — Les voisins communs renforcent A–B

![Les voisins communs renforcent A–B](assets/steps/03-shared-idea.png)

A et B partagent déjà une arête de poids cinq. Ils ont aussi un voisin commun : C. L'affinité par voisins communs ajoute le plus petit des deux rayons, c'est-à-dire un, donc A–B monte à six.

## Slide 5 — Le classement par voisins communs rebat les cartes

![Le classement par voisins communs rebat les cartes](assets/steps/04-shared-rank.png)

Avec le score par voisins communs, A–B et D–E mènent à six. L'arête faible A–C bondit à cinq grâce à B. Des paires sans arête, comme B–D, peuvent apparaître uniquement grâce à leurs voisins communs.

## Slide 6 — Pourquoi l'affinité compte en EDA

![Pourquoi l'affinité compte en EDA](assets/steps/05-takeaway.png)

L'affinité, c'est la préférence locale de l'objectif : quelles cellules vont ensemble, avant les contraintes globales. Une mauvaise affinité donne de mauvaises fusions, et un raffinement plus difficile ensuite.

<!-- /algorithm-walkthrough -->

## Slide 7 — Le score par voisins communs en pseudo-code

Voici le score par voisins communs sous forme de code. D'abord, chaque arête existante ajoute son poids à sa paire. Ensuite, on prend chaque paire de nœuds et chacun de leurs voisins communs. Pour chaque voisin commun, on ajoute le plus petit des deux poids vers la paire. Une paire dont le score dépasse zéro est gardée. Enfin, on trie par score décroissant, et on départage les égalités par ordre alphabétique. Ainsi, la liste est toujours la même.

```text
affinity_shared_neighbors(nodes, edges):
  score[u,v] = w(u,v) pour chaque arête
  pour chaque paire (u, v) de nœuds :
    s = 0
    pour x dans voisins(u), x != v :
      si x dans voisins(v) :
        s += min(w(u,x), w(v,x))
    si s > 0 ou (u,v) a une arête :
      score[u,v] += s
  trier par score (décroissant), puis u, puis v
```

## Slide 8 — Dix paires, pas six

Avec le score par voisins communs, le graphe de départ donne dix paires, et non six. Quatre d'entre elles n'ont aucune arête. B et D sont tous les deux reliés à C, donc B–D obtient le plus petit rayon : deux. A–D, A–E et B–E gagnent chacune un, en passant par C. Ces paires ne sont pas des erreurs. Elles disent que deux cellules sont proches, même sans fil direct. Une paire n'est exclue que si son score vaut zéro.

## Slide 9 — Même graphe, première fusion différente

![Poids d'arête et voisins communs sur le graphe de priorité](assets/priority-graph.png)

Prenons un triangle serré P, Q, R, dont chaque arête pèse quatre. Ajoutons une paire isolée X–Y, de poids cinq. Le poids d'arête choisit d'abord X–Y, car cinq bat quatre. Le score par voisins communs donne à P–Q quatre, plus quatre via R : huit. X–Y n'a aucun voisin commun, donc reste à cinq. Même graphe, même moteur de fusion, mais une première fusion différente.

## Slide 10 — Des nets à nombreuses broches

Les vraies netlists ne sont pas faites de simples arêtes. Un seul net peut relier de nombreuses cellules, comme une ligne de reset ou d'enable. Compter chaque net partagé à plein poids rapproche A et B à tort. Elles semblent proches simplement parce qu'elles voient toutes les deux le reset. Le score par nombre de broches corrige cela. Chaque net divise son poids par son nombre de broches moins un. Un net à deux broches compte donc entièrement. Un net à cinq broches ne donne qu'un quart à chaque paire.

```text
petite netlist : en {A,B,C,D,E}, rst {A,B,C,D,E}, n1 {E,F}

           nombre brut de nets    nombre de broches w/(|e|-1)
A-B        1 + 1 = 2              1/4 + 1/4 = 0.5
E-F        1                      1/1 = 1.0
1re fusion A-B                    E-F
```

## Slide 11 — Le parcours lab dans le navigateur

![Le lab dans le navigateur](assets/lab-starter.png)

Dans le lab du navigateur, c'est vous qui calculez les scores. Cliquez sur deux nœuds pour choisir une paire, même une paire sans arête, calculez son score à la main, puis saisissez-le. Vous pouvez aussi construire votre propre classement, une paire à la fois, et modifier les poids des arêtes pour voir quelle paire fusionne en premier. Vous pouvez passer d'un graphe à l'autre et d'un score à l'autre. Les dix défis vérifient ce que vous avez saisi, votre classement et vos modifications. Le détail du calcul et le classement complet sont là pour réviser, mais tout ce qu'ils révèlent ne compte plus.

## Slide 12 — Le parcours implémentation

![Session dans un vrai terminal](assets/real-shell.png)

Dans le parcours implémentation, affichez les deux classements pour le graphe de départ, puis pour le graphe de priorité, et comparez la première ligne de chaque tableau. Ensuite, écrivez vos propres fonctions de score, y compris le nombre de broches, et lancez le vérificateur sur votre fichier. Il contrôle les trois scores, et il fournit les arêtes dans le désordre : un départage oublié apparaît donc comme un échec.

```bash
# indiquer à Python où sont les fonctions partagées
export PYTHONPATH=../common

# les deux classements : graphe de départ, puis graphe de priorité
python3 ../common/solvers.py examples/tiny_graph.json --mode affinity
python3 ../common/solvers.py examples/priority_graph.json --mode affinity

# vérifier tous les résultats de référence sur vos propres fonctions
python3 examples/affinity_check.py --impl my_affinity.py
```

## Slide 13 — Les pièges à éviter

Attention à quatre choses. Compter deux fois une arête non orientée, une fois depuis chaque extrémité. Ajouter le plus grand rayon au lieu du plus petit, ce qui rend tout proche de tout. Oublier le départage : A–B et D–E changent alors de place d'une exécution à l'autre. Et compter les nets bruts sur une netlist. Des nets très larges comme le reset collent alors des cellules sans rapport.

## Slide 14 — À vous de jouer

Faites passer les trois vérifications de référence. Puis expliquez pourquoi A–C monte avec le score par voisins communs. Expliquez aussi pourquoi le graphe de priorité change sa première fusion. Faites le petit quiz. Passez ensuite à la fusion gloutonne par paires, où ces scores deviennent la règle.