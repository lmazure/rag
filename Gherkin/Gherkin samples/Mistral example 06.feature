Feature: Modifier ses données personnelles
  En tant qu'utilisateur, je veux modifier mes données personnelles afin de mettre à jour mes informations.

  Scenario: Modifier le genre réussi
    Given l'utilisateur est connecté
    When l'utilisateur va dans la section "Mon compte"
    And l'utilisateur modifie son genre
    And l'utilisateur clique sur le bouton "Enregistrer les modifications"
    Then le genre est mis à jour
    And un message de confirmation est affiché

  Scenario: Modifier le prénom réussi
    Given l'utilisateur est connecté
    When l'utilisateur va dans la section "Mon compte"
    And l'utilisateur modifie son prénom
    And l'utilisateur clique sur le bouton "Enregistrer les modifications"
    Then le prénom est mis à jour
    And un message de confirmation est affiché

  Scenario: Modifier le nom réussi
    Given l'utilisateur est connecté
    When l'utilisateur va dans la section "Mon compte"
    And l'utilisateur modifie son nom
    And l'utilisateur clique sur le bouton "Enregistrer les modifications"
    Then le nom est mis à jour
    And un message de confirmation est affiché

  Scenario: Modifier le téléphone fixe réussi
    Given l'utilisateur est connecté
    When l'utilisateur va dans la section "Mon compte"
    And l'utilisateur modifie son numéro de téléphone fixe
    And l'utilisateur clique sur le bouton "Enregistrer les modifications"
    Then le numéro de téléphone fixe est mis à jour
    And un message de confirmation est affiché

  Scenario: Modifier le téléphone portable réussi
    Given l'utilisateur est connecté
    When l'utilisateur va dans la section "Mon compte"
    And l'utilisateur modifie son numéro de téléphone portable
    And l'utilisateur clique sur le bouton "Enregistrer les modifications"
    Then le numéro de téléphone portable est mis à jour
    And un message de confirmation est affiché

  Scenario: Modifier l'adresse e-mail réussi
    Given l'utilisateur est connecté
    When l'utilisateur va dans la section "Mon compte"
    And l'utilisateur modifie son adresse e-mail
    And l'utilisateur clique sur le bouton "Enregistrer les modifications"
    Then un e-mail de validation est envoyé à la nouvelle adresse e-mail
    And l'utilisateur clique sur le lien de validation dans l'e-mail
    Then l'adresse e-mail est mise à jour
    And un message de confirmation est affiché

  Scenario: Modifier l'adresse réussi
    Given l'utilisateur est connecté
    When l'utilisateur va dans la section "Mon compte"
    And l'utilisateur modifie son adresse
    And l'utilisateur clique sur le bouton "Enregistrer les modifications"
    Then l'adresse est mise à jour
    And un message de confirmation est affiché

  Scenario: Modifier les données personnelles échouée avec les deux numéros de téléphone vides
    Given l'utilisateur est connecté
    When l'utilisateur va dans la section "Mon compte"
    And l'utilisateur laisse les champs de téléphone fixe et portable vides
    And l'utilisateur clique sur le bouton "Enregistrer les modifications"
    Then un message d'erreur "Au moins un numéro de téléphone doit être rempli" est affiché

  Scenario: Modifier les données personnelles échouée avec adresse e-mail invalide
    Given l'utilisateur est connecté
    When l'utilisateur va dans la section "Mon compte"
    And l'utilisateur modifie son adresse e-mail avec une adresse invalide
    And l'utilisateur clique sur le bouton "Enregistrer les modifications"
    Then un message d'erreur "Adresse e-mail invalide" est affiché

  Scenario: Modifier les données personnelles échouée sans validation de l'adresse e-mail
    Given l'utilisateur est connecté
    When l'utilisateur va dans la section "Mon compte"
    And l'utilisateur modifie son adresse e-mail
    And l'utilisateur clique sur le bouton "Enregistrer les modifications"
    Then un e-mail de validation est envoyé à la nouvelle adresse e-mail
    But l'utilisateur ne clique pas sur le lien de validation dans l'e-mail
    Then l'adresse e-mail n'est pas mise à jour
    And un message d'erreur "Veuillez valider votre nouvelle adresse e-mail" est affiché
