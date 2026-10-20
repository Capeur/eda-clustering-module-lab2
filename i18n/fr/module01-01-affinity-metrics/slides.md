---
marp: true
title: Métriques d'affinité
paginate: true
---

# Métriques d'affinité

Avant de fusionner des cellules ou de réduire une netlist, il faut savoir lesquelles vont ensemble

---

## Un petit graphe pondéré
![Un petit graphe pondéré](assets/steps/01-raw-graph.png)

---

## L'affinité par poids d'arête classe les paires
![L'affinité par poids d'arête classe les paires](assets/steps/02-edge-rank.png)

---

## Les voisins communs renforcent A–B
![Les voisins communs renforcent A–B](assets/steps/03-shared-idea.png)

---

## Le classement par voisins communs rebat les cartes
![Le classement par voisins communs rebat les cartes](assets/steps/04-shared-rank.png)

---

## Pourquoi l'affinité compte en EDA
![Pourquoi l'affinité compte en EDA](assets/steps/05-takeaway.png)

---

## Le score par voisins communs en pseudo-code
- Voici le score par voisins communs sous forme de code
- D'abord, chaque arête existante ajoute son poids à sa paire
- Ensuite, on prend chaque paire de nœuds et chacun de leurs voisins communs
- Pour chaque voisin commun, on ajoute le plus petit des deux poids vers la paire
- Une paire dont le score dépasse zéro est gardée
- Enfin, on trie par score décroissant, et on départage les égalités par ordre alphabétique

---

## Le score par voisins communs en pseudo-code — try these

```
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

---

## Dix paires, pas six
- Avec le score par voisins communs, le graphe de départ donne dix paires, et non six
- Quatre d'entre elles n'ont aucune arête
- B et D sont tous les deux reliés à C, donc B–D obtient le plus petit rayon : deux
- A–D, A–E et B–E gagnent chacune un, en passant par C
- Ces paires ne sont pas des erreurs
- Elles disent que deux cellules sont proches, même sans fil direct

---

## Même graphe, première fusion différente
- Prenons un triangle serré P, Q, R, dont chaque arête pèse quatre
- Ajoutons une paire isolée X–Y, de poids cinq
- Le poids d'arête choisit d'abord X–Y, car cinq bat quatre
- Le score par voisins communs donne à P–Q quatre, plus quatre via R : huit
- X–Y n'a aucun voisin commun, donc reste à cinq
- Même graphe, même moteur de fusion, mais une première fusion différente
![snippet](assets/priority-graph.png)

---

## Des nets à nombreuses broches
- Les vraies netlists ne sont pas faites de simples arêtes
- Un seul net peut relier de nombreuses cellules, comme une ligne de reset ou d'enable
- Compter chaque net partagé à plein poids rapproche A et B à tort
- Elles semblent proches simplement parce qu'elles voient toutes les deux le reset
- Le score par nombre de broches corrige cela
- Chaque net divise son poids par son nombre de broches moins un

---

## Des nets à nombreuses broches — try these

```
petite netlist : en {A,B,C,D,E}, rst {A,B,C,D,E}, n1 {E,F}

           nombre brut de nets    nombre de broches w/(|e|-1)
A-B        1 + 1 = 2              1/4 + 1/4 = 0.5
E-F        1                      1/1 = 1.0
1re fusion A-B                    E-F
```

---

## Le parcours lab dans le navigateur
![Le lab dans le navigateur](assets/lab-starter.png)

---

## Le parcours implémentation
![Session dans un vrai terminal](assets/real-shell.png)

---

## Le parcours implémentation — try these

```
# indiquer à Python où sont les fonctions partagées
export PYTHONPATH=../common

# les deux classements : graphe de départ, puis graphe de priorité
python3 ../common/solvers.py examples/tiny_graph.json --mode affinity
python3 ../common/solvers.py examples/priority_graph.json --mode affinity

# vérifier tous les résultats de référence sur vos propres fonctions
python3 examples/affinity_check.py --impl my_affinity.py
```

---

## Les pièges à éviter
- Attention à quatre choses
- Compter deux fois une arête non orientée, une fois depuis chaque extrémité
- Ajouter le plus grand rayon au lieu du plus petit, ce qui rend tout proche de tout
- Oublier le départage : A–B et D–E changent alors de place d'une exécution à l'autre
- Et compter les nets bruts sur une netlist
- Des nets très larges comme le reset collent alors des cellules sans rapport

---

## À vous de jouer
- Faites passer les trois vérifications de référence
- Puis expliquez pourquoi A–C monte avec le score par voisins communs
- Expliquez aussi pourquoi le graphe de priorité change sa première fusion
- Faites le petit quiz
- Passez ensuite à la fusion gloutonne par paires, où ces scores deviennent la règle

