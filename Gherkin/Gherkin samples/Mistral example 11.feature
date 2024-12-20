Feature: Offrir un bon d'achat à un ami
  En tant qu'utilisateur, je veux offrir un bon d'achat à un ami afin de lui faire un cadeau.

  Scenario: Offrir un bon d'achat réussi
    Given l'utilisateur est connecté
    When l'utilisateur va dans la section "Bons d'achat"
    And l'utilisateur sélectionne le montant du bon d'achat
    And l'utilisateur entre l'adresse e-mail de l'ami
    And l'utilisateur clique sur le bouton "Offrir"
    Then le bon d'achat est envoyé à l'adresse e-mail de l'ami
    And un message de confirmation est affiché

  Scenario: Offrir un bon d'achat échoué avec adresse e-mail invalide
    Given l'utilisateur est connecté
    When l'utilisateur va dans la section "Bons d'achat"
    And l'utilisateur sélectionne le montant du bon d'achat
    And l'utilisateur entre une adresse e-mail invalide
    And l'utilisateur clique sur le bouton "Offrir"
    Then un message d'erreur "Adresse e-mail invalide" est affiché
