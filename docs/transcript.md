# Affinity metrics

**Module id:** module01-01-affinity-metrics
**Lab:** affinity-metrics
**Tracks:** A (implement) · B (browser lab)

## Slide 1 — Affinity metrics

Before you merge cells or coarsen a netlist, you need a score that says these two should stay together. That score is affinity. In this module you’ll compare plain edge weight with shared-neighbor scoring on the same tiny graph—and watch who wants to merge first. Then you’ll see a graph where the two scores disagree, and a third score for real netlists, where one net can touch many cells.

<!-- algorithm-walkthrough -->

## Slide 2 — Start with a tiny weighted graph

![Start with a tiny weighted graph](assets/steps/01-raw-graph.png)

Five cells A through E with edge weights. Heavy edges A–B and D–E both weigh five; the bridge through C is weaker. Affinity will decide which pairs want to cluster first.

## Slide 3 — Edge-weight affinity ranks pairs

![Edge-weight affinity ranks pairs](assets/steps/02-edge-rank.png)

Pure edge-weight affinity just sorts existing edges. A–B and D–E tie at five; tie-break puts A–B first. That ranking is the simplest merge priority.

## Slide 4 — Shared neighbors boost A–B

![Shared neighbors boost A–B](assets/steps/03-shared-idea.png)

A and B already share edge weight five. They also share neighbor C. Shared-neighbor affinity adds the minimum of those spokes—one—so A–B rises to six.

## Slide 5 — Shared ranking reshuffles the list

![Shared ranking reshuffles the list](assets/steps/04-shared-rank.png)

Under shared-neighbor scoring, A–B and D–E lead at six. Weak edge A–C jumps to five because of B. Non-edges like B–D can appear from shared support alone.

## Slide 6 — Why affinity matters in EDA

![Why affinity matters in EDA](assets/steps/05-takeaway.png)

Affinity is the objective’s local preference: which cells belong together before global constraints. Bad affinity means bad merges, and harder refinement later.

<!-- /algorithm-walkthrough -->

## Slide 7 — Shared-neighbor scoring as pseudocode

Here is the shared-neighbor score as code. First, every existing edge adds its weight to its pair. Then, for every pair of nodes, look at each neighbor they have in common, and add the smaller of the two connecting weights. If a pair ends up with a score above zero, keep it. Finally, sort by score, highest first, and break ties alphabetically, so your list comes out the same every time.

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

## Slide 8 — Ten pairs, not six

Under shared-neighbor scoring the starter graph produces ten pairs, not six. Four of them have no edge at all. B and D both connect to C, so B–D scores the smaller spoke, two. A–D, A–E and B–E each pick up one through C. These pairs aren't mistakes: they say two cells are close even without a direct wire. A pair is only left out when its score would be zero.

## Slide 9 — Same graph, different first merge

![Edge weight versus shared neighbors on the priority graph](assets/priority-graph.png)

Here's why the choice matters. Take a tight triangle P, Q, R, with every edge at weight four, and a lone pair X–Y at weight five. Edge weight picks X–Y first, because five beats four. Shared-neighbor scoring gives P–Q four plus four through R: eight. X–Y has no common neighbor, so it stays at five. Same graph, same merge engine, different first merge.

## Slide 10 — Nets with many pins

Real netlists aren't simple edges. One net can connect many cells, like a reset or an enable line. If you count every shared net at full weight, cells A and B look close just because both see reset. Pin-count scoring fixes this. Each net splits its weight across its pins: weight divided by pins minus one. A two-pin net counts fully. A five-pin net gives only a quarter to each pair.

```text
tiny netlist: en {A,B,C,D,E}, rst {A,B,C,D,E}, n1 {E,F}

           raw net count     pin-count w/(|e|-1)
A-B        1 + 1 = 2         1/4 + 1/4 = 0.5
E-F        1                 1/1 = 1.0
first      A-B               E-F
```

## Slide 11 — Browser lab track

![Browser lab starter](assets/lab-starter.png)

In the browser lab, you do the scoring. Click two nodes to pick a pair, even a pair with no edge, work out its score by hand, and type it in. You can also build your own ranking, one pair at a time, and change edge weights to see which pair merges first. You can switch between all three graphs and all the scores. The ten challenges check what you typed, your ranking and your edits. The breakdown and the full ranking are there for study, but anything they reveal no longer counts.

## Slide 12 — Implement track

![Real shell session](assets/real-shell.png)

In the implement track, print both rankings for the starter graph, then for the priority graph, and compare the first line of each table. Then write your own scoring functions, including pin-count, and run the golden checker on your file. It checks all three scores, and it feeds the edges in a scrambled order, so a missing tie-break shows up as a failure.

```bash
# point Python at the shared helpers
export PYTHONPATH=../common

# both graph rankings, starter graph then priority graph
python3 ../common/solvers.py examples/tiny_graph.json --mode affinity
python3 ../common/solvers.py examples/priority_graph.json --mode affinity

# check every golden against your own functions
python3 examples/affinity_check.py --impl my_affinity.py
```

## Slide 13 — Pitfalls to watch

Watch for four things. Counting an undirected edge twice, once from each end. Adding the larger spoke instead of the smaller one, which makes everything look close. Forgetting the tie-break, so A–B and D–E swap places from run to run. And using raw net counts on a netlist, where wide nets like reset glue unrelated cells together.

## Slide 14 — Your turn

Match all three golden checks, then explain two things in your own words: why A–C climbs under shared-neighbor scoring, and why the priority graph changes its first merge. Take the short quiz, then continue to greedy pair merge, where these scores become the merge policy.
