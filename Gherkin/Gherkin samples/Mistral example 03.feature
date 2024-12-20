Feature: Recherche de produits
  En tant qu'utilisateur, je veux rechercher des produits afin de pouvoir trouver ce que je cherche rapidement.

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
