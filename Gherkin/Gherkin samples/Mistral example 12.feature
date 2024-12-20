Feature: Utiliser un bon d'achat à la commande
  En tant qu'utilisateur, je veux utiliser un bon d'achat afin de réduire le montant de ma commande.

  Scenario: Utiliser un bon d'achat réussi
    Given l'utilisateur a des articles dans le panier
    And l'utilisateur a un bon d'achat valide
    When l'utilisateur clique sur le bouton "Passer à la caisse"
    And l'utilisateur entre le code du bon d'achat
    And l'utilisateur clique sur le bouton "Appliquer"
    Then le montant du bon d'achat est déduit du total de la commande
    And l'utilisateur clique sur le bouton "Passer la commande"
    Then la commande est confirmée avec le montant réduit
    And un message de confirmation est affiché

  Scenario: Utiliser un bon d'achat échoué avec code invalide
    Given l'utilisateur a des articles dans le panier
    When l'utilisateur clique sur le bouton "Passer à la caisse"
    And l'utilisateur entre un code de bon d'achat invalide
    And l'utilisateur clique sur le bouton "Appliquer"
    Then un message d'erreur "Code de bon d'achat invalide" est affiché
