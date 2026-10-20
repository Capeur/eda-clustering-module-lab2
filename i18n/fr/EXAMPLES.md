# Exemples — Métriques d'affinité

Parcours A (implémentation). Fonctions partagées : `../common/graphutil.py`.

## Objectif

Définir **trois** scores d'affinité, les calculer à la main et en code, et montrer que le
choix du score **change la paire qui fusionne en premier**.

L'affinité répond à une seule question pour chaque paire de cellules : *à quel point ces deux-là
veulent-elles être dans le même cluster ?* Tous les algorithmes de clustering de la suite du cours
(fusion gloutonne, réduction multiniveau, clustering d'hypergraphe) partent d'un tel classement :
un mauvais score donne de mauvaises fusions, que le raffinement devra réparer ensuite.

| Score | S'applique à | Idée |
|-------|--------------|------|
| Poids d'arête | graphe | connexion directe uniquement |
| Voisins communs + arête | graphe | connexion directe **plus** le soutien des voisins communs (« connectivité ») |
| Nombre de broches (modèle en clique) | netlist | chaque net répartit son poids entre ses broches, donc les nets larges comptent moins |

## API (cible)

```text
affinity_edge_weight(edges) -> list[(u, v, score)]                # trié
affinity_shared_neighbors(nodes, edges) -> list[(u, v, score)]    # trié
affinity_pin_count(nodes, hyperedges) -> list[(u, v, score)]      # trié
```

**Trié** veut dire : score décroissant, puis `u`, puis `v` par ordre alphabétique. Ce **départage**
fait partie de l'API : A–B et D–E valent toutes les deux 5, et le résultat de référence met A–B en
premier car A < D. Les labs suivants (fusion gloutonne) prennent la première paire : un départage
instable change donc leurs résultats.

## Définitions

**Affinité par poids d'arête**

```text
score(u,v) = w(u,v)
```

**Affinité par voisins communs + arête**

```text
score(u,v) = w(u,v) + somme_x min(w(u,x), w(v,x))
             sur les voisins communs x
```

`w(u,v)` vaut 0 s'il n'y a pas d'arête directe. Une paire sans arête mais avec un voisin commun
obtient quand même un score (B–D ci-dessous). Les paires dont le score vaudrait 0 ne sont **pas**
listées. Le `min` signifie qu'un voisin ne soutient une paire qu'autant que son rayon **le plus faible**.

**Affinité par nombre de broches (modèle en clique)** pour les netlists, où un net peut relier
de nombreuses broches :

```text
score(u,v) = somme, sur les nets e contenant u et v, de  w(e) / (|e| - 1)
```

`|e|` est le nombre de broches du net. Un net à 2 broches donne tout son poids ; un net à 5 broches
ne donne qu'un quart à chaque paire. Les nets larges comme le reset, l'enable ou l'horloge touchent
de nombreuses cellules et ne doivent pas toutes les coller ensemble.

## Pseudo-code

```text
affinity_shared_neighbors(nodes, edges):
  adj = table d'adjacence, adj[u][v] = w(u,v) (dans les deux sens)
  score = {}
  pour (u, v, w) dans edges : score[u,v] += w     # partie directe
  pour chaque paire non ordonnée (u, v) de nœuds :
    s = 0
    pour x dans voisins(u), x != v :
      si x dans voisins(v) :
        s += min(adj[u][x], adj[v][x])
    si s > 0 ou (u,v) dans score : score[u,v] += s
  renvoyer les paires triées par (-score, u, v)
```

```text
affinity_pin_count(nodes, nets):
  score = {}
  pour chaque net e de broches P (|P| >= 2) :
    part = w(e) / (|P| - 1)
    pour chaque paire (u, v) de P : score[u,v] += part
  renvoyer les paires triées par (-score, u, v)
```

## Référence 1 — graphe de départ (`examples/tiny_graph.json`)

Arêtes : A–B 5, A–C 1, B–C 4, C–D 2, D–E 5, C–E 1.

**Poids d'arête** (exactement les six arêtes existantes) :

| Rang | Paire | Score |
|------|-------|-------|
| 1 | A–B | 5 |
| 2 | D–E | 5 |
| 3 | B–C | 4 |
| 4 | C–D | 2 |
| 5 | A–C | 1 |
| 6 | C–E | 1 |

**Voisins communs + arête** (dix paires : les six arêtes, plus quatre paires qui n'ont qu'un voisin en commun) :

| Rang | Paire | Score | Pourquoi |
|------|-------|-------|----------|
| 1 | A–B | 6 | 5 + via C min(1,4)=1 |
| 2 | D–E | 6 | 5 + via C min(2,1)=1 |
| 3 | A–C | 5 | 1 + via B min(5,4)=4 |
| 4 | B–C | 5 | 4 + via A min(5,1)=1 |
| 5 | C–D | 3 | 2 + via E min(1,5)=1 |
| 6 | C–E | 3 | 1 + via D min(2,5)=2 |
| 7 | B–D | 2 | pas d'arête ; via C min(4,2)=2 |
| 8 | A–D | 1 | pas d'arête ; via C min(1,2)=1 |
| 9 | A–E | 1 | pas d'arête ; via C min(1,1)=1 |
| 10 | B–E | 1 | pas d'arête ; via C min(4,1)=1 |

L'arête faible A–C passe du rang 5 au rang 3, car A et C sont tous les deux fortement reliés à B :
le triangle A–B–C forme un groupe dense.

## Référence 2 — l'affinité change la première fusion (`examples/priority_graph.json`)

Un triangle serré P–Q–R (chaque arête pèse 4) et une paire isolée X–Y (poids 5).

| Score | Première fusion | Pourquoi |
|-------|-----------------|----------|
| Poids d'arête | **X–Y @ 5** | l'arête la plus lourde |
| Voisins communs + arête | **P–Q @ 8** | 4 + via R min(4,4)=4 ; X–Y n'a aucun voisin commun et reste à 5 |

Même graphe, même algorithme, première fusion différente. C'est pourquoi le choix de l'affinité
est une décision de conception, pas un détail.

## Référence 3 — les nets larges (`examples/tiny_netlist.json`)

Deux nets à 5 broches (`en`, `rst`) touchent A–E ; un net privé à 2 broches relie E–F. Tous les poids valent 1.

| Score | A–B (et chaque paire de A–E) | E–F | Première fusion |
|-------|------------------------------|-----|-----------------|
| Nombre brut de nets (somme des w) | 2 | 1 | A–B |
| Nombre de broches, w/(\|e\|−1) | 1/4 + 1/4 = **0.5** | **1.0** | **E–F** |

Compter naïvement les nets partagés dit que A–B vont ensemble simplement parce qu'elles voient toutes
les deux l'enable et le reset. Le score par nombre de broches dit que E–F, la seule paire reliée par
une connexion privée, compte davantage. Le clustering d'une netlist devient du clustering d'hypergraphe
(module 03-03) ; ce score fait le lien.

## À essayer

Depuis le dossier de ce module :

```bash
# indiquer à Python où sont les fonctions partagées
export PYTHONPATH=../common

# afficher les deux classements du graphe de départ
python3 ../common/solvers.py examples/tiny_graph.json --mode affinity

# idem pour le graphe de priorité : comparez la première ligne de chaque tableau
python3 ../common/solvers.py examples/priority_graph.json --mode affinity

# vérifier tous les résultats de référence et afficher les classements, nombre de broches compris
python3 examples/affinity_check.py --show

# vérifier VOTRE implémentation (les fonctions pas encore écrites sont ignorées)
python3 examples/affinity_check.py --impl my_affinity.py
```

Tests unitaires des fonctions partagées, depuis `courses/learn_clustering` :

```bash
PYTHONPATH=common python3 -m unittest common.test_solvers.TestFoundations -v
```

## Pour démarrer

1. Calculez **à la main** le score par voisins communs de A–C, B–D et C–E, puis comparez avec la référence 1.
2. Implémentez `affinity_edge_weight` et `affinity_shared_neighbors` ; lancez
   `affinity_check.py --impl` jusqu'à ce que les vérifications sur les graphes passent. (Il fournit les
   arêtes dans l'ordre inverse : un départage oublié échoue.)
3. Expliquez en une phrase pourquoi A–C monte avec le score par voisins communs.
4. Sur le graphe de priorité, expliquez pourquoi la première fusion change d'un score à l'autre.
5. Implémentez `affinity_pin_count`. Expliquez pourquoi A–B tombe à 0.5 alors que E–F reste à 1.
6. Pour aller plus loin : copiez le graphe de départ et passez D–E de 5 à 6. Prédisez d'abord les deux
   classements, puis lancez le solveur sur votre copie. Quelle paire est maintenant en tête, et A–C
   monte-t-elle toujours ?
