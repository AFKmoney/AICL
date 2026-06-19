# Design: AICL Turing-complet — compilateur qui génère du code réel

**Date:** 2026-06-18
**Status:** En attente d'approbation
**Auteur:** Session ZCode (AFKmoney)
**Cible:** Rendre AICL capable de compiler n'importe quel algorithme décrit dans un sous-langage formel, pour produire du code Python/Rust/JS/Go exécutable et correct. Motivation directe : fournir un corpus d'entraînement `(spec.aicl → code correct)` pour CogNetAICL.

---

## 1. Problème

Le compilateur AICL actuel (`compiler.py`, `patterns.py`) génère du code qui :
- contient des corps de méthode `pass` (vides) dès qu'un `Action:` ne matche pas un des ~8 patterns codés en dur ;
- produit de la **syntaxe invalide** (`def f(self, array,: Any = None)` — virgule orpheline) ;
- recrache les recoveries en prose (`return an empty array immediately`) comme du code Python ;
- n'a aucun moyen d'exprimer une boucle, une récursion, ou une expression arithmétique générale.

**Cause racine :** `<action-section> ::= "Action:" <text>`. L'action est du texte libre anglais. Aucun pattern-matcher fini ne peut traduire l'anglais arbitraire en code. C'est un problème de **spécification du langage**, pas un bug.

## 2. Solution : un sous-langage d'expressions Turing-complet dans `Action:`

On introduit un **sous-langage formel** (appelé **AICL-Action** ou **AX**) que l'on peut utiliser dans les sections `Action:` à la place de la prose. AX est délibérément petit, déterministe, et traduisible en tous les backends.

### 2.1 Grammaire AX

```
action        ::= stmt+
stmt          ::= assign | if_stmt | while_stmt | for_stmt | return_stmt | call_stmt | break | continue
assign        ::= lvalue "=" expr
              |  lvalue aug_op expr           (* += -= *= /= //= %= **= *)
if_stmt       ::= "if" expr block ("else" "if" expr block)* ("else" block)?
while_stmt    ::= "while" expr block
for_stmt      ::= "for" name "in" expr block               (* expr = range/list/string *)
return_stmt   ::= "return" expr?
call_stmt     ::= name "(" args? ")"
block         ::= INDENT stmt+ DEDENT
expr          ::= or_expr
or_expr       ::= and_expr ("or" and_expr)*
and_expr      ::= not_expr ("and" not_expr)*
not_expr      ::= "not" not_expr | comparison
comparison    ::= arith (comp_op arith)*
arith         ::= term (("+" | "-") term)*
term          ::= factor (("*" | "/" | "//" | "%") factor)*
factor        ::= power
power         ::= atom ("**" factor)?
atom          ::= literal | name | "(" expr ")" | list_lit | call | index | attr
literal       ::= integer | float | string | "true" | "false" | "none"
list_lit      ::= "[" (expr ("," expr)*)? "]"
index         ::= atom "[" expr "]"
attr          ::= atom "." name
call          ::= name "(" (expr ("," expr)*)? ")"
lvalue        ::= name | index | attr
```

C'est intentionnellement un sous-ensemble strict de Python — donc la traduction Python est triviale (presque identité), et la traduction Rust/JS/Go est mécanique.

### 2.2 Exemple : quicksort en AX

```aicl
Behavior Partition
    Input: array, low, high
    Output: pivot_index
    Action:
        pivot = array[high]
        i = low - 1
        for j in range(low, high):
            if array[j] < pivot:
                i = i + 1
                array[i], array[j] = array[j], array[i]
        array[i + 1], array[high] = array[high], array[i + 1]
        return i + 1
```

Plus de prose. Le compilateur lit ça, le valide, et génère le Python équivalent. Note : `range`, swap `a, b = b, a` et le pattern `for x in range(...)` font partie du sous-ensemble supporté.

### 2.3 Rétrocompatibilité

- La prose anglaise reste **légale** (pour les cas specifiés au niveau architecture, où on ne veut pas d'implémentation). Elle déclenche le fallback existant.
- AX est détecté par la présence de mots-clés structurels (`if`, `while`, `for`, `=`, `return`) suivis d'une syntaxe valide. Le `SubLanguageParser` étendu fait la détection.
- `aicl verify` signale une action en prose comme **warning** ("action uses natural language; compile will produce a skeleton"), pas une erreur.

## 3. Architecture du changement

### 3.1 Nouveau module : `src/aicl/ax/` (AICL-Action)

```
src/aicl/ax/
├── __init__.py
├── lexer.py        tokenize AX
├── parser.py       AX → AX AST
├── ast.py          nodes AX (Assign, If, While, For, BinOp, Call, ...)
├── checker.py      type-check léger + vérif sémantique (variables définies, etc.)
├── emitter_python.py    AX AST → str (code Python, presque identité)
├── emitter_javascript.py
├── emitter_rust.py
└── emitter_go.py
```

### 3.2 Branchement dans le compilateur existant

`BehaviorCompiler.compile_action` (patterns.py:1178) étendu :

```
1. SubLanguageParser (existant, ~8 stmts)          → inchangé
2. NOUVEAU : AX parser essaie de parser l'action   → si succès, émet via emitter
3. Pattern matching (existant, ~30 patterns)       → inchangé (rétrocompat)
4. Fallback structurel (existant)                  → inchangé, mais CORRIGÉ
```

Le point 4 inclut les corrections de bugs (paramètres invalides, recoveries en prose → commentaires + `return None` valide).

### 3.3 Corrections de bugs connexes (Phase A, obligatoires)

| Bug | Fichier | Fix |
|---|---|---|
| CLI crash Python 3.14 (`%` dans help argparse) | `cli.py:780` et autres | échapper les `%` en `%%` dans tous les help strings |
| 4 tests self-healing en échec (`strftime("%f")`) | `runtime.py:72` | remplacer par `datetime.now().strftime(...)` ou `time.strftime` sans `%f` + formatage µs séparé |
| Écriture fichier Windows (`/tmp\` mix) | `compiler.py` `compile_to_file` | normaliser le chemin via `os.path.normpath` avant `os.path.join` |
| Paramètres invalides `array,:` | `compiler.py:_generate_behavior_method` | splitter proprement les inputs (le parser met `array, low_index, high_index` dans UN input) |
| Recoveries en prose `return an empty array immediately` | codegen recovery | ne pas émettre la prose comme instruction ; émettre `return None` + commentaire |

## 4. Tests

Pour chaque algorithme de référence, un test dans `tests/test_ax.py` :

1. **Parse** : la spec `.aicl` parse sans erreur
2. **Compile** : `aicl compile --target python` produit un `main.py`
3. **Syntaxe valide** : `ast.parse(main.py)` réussit (garde anti-régression — c'est ce qui manque aujourd'hui)
4. **Exécution correcte** : on importe le module généré et on appelle le behavior ; on vérifie le résultat (ex : quicksort trie bien un tableau aléatoire)

**Algorithmes de référence pour les tests** (chacun en AX) :
- Bubble sort, insertion sort, selection sort, merge sort, quicksort
- Linear search, binary search
- Factorial (récursif + itératif), Fibonacci (récursif + itératif + mémoïsé)
- Stack, queue (via listes)
- GCD (Euclide)
- String reversal, palindrome check

~15 algorithmes. Chacun prouve une capacité différente du langage (récursion, boucles, conditions, structures).

## 5. Découpage en phases

### Phase A — Fondations (cette session, priorité haute)
- A1. Corriger les 3 bugs triviaux (Python 3.14, strftime, chemins Windows)
- A2. Corriger le bug de syntaxe invalide + recoveries en prose
- A3. Écrire `ax/lexer.py` + `ax/parser.py` + `ax/ast.py`
- A4. Écrire `ax/emitter_python.py`
- A5. Brancher dans `BehaviorCompiler`
- A6. Tests : quicksort + binary search + factorial en AX → Python qui exécute correctement
- **Critère de sortie A :** `py -3.13 -m pytest tests/ -q` passe 156/156 (bugs fixés) + nouveaux tests AX verts

### Phase B — Backends (session suivante)
- B1. `emitter_javascript.py` + tests
- B2. `emitter_rust.py` + tests (attention : ownership, types)
- B3. `emitter_go.py` + tests
- B4. Vérifier que les 4 backends produisent une sortie sémantiquement équivalente (mêmes tests algorithmiques exécutés dans chaque langage)
- **Critère de sortie B :** une spec AX compile vers Python/Rust/JS/Go et tous produisent le même résultat sur les 15 algos

### Phase C — Corpus CogNetAICL (session suivante)
- C1. Générer N specs AX variées (couvrir les patterns algorithmiques)
- C2. Compiler chaque spec → paires `(spec.aicl → code correct)` en JSONL
- C3. Format adapté au fine-tuning CogNet (character-level, séquence ≤192 tokens → chunking)
- C4. Note : CogNet 40M a seq_len=192 ; les specs longues devront être chunkées. Le 1B (ONNX) aura plus de marge.

## 6. Ce qui reste hors de portée même après tout ça

- La traduction de la **prose anglaise arbitraire** en code. AX la remplace, il ne la traduit pas. Si un utilisateur écrit `Action: do the thing`, le fallback s'applique toujours.
- L'inférence de types riche (AX sera typé dynamiquement côté Python, explicitement typé côté Rust/Go — types simples requis).
- L'I/O concret (sockets, fichiers, graphisme) — AX est un langage de **logique pure** ; les layers restent du scaffolding pour l'I/O.
- CogNet fine-tuné sur AICL — le corpus sera prêt, l'entraînement est un chantier séparé.

## 7. Risques

| Risque | Mitigation |
|---|---|
| AX devient un langage trop gros (scope creep) | Maintenir la grammaire volontairement petite ; refuser les features non Turing-essential |
| Les 4 backends divergent sémantiquement | Tests croisés : un algo, 4 sorties, même résultat |
| Le parser AX ambigu avec la prose | Détection stricte par mots-clés + paren-rééquilibrage ; si ambigu → prose (fallback sûr) |
| CogNet 192 tokens trop court pour les specs | Chunking intelligent + le 1B a plus de contexte |

## 8. Définition de "flawless" retenue

Pour cette session (Phase A) : **tous les tests existants passent (156/156), les bugs de syntaxe invalide sont éliminés, et au moins 3 algorithmes (quicksort, binary search, factorial) écrits en AX produisent du Python qui s'exécute correctement.** C'est mesurable, c'est vérité terrain, et c'est la première pierre du compilateur "sorcellerie".
