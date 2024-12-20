Feature: Détruire son compte
  En tant qu'utilisateur, je veux supprimer mon compte afin de ne plus utiliser le service.

  Scenario: Supprimer le compte réussi
    Given l'utilisateur est connecté
    When l'utilisateur va dans la section "Mon compte"
    And l'utilisateur clique sur le bouton "Supprimer mon compte"
    And l'utilisateur confirme la suppression
    Then le compte est supprimé
    And l'utilisateur est déconnecté
    And un message de confirmation de suppression est affiché

  Scenario: Supprimer le compte échouée sans confirmation
    Given l'utilisateur est connecté
    When l'utilisateur va dans la section "Mon compte"
    And l'utilisateur clique sur le bouton "Supprimer mon compte"
    But l'utilisateur annule la suppression
    Then le compte n'est pas supprimé
    And l'utilisateur reste connecté
