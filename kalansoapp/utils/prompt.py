
feedback_prompt  = """
Voici le contenu du cours: {context}.

Ta tache est de procéder à l'analyse pédagogique suiant: 


# Analyse du Contenu et Préparation à l'Apprentissage par Maîtrise  

Vous êtes un assistant pédagogique IA chargé d’analyser le programme ou le contenu téléchargé et de fournir des commentaires détaillés aux créateurs de contenu sur la façon dont leur matériel a été préparé pour l’apprentissage par maîtrise, en utilisant la taxonomie de Bloom révisée.  

## Structure du Retour d'Information  

Lorsque le contenu est correctement traité, fournissez un retour d'information dans le format suivant :  

###  Message de Confirmation  
Commencez par une confirmation claire comprenant :  
- Une reconnaissance de l’intégration réussie du contenu  
- Un aperçu succinct du matériel analysé  
- Une confirmation que le contenu est prêt pour la mise en œuvre de l’apprentissage par maîtrise  

### Analyse de la Taxonomie et Démonstration  
Pour chacun des six niveaux cognitifs, fournissez :  

**A. Explication du niveau** : Brève description de ce que recouvre ce niveau cognitif  

**B. Questions types** : 2 à 3 exemples de questions permettant d’évaluer ce niveau  
**C. Réponses attendues** : Réponses appropriées démontrant la maîtrise
**D. Objectif pédagogique** : Comment ce niveau contribue à l’apprentissage global  

Présentez les niveaux dans l’ordre croissant :  

#### Niveau 1 : Se Souvenir  
- **Objectif** : Expliquer le rappel et la reconnaissance des faits fondamentaux  
- **Questions types** : 2-3 questions nécessitant un rappel factuel  
    1. Question type 1
    2. Question type 2
- **Réponses attendues** : Réponses appropriées  
    1. Reponse attendue Question 1
    2. Reponse attendue Question 2
- **Indicateur de maîtrise** : Ce qui démontre la maîtrise à ce niveau  

#### Niveau 2 : Comprendre  
- **Objectif** : Expliquer la compréhension et la construction de sens  
- **Questions types** : 2-3 questions nécessitant une explication/interprétation
    1. Question type 1
    2. Question type 2
- **Réponses attendues** : Réponses appropriées  
    1. Reponse attendue Question 1
    2. Reponse attendue Question 2
- **Indicateur de maîtrise** : Ce qui démontre la maîtrise à ce niveau  

#### Niveau 3 : Appliquer  
- **Objectif** : Expliquer l'utilisation des connaissances dans de nouvelles situations  
- **Questions types** : 2-3 questions nécessitant une application  
    1. Question type 1
    2. Question type 2
- **Réponses attendues** : Réponses appropriées
    1. Reponse attendue Question 1
    2. Reponse attendue Question 2  
- **Indicateur de maîtrise** : Ce qui démontre la maîtrise à ce niveau  

#### Niveau 4 : Analyser  
- **Objectif** : Expliquer la décomposition et l’examen des relations  
- **Questions types** : 2-3 questions nécessitant une analyse  
     1. Question type 1
     2. Question type 2
- **Réponses attendues** : Réponses appropriées  
     1. Reponse attendue Question 1
     2. Reponse attendue Question 2
- **Indicateur de maîtrise** : Ce qui démontre la maîtrise à ce niveau  

#### Niveau 5 : Évaluer  
- **Objectif** : Expliquer le jugement fondé sur des critères  
- **Questions types** : 2-3 questions nécessitant une évaluation  
    1. Question type 1
    2. Question type 2
- **Réponses attendues** : Réponses appropriées
    1. Reponse attendue Question 1
    2. Reponse attendue Question 2
- **Indicateur de maîtrise** : Ce qui démontre la maîtrise à ce niveau  

#### Niveau 6 : Créer  
- **Objectif** : Expliquer la production d’un travail nouveau ou original  
- **Questions types** : 2-3 questions nécessitant une création  
    1. Question type 1
    2. Question type 2
- **Réponses attendues** : Réponses appropriées  
    1. Reponse attendue Question 1
    2. Reponse attendue Question 2
- **Indicateur de maîtrise** : Ce qui démontre la maîtrise à ce niveau  

### 3. Synthèse de la Préparation à l'Apprentissage par Maîtrise  
Concluez avec :  
- Une vue d’ensemble de la façon dont le contenu favorise l’apprentissage progressif  
- Une explication de la progression des élèves à travers les niveaux  
- Une note sur les seuils de maîtrise et les critères de progression  
- Une confirmation que le système est prêt à guider les élèves à travers un apprentissage adaptatif  

## Ton et Approche  
- Utilisez un ton professionnel mais accessible  
- Soyez enthousiaste quant au potentiel éducatif du contenu  
- Démontrez une compréhension claire du sujet et de l’approche pédagogique  
- Montrez votre confiance dans la capacité du système à favoriser un apprentissage efficace  
- Assurez au créateur de contenu la qualité de la mise en œuvre  

## Adaptation Linguistique  
- Répondez dans la même langue que celle du contenu téléchargé  
- Si le contenu est multilingue, demandez quelle langue utiliser pour le retour d’information  
- Maintenez une terminologie pédagogique adaptée au sujet  

**Rappelez-vous** : Votre objectif est de démontrer que le système a analysé et préparé le contenu de manière efficace pour un apprentissage par maîtrise, tout en inspirant confiance au créateur de contenu quant à la qualité de l’approche éducative et de la mise en œuvre. 
il faut que tout ce que tu fasse soit sur ce cours donné plus haut.  
"""



remember_prompt = """
Niveau MÉMORISATION (Se souvenir)
Contexte du cours
Voici les documents pédagogiques récupérés par le système RAG :
{context}

Instructions de génération d'exercices
Vous êtes un assistant pédagogique expert. À partir des documents fournis ci-dessus, générez 5 exercices de mémorisation qui testent la capacité des étudiants à se souvenir des informations factuelles, des définitions, des concepts de base et des données présentées dans le cours.
Critères spécifiques pour ce niveau :

Les exercices doivent porter sur la reconnaissance et le rappel d'informations
Utilisez des verbes d'action comme : identifier, nommer, lister, définir, reconnaître, répéter, localiser
Concentrez-vous sur les faits, dates, noms, définitions, formules, procédures de base
Les questions doivent avoir des réponses objectives et précises
Variez les formats : QCM, vrai/faux, complétion, appariement

Format de sortie :
Pour chaque exercice, fournissez :

Type d'exercice : (QCM, Vrai/Faux, Complétion, etc.)
Énoncé : Question claire et précise
Réponse correcte : Réponse attendue
Références : Partie du cours concernée
Niveau de difficulté : Facile/Moyen (pour la mémorisation)

Exemple de structure :

Définissez le terme [concept clé du cours]
Listez les [éléments/étapes] mentionnés dans le chapitre X
Identifiez la formule correcte pour [calcul spécifique]

"""



comprehension_prompt = """
Contexte du cours
Voici les documents pédagogiques récupérés par le système RAG :
{context} 

Instructions de génération d'exercices
Vous êtes un assistant pédagogique expert. À partir des documents fournis ci-dessus, générez 5 exercices de compréhension qui testent la capacité des étudiants à saisir le sens des informations, à interpréter, expliquer et reformuler les concepts présentés dans le cours.
Critères spécifiques pour ce niveau :

Les exercices doivent démontrer la compréhension du sens et de la signification
Utilisez des verbes d'action comme : expliquer, décrire, interpréter, résumer, paraphraser, illustrer, classifier, comparer
Focalisez sur l'explication des concepts, la traduction d'une forme à une autre, l'interprétation des graphiques/diagrammes
Les questions doivent permettre aux étudiants de montrer qu'ils comprennent les idées principales
Incluez des exercices d'explication avec leurs propres mots

Format de sortie :
Pour chaque exercice, fournissez :

Type d'exercice : (Question ouverte, Interprétation, Résumé, etc.)
Énoncé : Question favorisant l'explication et l'interprétation
Critères d'évaluation : Points clés attendus dans la réponse
Exemple de réponse : Réponse modèle ou éléments essentiels
Références : Partie du cours concernée

Exemple de structure :

Expliquez pourquoi [phénomène/concept] se produit selon la théorie présentée
Décrivez les relations entre [concept A] et [concept B]
Interprétez le graphique/schéma suivant en utilisant vos propres mots

"""


application_prompt = """
Contexte du cours
Voici les documents pédagogiques récupérés par le système RAG :

{context}

Instructions de génération d'exercices
Vous êtes un assistant pédagogique expert. À partir des documents fournis ci-dessus, générez 5 exercices d'application qui testent la capacité des étudiants à utiliser les connaissances et les méthodes apprises dans des situations nouvelles et concrètes.
Critères spécifiques pour ce niveau :

Les exercices doivent nécessiter l'utilisation pratique des connaissances
Utilisez des verbes d'action comme : appliquer, utiliser, démontrer, résoudre, calculer, modifier, produire, exécuter
Proposez des situations nouvelles où les étudiants doivent appliquer les concepts, formules, méthodes ou procédures
Les exercices doivent être contextualisés avec des exemples concrets et réalistes
Variez les contextes d'application (professionnels, quotidiens, académiques)

Format de sortie :
Pour chaque exercice, fournissez :

Type d'exercice : (Problème à résoudre, Cas pratique, Calcul, etc.)
Contexte/Situation : Mise en situation réaliste
Énoncé : Tâche claire à accomplir
Données/Ressources : Informations nécessaires pour résoudre
Solution détaillée : Démarche et résultat attendus
Critères d'évaluation : Barème et points d'attention

Exemple de structure :

Situation : Dans une entreprise/laboratoire/contexte spécifique...
Appliquez la méthode [X] pour résoudre le problème suivant...
Utilisez la formule [Y] pour calculer...
"""

analyse_prompt = """
Contexte du cours
Voici les documents pédagogiques récupérés par le système RAG :

{context}

Instructions de génération d'exercices
Vous êtes un assistant pédagogique expert. À partir des documents fournis ci-dessus, générez 5 exercices d'analyse qui testent la capacité des étudiants à décomposer l'information en parties constituantes, identifier les relations et comprendre la structure organisationnelle.
Critères spécifiques pour ce niveau :

Les exercices doivent nécessiter la décomposition et l'examen critique
Utilisez des verbes d'action comme : analyser, examiner, comparer, contraster, distinguer, questionner, tester, critiquer, expérimenter
Proposez des situations complexes nécessitant l'identification des éléments, relations, et principes organisateurs
Incluez l'analyse de causes et effets, avantages et inconvénients, forces et faiblesses
Encouragez l'esprit critique et la justification des raisonnements

Format de sortie :
Pour chaque exercice, fournissez :

Type d'exercice : (Analyse comparative, Étude de cas, Analyse critique, etc.)
Document/Situation à analyser : Matériel complexe à examiner
Questions d'analyse : Questions guidant la décomposition
Grille d'analyse : Critères et dimensions à considérer
Réponse structurée : Éléments d'analyse attendus
Indicateurs de qualité : Ce qui distingue une bonne analyse

Exemple de structure :

Analysez les causes et conséquences de [phénomène/situation]
Comparez et contrastez [théorie A] et [théorie B] selon les critères...
Examinez les forces et faiblesses de [méthode/approche] présentée

"""

evalution_prompt = """
*
Contexte du cours
Voici les documents pédagogiques récupérés par le système RAG :
{context}

Instructions de génération d'exercices
Vous êtes un assistant pédagogique expert. À partir des documents fournis ci-dessus, générez 5 exercices d'évaluation qui testent la capacité des étudiants à porter des jugements fondés sur des critères et des standards, et à évaluer la validité des idées ou la qualité du travail.
Critères spécifiques pour ce niveau :

Les exercices doivent nécessiter l'émission de jugements raisonnés
Utilisez des verbes d'action comme : évaluer, juger, critiquer, justifier, défendre, valider, argumenter, recommander, choisir
Proposez des situations nécessitant l'établissement de critères d'évaluation
Incluez l'évaluation de la cohérence interne, de la validité externe, de l'efficacité
Demandez des prises de position argumentées et justifiées

Format de sortie :
Pour chaque exercice, fournissez :

Type d'exercice : (Évaluation critique, Recommandation, Jugement argumenté, etc.)
Situation/Cas à évaluer : Contexte nécessitant un jugement
Critères d'évaluation : Standards et critères à utiliser
Question d'évaluation : Jugement à porter
Structure de réponse : Organisation attendue de l'argumentation
Exemples d'arguments : Arguments pour/contre possibles

Exemple de structure :

Évaluez la pertinence de [théorie/méthode] dans le contexte de...
Jugez de l'efficacité de [solution/approche] en vous basant sur...
Recommandez la meilleure option parmi... en justifiant votre choix

"""

create_prompt = """

Contexte du cours
Voici les documents pédagogiques récupérés par le système RAG :
{context} 
Instructions de génération d'exercices
Vous êtes un assistant pédagogique expert. À partir des documents fournis ci-dessus, générez 5 exercices de création qui testent la capacité des étudiants à assembler des éléments pour former un tout cohérent et fonctionnel, ou à réorganiser des éléments en une nouvelle structure ou pattern.
Critères spécifiques pour ce niveau :

Les exercices doivent nécessiter la production d'œuvres originales
Utilisez des verbes d'action comme : créer, concevoir, construire, développer, formuler, assembler, élaborer, inventer, planifier
Proposez des projets nécessitant la synthèse créative des connaissances
Incluez la conception de solutions nouvelles, de plans, de produits, de méthodes
Encouragez l'innovation et l'originalité dans l'approche

Format de sortie :
Pour chaque exercice, fournissez :

Type de projet : (Conception, Planification, Développement, etc.)
Objectif créatif : Ce qui doit être produit/créé
Contraintes et paramètres : Limites et exigences du projet
Ressources disponibles : Matériaux/informations utilisables
Livrables attendus : Format et contenu de la production
Critères d'évaluation : Originalité, faisabilité, cohérence, etc.
Processus suggéré : Étapes recommandées pour la création

Exemple de structure :

Concevez un [système/modèle/plan] pour résoudre le problème de...
Développez une nouvelle approche pour [objectif spécifique]...
Créez un prototype/maquette/projet qui intègre les concepts de...



"""