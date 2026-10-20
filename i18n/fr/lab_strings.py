"""French strings for the Lab 02 browser lab.

Each entry is (file, English source text, French text). build_site.py copies the lab
into docs/fr/ and replaces every English snippet. If a snippet is no longer found
(the lab changed in eda-learning), the build stops, so a half-translated lab is never
published: update the snippet here and rebuild.

Paths are relative to docs/fr/. Pair names (A–B), numbers and code-like text such as
w(A,B) stay as they are.
"""

LAB = "tools/affinity-metrics/"
UI = "assets/clustering-ui.js"

STRINGS = [
    # ---------------- page (index.html) ----------------
    (LAB + "index.html", '<html lang="en">', '<html lang="fr">'),
    (LAB + "index.html", "<title>Affinity metrics — EDA Algorithms Platform</title>",
     "<title>Métriques d'affinité — EDA Algorithms Platform</title>"),
    (LAB + "index.html", ">Skip to content<", ">Aller au contenu<"),
    (LAB + "index.html", '<div class="eyebrow">Interactive tool</div>', '<div class="eyebrow">Outil interactif</div>'),
    (LAB + "index.html", "<h1>Affinity metrics</h1>", "<h1>Métriques d'affinité</h1>"),
    (LAB + "index.html",
     "Score pairs by hand with three affinity metrics, build the ranking yourself, and change weights to see which pair merges first.",
     "Calculez à la main le score des paires avec trois métriques d'affinité, construisez vous-même le classement, et modifiez les poids pour voir quelle paire fusionne en premier."),

    # ---------------- shared challenge chrome (clustering-ui.js) ----------------
    (UI, 'statusText: "Idle"', 'statusText: "En attente"'),
    (UI, '"Challenge armed — act, then Check"', '"Défi lancé : agissez, puis Vérifier"'),
    (UI, '"Starter loaded (reference)"', '"Exemple de départ chargé (référence)"'),
    (UI, '"Load a challenge with Start"', '"Lancez un défi avec Commencer"'),
    (UI, 'setStatus("pass", "PASS")', 'setStatus("pass", "RÉUSSI")'),
    (UI, '"Not yet — try again or show hint"', '"Pas encore : réessayez ou affichez l\'indice"'),
    (UI, '"Load starter example"', '"Charger l\'exemple de départ"'),
    (UI, "<h2>Challenges</h2>", "<h2>Défis</h2>"),
    (UI, "${challenges.length} cleared</span>", "${challenges.length} réussis</span>"),
    (UI, '<label for="lab-chal-sel">Pick one</label>', '<label for="lab-chal-sel">Choisir</label>'),
    (UI, '"Pick a challenge and click <strong>Start</strong>. The starter example above stays available as a reference — reload it anytime."',
     '"Choisissez un défi et cliquez sur <strong>Commencer</strong>. L\'exemple de départ reste disponible comme référence : rechargez-le quand vous voulez."'),
    (UI, "<strong>Hint:</strong>", "<strong>Indice :</strong>"),
    (UI, '"Restart" : "Start"', '"Recommencer" : "Commencer"'),
    (UI, '"Hide hint" : "Show hint"', '"Masquer l\'indice" : "Afficher l\'indice"'),
    (UI, '"disabled"}>Check</button>', '"disabled"}>Vérifier</button>'),
    (UI, ">Next challenge</button>", ">Défi suivant</button>"),
    (UI, ">Stop checking</button>", ">Arrêter le défi</button>"),
    (UI, 'el("h2", { text: "Graph" })', 'el("h2", { text: "Graphe" })'),
    (UI, 'el("h2", { text: "Reference / metrics" })', 'el("h2", { text: "Travail et mesures" })'),

    # ---------------- model (affinity-lab-model.js) ----------------
    (LAB + "affinity-lab-model.js", 'label: "Starter graph (A–E)"', 'label: "Graphe de départ (A–E)"'),
    (LAB + "affinity-lab-model.js", 'label: "Priority graph (triangle + lone pair)"', 'label: "Graphe de priorité (triangle + paire isolée)"'),
    (LAB + "affinity-lab-model.js", 'label: "Tiny netlist (wide nets)"', 'label: "Petite netlist (nets larges)"'),
    (LAB + "affinity-lab-model.js", 'label: "Edge weight"', 'label: "Poids d\'arête"'),
    (LAB + "affinity-lab-model.js", 'label: "Shared neighbors + edge"', 'label: "Voisins communs + arête"'),
    (LAB + "affinity-lab-model.js", 'label: "Pin-count w/(|e|−1)"', 'label: "Nombre de broches w/(|e|−1)"'),
    (LAB + "affinity-lab-model.js", 'label: "Raw net count"', 'label: "Nombre brut de nets"'),
    (LAB + "affinity-lab-model.js", "`direct: w(", "`direct : w("),
    (LAB + "affinity-lab-model.js", "`via ${x}: min(", "`via ${x} : min("),
    (LAB + "affinity-lab-model.js", "`net ${h.id} (${p} pins): ${fmt(h.w)}", "`net ${h.id} (${p} broches) : ${fmt(h.w)}"),
    (LAB + "affinity-lab-model.js", "`net ${h.id} (${p} pins): +${fmt(h.w)}`", "`net ${h.id} (${p} broches) : +${fmt(h.w)}`"),
    (LAB + "affinity-lab-model.js", "`no net contains both ${a} and ${b}`", "`aucun net ne contient à la fois ${a} et ${b}`"),
    (LAB + "affinity-lab-model.js", '"Type a number such as 5, 0.5 or 1/4."', '"Saisissez un nombre, par exemple 5, 0.5 ou 1/4."'),
    (LAB + "affinity-lab-model.js", "`Correct: ${pairKey(u, v)} = ${value}`", "`Correct : ${pairKey(u, v)} = ${value}`"),
    (LAB + "affinity-lab-model.js",
     "`Not quite: ${pairKey(u, v)} is not ${value}. Recount, or open the breakdown (study).`",
     "`Pas tout à fait : ${pairKey(u, v)} ne vaut pas ${value}. Recomptez, ou ouvrez le détail (révision).`"),
    (LAB + "affinity-lab-model.js", "`${k} is already in your ranking.`", "`${k} est déjà dans votre classement.`"),
    (LAB + "affinity-lab-model.js", "`Added ${k} at position ${n.myRanking.length}.`", "`${k} ajoutée en position ${n.myRanking.length}.`"),
    (LAB + "affinity-lab-model.js", '"Weights are edited on graphs, not the netlist."', '"Les poids se modifient sur les graphes, pas sur la netlist."'),
    (LAB + "affinity-lab-model.js", "`${k} has no edge to lower.`", "`${k} n'a pas d'arête à diminuer.`"),
    (LAB + "affinity-lab-model.js", "`${k} weight is now ${e.w}.`", "`Le poids de ${k} vaut maintenant ${e.w}.`"),

    # ---------------- lab page script (affinity-metrics.js) ----------------
    (LAB + "affinity-metrics.js", "`${net.id} (${net.pins.length} pins)`", "`${net.id} (${net.pins.length} broches)`"),
    (LAB + "affinity-metrics.js", 'level: "Intro"', 'level: "Initiation"'),
    (LAB + "affinity-metrics.js", 'level: "Practice"', 'level: "Pratique"'),
    (LAB + "affinity-metrics.js", 'level: "Stretch"', 'level: "Approfondissement"'),
    # challenge 1
    (LAB + "affinity-metrics.js", '"Top three by edge weight"', '"Le trio de tête par poids d\'arête"'),
    (LAB + "affinity-metrics.js",
     '"Edge weight, starter graph. Build YOUR ranking: click a pair, press “Add to my ranking”, in order. The first three must be right, ties broken alphabetically."',
     '"Poids d\'arête, graphe de départ. Construisez VOTRE classement : cliquez sur une paire, puis sur « Ajouter à mon classement », dans l\'ordre. Les trois premières doivent être justes, égalités départagées par ordre alphabétique."'),
    (LAB + "affinity-metrics.js",
     '"A–B and D–E both weigh 5. Alphabetical order: A before D. Then the next heaviest edge."',
     '"A–B et D–E pèsent toutes les deux 5. Ordre alphabétique : A avant D. Ensuite, l\'arête la plus lourde suivante."'),
    # challenge 2
    (LAB + "affinity-metrics.js", '"Score A–B with shared neighbors"', '"Le score de A–B par voisins communs"'),
    (LAB + "affinity-metrics.js",
     '"Shared neighbors, starter graph. Pick A and B, compute the score by hand, type it in and press “Check my score”."',
     '"Voisins communs, graphe de départ. Choisissez A et B, calculez le score à la main, saisissez-le puis cliquez sur « Vérifier mon score »."'),
    (LAB + "affinity-metrics.js",
     '"Direct weight 5, plus for each common neighbor the SMALLER of its two edges. A and B share C."',
     '"Poids direct 5, plus, pour chaque voisin commun, la PLUS PETITE de ses deux arêtes. A et B ont C en commun."'),
    # challenge 3
    (LAB + "affinity-metrics.js", '"The weak edge climbs"', '"L\'arête faible remonte"'),
    (LAB + "affinity-metrics.js",
     '"A–C is only 1 by edge weight. Compute its shared-neighbor score yourself."',
     '"A–C ne vaut que 1 en poids d\'arête. Calculez vous-même son score par voisins communs."'),
    (LAB + "affinity-metrics.js", '"A and C share B: min(w(A,B), w(C,B))."', '"A et C ont B en commun : min(w(A,B), w(C,B))."'),
    # challenge 4
    (LAB + "affinity-metrics.js", '"A pair with no edge"', '"Une paire sans arête"'),
    (LAB + "affinity-metrics.js",
     '"B and D have no edge. Pick them anyway (dashed line) and compute their shared-neighbor score."',
     '"B et D n\'ont pas d\'arête. Choisissez-les quand même (ligne pointillée) et calculez leur score par voisins communs."'),
    (LAB + "affinity-metrics.js",
     '"Direct part is 0. They share C: min(w(B,C), w(D,C))."',
     '"La partie directe vaut 0. Ils ont C en commun : min(w(B,C), w(D,C))."'),
    # challenge 5
    (LAB + "affinity-metrics.js", '"Find all four invented pairs"', '"Trouver les quatre paires sans arête"'),
    (LAB + "affinity-metrics.js",
     '"Four pairs without an edge get a shared-neighbor score above 0. Find them all and score each one correctly."',
     '"Quatre paires sans arête obtiennent un score par voisins communs supérieur à 0. Trouvez-les toutes et donnez le bon score à chacune."'),
    (LAB + "affinity-metrics.js",
     '"All four go through C. Besides B–D, look at A–D, A–E and B–E."',
     '"Toutes passent par C. En plus de B–D, regardez A–D, A–E et B–E."'),
    # challenge 6
    (LAB + "affinity-metrics.js", '"Shared ranking, top four"', '"Classement par voisins communs, les quatre premières"'),
    (LAB + "affinity-metrics.js",
     '"Shared neighbors, starter graph. Build your ranking: the first four pairs, in order."',
     '"Voisins communs, graphe de départ. Construisez votre classement : les quatre premières paires, dans l\'ordre."'),
    (LAB + "affinity-metrics.js",
     '"Two pairs score 6 and two score 5. Inside each tie, alphabetical order."',
     '"Deux paires valent 6 et deux valent 5. Dans chaque égalité, ordre alphabétique."'),
    # challenge 7
    (LAB + "affinity-metrics.js", '"The first merge flips"', '"La première fusion s\'inverse"'),
    (LAB + "affinity-metrics.js",
     '"Priority graph, shared neighbors. Score P–Q and X–Y yourself. Which one merges first now, and which one did under edge weight?"',
     '"Graphe de priorité, voisins communs. Calculez vous-même P–Q et X–Y. Laquelle fusionne en premier maintenant, et laquelle fusionnait en premier avec le poids d\'arête ?"'),
    (LAB + "affinity-metrics.js",
     '"P–Q: 4 plus via R min(4,4). X–Y has no common neighbor."',
     '"P–Q : 4 plus, via R, min(4,4). X–Y n\'a aucun voisin commun."'),
    # challenge 8
    (LAB + "affinity-metrics.js", '"Make D–E win"', '"Faire gagner D–E"'),
    (LAB + "affinity-metrics.js",
     '"Starter graph, edge weight. Edit weights so D–E ranks FIRST, changing the total weight by exactly 1."',
     '"Graphe de départ, poids d\'arête. Modifiez les poids pour que D–E passe EN PREMIER, en changeant le poids total d\'exactement 1."'),
    (LAB + "affinity-metrics.js",
     '"D–E loses only on the tie-break. Either raise D–E or lower A–B by one."',
     '"D–E ne perd qu\'au départage. Augmentez D–E ou diminuez A–B de un."'),
    # challenge 9
    (LAB + "affinity-metrics.js", '"Out-score the triangle"', '"Battre le triangle"'),
    (LAB + "affinity-metrics.js",
     '"Priority graph. Raise ONLY X–Y until X–Y ranks first under shared neighbors. Use the smallest weight that works."',
     '"Graphe de priorité. Augmentez UNIQUEMENT X–Y jusqu\'à ce que X–Y passe en premier avec les voisins communs. Utilisez le plus petit poids qui fonctionne."'),
    (LAB + "affinity-metrics.js",
     '"The triangle pairs score 8. A tie goes to P–Q (P before X), so 8 is not enough."',
     '"Les paires du triangle valent 8. Une égalité revient à P–Q (P avant X), donc 8 ne suffit pas."'),
    # challenge 10
    (LAB + "affinity-metrics.js", '"Wide nets count less"', '"Les nets larges comptent moins"'),
    (LAB + "affinity-metrics.js",
     '"Tiny netlist, pin-count score. Score A–B and E–F yourself (fractions like 1/4 are fine). Which pair merges first?"',
     '"Petite netlist, score par nombre de broches. Calculez vous-même A–B et E–F (les fractions comme 1/4 sont acceptées). Quelle paire fusionne en premier ?"'),
    (LAB + "affinity-metrics.js",
     '"Each net gives w/(pins − 1) to every pair it connects. A–B shares two 5-pin nets; E–F shares one 2-pin net."',
     '"Chaque net donne w/(broches − 1) à chaque paire qu\'il relie. A–B partage deux nets à 5 broches ; E–F partage un net à 2 broches."'),
    # toolbar
    (LAB + "affinity-metrics.js", 'selectEl("Graph",', 'selectEl("Graphe",'),
    (LAB + "affinity-metrics.js", 'selectEl("Score",', 'selectEl("Score",'),
    (LAB + "affinity-metrics.js", '"Score changed: your ranking was cleared."', '"Score changé : votre classement a été effacé."'),
    # workspace panel
    (LAB + "affinity-metrics.js", "`<strong>Pair ${M.pairKey(...pair)}</strong> · score: ${scoreLabel}`",
     "`<strong>Paire ${M.pairKey(...pair)}</strong> · score : ${scoreLabel}`"),
    (LAB + "affinity-metrics.js", "+ … click a second node`", "+ … cliquez sur un second nœud`"),
    (LAB + "affinity-metrics.js", '"Click two nodes on the canvas to pick a pair."', '"Cliquez sur deux nœuds du graphe pour choisir une paire."'),
    (LAB + "affinity-metrics.js", 'placeholder: "e.g. 5 or 1/4"', 'placeholder: "ex. 5 ou 1/4"'),
    (LAB + "affinity-metrics.js", '"aria-label": "Your score for the selected pair"', '"aria-label": "Votre score pour la paire choisie"'),
    (LAB + "affinity-metrics.js", 'btn("Check my score"', 'btn("Vérifier mon score"'),
    (LAB + "affinity-metrics.js", 'btn("Add to my ranking"', 'btn("Ajouter à mon classement"'),
    (LAB + "affinity-metrics.js", '"Breakdown shown" : "Show breakdown (study)"', '"Détail affiché" : "Afficher le détail (révision)"'),
    (LAB + "affinity-metrics.js", '"Breakdown shown: your answer for this pair no longer counts for challenges."',
     '"Détail affiché : votre réponse pour cette paire ne compte plus pour les défis."'),
    (LAB + "affinity-metrics.js", "`edge weight ${M.weightOf(state, pair[0], pair[1])}:`", "`poids d'arête ${M.weightOf(state, pair[0], pair[1])} :`"),
    (LAB + "affinity-metrics.js", '" Scores changed: answers and ranking cleared."', '" Scores modifiés : réponses et classement effacés."'),
    (LAB + "affinity-metrics.js", '" (breakdown seen)"', '" (détail vu)"'),
    (LAB + "affinity-metrics.js", "`graph: ${state.graphKey} · score: ${scoreLabel}`", "`graphe : ${M.GRAPHS[state.graphKey].label} · score : ${scoreLabel}`"),
    (LAB + "affinity-metrics.js", '"your scores:"', '"vos scores :"'),
    (LAB + "affinity-metrics.js", '"  (none yet)"', '"  (aucun pour l\'instant)"'),
    (LAB + "affinity-metrics.js", '"your ranking:"', '"votre classement :"'),
    (LAB + "affinity-metrics.js", '"  (empty)"', '"  (vide)"'),
    (LAB + "affinity-metrics.js", "`weight edits (total change ${ed.total}):`", "`poids modifiés (changement total ${ed.total}) :`"),
    (LAB + "affinity-metrics.js", '"  (none)"', '"  (aucun)"'),
    (LAB + "affinity-metrics.js", '"nets:"', '"nets :"'),
    (LAB + "affinity-metrics.js", 'btn("Undo last ranking entry"', 'btn("Annuler le dernier ajout"'),
    (LAB + "affinity-metrics.js", '"Hide full ranking" : "Reveal full ranking (study)"', '"Masquer le classement complet" : "Révéler le classement complet (révision)"'),
    (LAB + "affinity-metrics.js", '"Full ranking revealed: ranking challenges for this score no longer pass until you reset."',
     '"Classement complet révélé : les défis de classement pour ce score ne passent plus tant que vous ne réinitialisez pas."'),
    (LAB + "affinity-metrics.js", '["full ranking (study):",', '["classement complet (révision) :",'),
    (LAB + "affinity-metrics.js", 'starterButtonLabel: "Reset workspace"', 'starterButtonLabel: "Réinitialiser"'),
    (LAB + "affinity-metrics.js",
     '"Pick a challenge and click <strong>Start</strong>. Work it out yourself, then <strong>Check</strong>. Study aids are allowed, but what they reveal stops counting."',
     '"Choisissez un défi et cliquez sur <strong>Commencer</strong>. Faites le travail vous-même, puis <strong>Vérifier</strong>. Les aides à la révision sont permises, mais ce qu\'elles révèlent ne compte plus."'),
    (LAB + "affinity-metrics.js",
     """<p><strong>Your workspace:</strong> click two nodes to pick a pair (any pair, even without an edge).
    Compute its score <em>by hand</em> and type it in, add pairs to <em>your</em> ranking in order,
    or change edge weights with − / + to see who merges first.</p>
    <p>Challenges check your typed scores, your ranking and your edits. Using “Show breakdown” or
    “Reveal full ranking” is fine for study, but those answers no longer count.</p>""",
     """<p><strong>Votre espace de travail :</strong> cliquez sur deux nœuds pour choisir une paire (n'importe laquelle, même sans arête).
    Calculez son score <em>à la main</em> et saisissez-le, ajoutez des paires à <em>votre</em> classement dans l'ordre,
    ou modifiez les poids des arêtes avec − / + pour voir qui fusionne en premier.</p>
    <p>Les défis vérifient les scores que vous saisissez, votre classement et vos modifications. « Afficher le détail » et
    « Révéler le classement complet » sont permis pour réviser, mais ces réponses ne comptent plus.</p>"""),
]
