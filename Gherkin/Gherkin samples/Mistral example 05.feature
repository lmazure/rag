Feature: Annulation de commande
  En tant qu'utilisateur, je veux annuler une commande afin de ne pas recevoir les produits commandés.

  Scenario: Annuler une commande réussie
    Given l'utilisateur a une commande en cours
    When l'utilisateur va dans la section "Mes commandes"
    And l'utilisateur clique sur le bouton "Annuler la commande" à côté de la commande
    Then la commande est annulée
    And un message de confirmation d'annulation est affiché

  Scenario: Annuler une commande échouée si la commande est déjà expédiée
    Given l'utilisateur a une commande déjà expédiée
    When l'utilisateur va dans la section "Mes commandes"
    And l'utilisateur clique sur le bouton "Annuler la commande" à côté de la commande
    Then un message d'erreur "Impossible d'annuler une commande déjà expédiée" est affiché
