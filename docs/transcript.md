# Affinity metrics

**Module id:** module01-01-affinity-metrics
**Lab:** affinity-metrics
**Tracks:** A (implement) · B (browser lab)

## Slide 1 — Affinity metrics

Which parts of a chip belong together? That is the question this lab answers. A chip is made of millions of tiny parts called cells. Before a computer can arrange them, it needs to know which cells like to stay close. That liking is a number called affinity. In this lab you'll learn three ways to compute it, and see why the choice matters.

## Slide 2 — From a chip to a graph

![Cells and wires on a chip, then the same thing drawn as a graph](assets/chip-to-graph.png)

A chip contains cells, the small building blocks of the circuit. Cells talk to each other through wires. We draw each cell as a dot, called a node. A line between two dots is an edge: it means the two cells are wired together. The number on an edge is its weight: how many wires join the pair. So A–B has weight five: five wires connect A and B. This drawing is called a graph, and it's the map every algorithm in this course works on.

## Slide 3 — Why group cells?

![Two groups of cells; only the red edges cross between them](assets/clustering-groups.png)

Cells that exchange many signals should sit close together. Short wires make the chip faster and save energy. Grouping close cells is called clustering, and each group is a cluster. Think of a seating plan: friends who chat a lot sit at the same table. Here, A, B and C form one group, and D and E form another. Only the red edges cross between the groups, and we want as few of those as possible.

## Slide 4 — What is affinity?

Affinity is a score for each pair of cells. A high score means these two should be in the same group. A low score means they can be apart. Clustering algorithms merge the pair with the highest score first. So the recipe for the score decides everything that follows. This lab compares three recipes on the same small example.

<!-- algorithm-walkthrough -->

## Slide 5 — Start with a tiny weighted graph

![Start with a tiny weighted graph](assets/steps/01-raw-graph.png)

Here is our example for the whole lab: five cells, A to E. The heavy edges are A–B and D–E, with weight five each. C sits in the middle, with thinner links to the others. Keep this picture in mind: we're going to give a score to every pair of cells in it.

## Slide 6 — Edge-weight affinity ranks pairs

![Edge-weight affinity ranks pairs](assets/steps/02-edge-rank.png)

Recipe one is the simplest. The score of a pair is just the weight of the edge between them. Then we sort the pairs from highest to lowest, like a leaderboard. A–B and D–E are tied at five. When two scores are equal, we break the tie in alphabetical order, so A–B comes first. A fixed tie-break matters: it makes the computer give the same answer every single time.

## Slide 7 — Shared neighbors boost A–B

![Shared neighbors boost A–B](assets/steps/03-shared-idea.png)

Recipe two adds an idea from everyday life: friends of friends. If two people share a close friend, they're probably close too. A and B are directly linked with weight five. They also share a neighbor: C. We add the weaker of the two links through C, which is one, so A–B rises to six. Why the weaker link? Because a chain is only as strong as its weakest link.

## Slide 8 — Shared ranking reshuffles the list

![Shared ranking reshuffles the list](assets/steps/04-shared-rank.png)

With recipe two, A–B and D–E still lead, now at six. But look at A–C: on its own it was a weak edge of one, and now it jumps to five, thanks to B. Even pairs with no edge at all, like B–D, get a score, because they share a neighbor.

## Slide 9 — Why affinity matters in EDA

![Why affinity matters in EDA](assets/steps/05-takeaway.png)

EDA stands for electronic design automation: the software that designs chips. In EDA, affinity is the local preference: which cells belong together, before any rule about the whole chip. Bad affinity means bad merges, and fixing them later is much harder.

<!-- /algorithm-walkthrough -->

## Slide 10 — Worked example: the score of A–C

![The A–C score computed step by step](assets/worked-ac.png)

Let's compute one score together, step by step. Step one: the direct edge A–C has weight one. Step two: A and C have one neighbor in common, B. The links through B weigh five and four, so we keep the smaller one: four. Step three: add them up, one plus four makes five. A–C was weak alone, but becomes strong once its shared friend counts.

## Slide 11 — Ten pairs, not six

With recipe two, our small graph gives ten pairs instead of six. Four of them have no wire at all between them. For example, B and D are not wired together, but both are wired to C. So B–D gets the weaker of those two links: two. It's like two people who have never met but share a best friend. Only pairs whose score would be zero are left out.

## Slide 12 — Recipe two as pseudocode

Here is recipe two written as steps a computer can follow. First, every edge adds its weight to its own pair. Next, for every pair of nodes, look at each neighbor they have in common. For each shared neighbor, add the smaller of its two links to the pair. Keep every pair whose score ends up above zero. Finally, sort from highest to lowest score, and break ties alphabetically.

```text
affinity_shared_neighbors(nodes, edges):
  score[u,v] = w(u,v) for every edge
  for every pair (u, v) of nodes:
    s = 0
    for x in neighbors(u), x != v:
      if x in neighbors(v):
        s += min(w(u,x), w(v,x))
    if s > 0 or (u,v) has an edge:
      score[u,v] += s
  sort by score (high first), then u, then v
```

## Slide 13 — Same graph, different first merge

![Edge weight versus shared neighbors on the priority graph](assets/priority-graph.png)

Here's a second example that shows why the recipe matters. Take a tight triangle P, Q, R, with every edge at weight four. Next to it, a lone pair X–Y has weight five. Recipe one picks X–Y first, because five beats four. Recipe two gives P–Q four, plus four through R: eight, so P–Q goes first. Same graph, same merge rule, but a different first merge.

## Slide 14 — Nets with many pins

![Two wide nets and one private net](assets/wide-nets.png)

On a real chip, one wire can connect many cells at once. Such a shared wire is called a net, and each cell it touches is a pin. Think of a group chat with fifty people: it says little about who is friends. A private message between two people says much more. Recipe three works the same way: each net shares its weight among its pins. The rule is the weight divided by the number of pins, minus one. Here, the enable and reset nets touch five cells each, so they give only a quarter to each pair. The private net between E and F gives its full weight, one.

```text
tiny netlist: en {A,B,C,D,E}, rst {A,B,C,D,E}, n1 {E,F}

           raw net count     pin-count w/(|e|-1)
A-B        1 + 1 = 2         1/4 + 1/4 = 0.5
E-F        1                 1/1 = 1.0
first      A-B               E-F
```

## Slide 15 — Browser lab track

![Browser lab starter](assets/lab-starter.png)

Now it's your turn to compute scores, in the browser lab. Click two nodes to pick a pair, even a pair with no edge, work out its score by hand, and type it in. The lab tells you right away if you're correct. You can also build your own ranking, one pair at a time, and change edge weights to see which pair merges first. The ten challenges go from easy to hard. If you get stuck, the breakdown button shows the calculation, but that answer no longer counts for the challenge.

## Slide 16 — Implement track

![Real shell session](assets/real-shell.png)

If you like programming, the implement track is for you. First, print both rankings with the reference program, for the starter graph and then for the priority graph. Then write your own three scoring functions in Python. Finally, run the checker on your file. It compares your answers with the correct ones, and it feeds the edges in a scrambled order, so a missing tie-break shows up as a failure.

```bash
# point Python at the shared helpers
export PYTHONPATH=../common

# both graph rankings, starter graph then priority graph
python3 ../common/solvers.py examples/tiny_graph.json --mode affinity
python3 ../common/solvers.py examples/priority_graph.json --mode affinity

# check every golden against your own functions
python3 examples/affinity_check.py --impl my_affinity.py
```

## Slide 17 — Pitfalls to watch

Watch out for four common mistakes. Counting an edge twice, once from each end. Adding the stronger link instead of the weaker one, which makes every pair look close. Forgetting the tie-break, so A–B and D–E swap places from one run to the next. And counting big shared nets at full weight, which glues unrelated cells together.

## Slide 18 — Recap: three recipes

Recipe one, edge weight: look only at the direct wire. Recipe two, shared neighbors: add the help of common friends. Recipe three, pin count: big shared nets count less than private ones. Ties are broken alphabetically, so results never change between runs. Different recipes can choose a different first merge. Choosing the recipe is a design decision, not a detail.

## Slide 19 — Your turn

Try the browser lab challenges, or write the three recipes yourself and pass the checker. Then explain two things in your own words. First, why does A–C climb with recipe two? Second, why does the priority graph change its first merge? Take the short quiz, then move on to greedy pair merge. There, these scores become the rule for merging.
