Feature: Recherche dans le catalogue de produits
  En tant qu'utilisateur, je veux rechercher des produits afin de pouvoir trouver rapidement ce que je cherche.

  Scenario: Recherche avec un terme valide
    Given l'utilisateur est sur la page d'accueil
    When l'utilisateur entre un terme de recherche valide dans la barre de recherche
    And l'utilisateur clique sur le bouton "Rechercher"
    Then les résultats de recherche correspondants sont affichés

  Scenario: Recherche avec un terme invalide
    Given l'utilisateur est sur la page d'accueil
    When l'utilisateur entre un terme de recherche invalide dans la barre de recherche
    And l'utilisateur clique sur le bouton "Rechercher"
    Then un message "Aucun résultat trouvé" est affiché

  Scenario: Recherche avec une barre de recherche vide
    Given l'utilisateur est sur la page d'accueil
    When l'utilisateur clique sur le bouton "Rechercher" sans entrer de terme de recherche
    Then un message "Veuillez entrer un terme de recherche" est affiché

  Scenario: Recherche dans la catégorie "Vêtements pour homme"
    Given l'utilisateur est sur la page d'accueil
    When l'utilisateur entre "chemise homme" dans la barre de recherche
    And l'utilisateur clique sur le bouton "Rechercher"
    Then les résultats de recherche pour "chemise homme" dans la catégorie "Vêtements pour homme" sont affichés

  Scenario: Recherche dans la catégorie "Livres pour adolescents"
    Given l'utilisateur est sur la page d'accueil
    When l'utilisateur entre "roman adolescent" dans la barre de recherche
    And l'utilisateur clique sur le bouton "Rechercher"
    Then les résultats de recherche pour "roman adolescent" dans la catégorie "Livres pour adolescents" sont affichés

  Scenario: Recherche dans la catégorie "Jouets"
    Given l'utilisateur est sur la page d'accueil
    When l'utilisateur entre "poupée" dans la barre de recherche
    And l'utilisateur clique sur le bouton "Rechercher"
    Then les résultats de recherche pour "poupée" dans la catégorie "Jouets" sont affichés

  Scenario: Recherche dans la catégorie "DVD de films"
    Given l'utilisateur est sur la page d'accueil
    When l'utilisateur entre "film d'action" dans la barre de recherche
    And l'utilisateur clique sur le bouton "Rechercher"
    Then les résultats de recherche pour "film d'action" dans la catégorie "DVD de films" sont affichés

  Scenario: Recherche dans la catégorie "CD audio"
    Given l'utilisateur est sur la page d'accueil
    When l'utilisateur entre "album rock" dans la barre de recherche
    And l'utilisateur clique sur le bouton "Rechercher"
    Then les résultats de recherche pour "album rock" dans la catégorie "CD audio" sont affichés
