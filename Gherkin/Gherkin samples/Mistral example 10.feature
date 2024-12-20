Feature: Effectuer une commande
  En tant qu'utilisateur, je veux passer une commande afin de pouvoir acheter des produits.

  Scenario: Passer une commande réussie
    Given l'utilisateur a des articles dans le panier
    When l'utilisateur clique sur le bouton "Passer à la caisse"
    And l'utilisateur entre les informations de livraison et de paiement valides
    And l'utilisateur clique sur le bouton "Passer la commande"
    Then la commande est confirmée
    And un message de confirmation est affiché
    And le panier est vidé

  Scenario: Passer une commande échouée avec informations de paiement invalides
    Given l'utilisateur a des articles dans le panier
    When l'utilisateur clique sur le bouton "Passer à la caisse"
    And l'utilisateur entre des informations de livraison valides et des informations de paiement invalides
    And l'utilisateur clique sur le bouton "Passer la commande"
    Then un message d'erreur "Informations de paiement invalides" est affiché
