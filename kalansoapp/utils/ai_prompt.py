remember = """


    Génère 3 questions à choix multiples pour tester la mémoire factuelle du cours.

    Propose 2 définitions clés extraites du texte et demande à l'étudiant de les compléter.

    Pose une question de type "Vrai ou Faux" à partir d’un fait important du document.

    Écris une question qui commence par : "Quelle est la définition de..." à partir du cours.

    Donne 3 mots-clés du document et demande à l’étudiant leur signification.

    Génère une flashcard contenant un concept du cours avec sa définition.
"""


understand = """

    Objectif : S'assurer que l'étudiant comprend le contenu (résumer, reformuler, expliquer).



    Génère une question qui demande à l’étudiant de résumer une section du cours.

    Crée une question du type "Expliquez avec vos propres mots..." à partir d’un concept important.

    Propose une analogie simple pour expliquer un concept vu dans le cours.

    Donne une affirmation issue du cours et demande "Pourquoi est-ce vrai ?"

    Propose une question du type "Quel est le but principal de cette section ?"

    Formule une question "Quelle est la différence entre X et Y ?", selon les contenus.
"""


apply  = """
    Objectif : Appliquer les connaissances à de nouvelles situations.


    Crée un exercice où l’étudiant doit utiliser un concept du cours pour résoudre un petit problème.

    Formule une situation concrète et demande à l’étudiant quelle règle/concept appliquer.

    Pose une question de type "Comment utiliseriez-vous ce concept pour..."

    Propose un exemple incomplet et demande à l’étudiant de le compléter correctement.

    Crée une mise en situation et demande une réponse ou une action basée sur le cours.

    Génère un mini-cas pratique à résoudre à l’aide d’un outil ou principe du cours.

"""


analyse = """Objectif : Identifier les relations, hiérarchies, ou composantes dans un contenu.


    Propose une question du type "Quelles sont les parties principales de...".

    Demande à l’étudiant de comparer deux sections du cours et d’identifier leurs points communs et différences.

    Formule une question qui invite à classer ou organiser les concepts selon leur importance.

    Pose une question de type "Quelle est la cause de ce phénomène décrit dans le texte ?"

    Demande à l’étudiant de repérer des arguments ou hypothèses dans un extrait du cours.

    Génère un schéma que l’étudiant doit remplir à partir de l’analyse du contenu."""

evaluate = """ Objectif : Porter un jugement, critiquer, justifier une opinion à partir d’un critère.

    Crée une question du type "Pensez-vous que cette approche est la meilleure ? Pourquoi ?"

    Pose une question demandant de justifier le choix d’une méthode par rapport à une autre.

    Propose deux interprétations d’un même concept et demande à l’étudiant de choisir et d’argumenter.

    Génère un énoncé incomplet et demande à l’étudiant de l’évaluer et le corriger si besoin.

    Crée une question qui pousse à critiquer une théorie, une méthode ou une pratique du cours.

    Formule une grille critériée à remplir pour évaluer une solution ou un exemple.

"""

create = """
Objectif : Produire quelque chose de nouveau à partir de ce qui a été appris.


    Demande à l’IA de proposer une consigne de projet final basé sur le cours.

    Crée une question du type "Imaginez une solution originale à..."

    Propose une activité où l’étudiant doit écrire un article court ou une synthèse innovante sur un thème du cours.

    Demande une invention ou une idée nouvelle inspirée des concepts étudiés.

    Pose une question du type "Comment amélioreriez-vous cette théorie ou méthode ?"

    Demande de créer une infographie ou une carte mentale résumant le cours de façon créative."""


prompts = [remember, understand, apply, analyse, evaluate, create ]