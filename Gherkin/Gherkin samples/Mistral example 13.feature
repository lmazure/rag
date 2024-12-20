Feature: Bénéficier de -20% du Black Friday
  En tant qu'utilisateur, je veux bénéficier de la réduction de -20% du Black Friday afin de faire des économies sur mes achats.

  Scenario: Bénéficier de la réduction Black Friday réussie
    Given l'utilisateur a des articles dans le panier
    And la promotion Black Friday est active
    When l'utilisateur clique sur le bouton "Passer à la caisse"
    Then la réduction de -20% est automatiquement appliquée au total de la commande
    And l'utilisateur clique sur le bouton "Passer la commande"
    Then la commande est confirmée avec le montant réduit
    And un message de confirmation est affiché

  Scenario: Bénéficier de la réduction Black Friday échouée si la promotion n'est pas active
    Given l'utilisateur a des articles dans le panier
    And la promotion Black Friday n'est pas active
    When l'utilisateur clique sur le bouton "Passer à la caisse"
    Then la réduction de -20% n'est pas appliquée au total de la commande
    And l'utilisateur clique sur le bouton "Passer la commande"
    Then la commande est confirmée sans réduction
    And un message de confirmation est affiché
