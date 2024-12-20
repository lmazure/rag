Feature: Gestion du panier d'achat
  En tant qu'utilisateur, je veux ajouter des articles à mon panier afin de pouvoir les acheter.

  Scenario: Ajouter un article au panier
    Given l'utilisateur est sur la page de détails du produit
    When l'utilisateur clique sur le bouton "Ajouter au panier"
    Then l'article est ajouté au panier
    And le nombre d'articles dans le panier est mis à jour

  Scenario: Retirer un article du panier
    Given l'utilisateur a un article dans le panier
    When l'utilisateur clique sur le bouton "Retirer" à côté de l'article
    Then l'article est retiré du panier
    And le nombre d'articles dans le panier est mis à jour

  Scenario: Vider le panier
    Given l'utilisateur a plusieurs articles dans le panier
    When l'utilisateur clique sur le bouton "Vider le panier"
    Then tous les articles sont retirés du panier
    And le nombre d'articles dans le panier est mis à jour à zéro
