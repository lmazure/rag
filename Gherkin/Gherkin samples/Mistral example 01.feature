Feature: Connexion utilisateur
  En tant qu'utilisateur, je veux me connecter à l'application afin de pouvoir accéder à mes informations personnelles.

  Scenario: Connexion réussie
    Given l'utilisateur est sur la page de connexion
    When l'utilisateur entre un nom d'utilisateur valide et un mot de passe valide
    And l'utilisateur clique sur le bouton "Se connecter"
    Then l'utilisateur est redirigé vers la page d'accueil
    And un message de bienvenue est affiché

  Scenario: Connexion échouée avec mot de passe incorrect
    Given l'utilisateur est sur la page de connexion
    When l'utilisateur entre un nom d'utilisateur valide et un mot de passe invalide
    And l'utilisateur clique sur le bouton "Se connecter"
    Then un message d'erreur "Mot de passe incorrect" est affiché

  Scenario: Connexion échouée avec nom d'utilisateur incorrect
    Given l'utilisateur est sur la page de connexion
    When l'utilisateur entre un nom d'utilisateur invalide et un mot de passe valide
    And l'utilisateur clique sur le bouton "Se connecter"
    Then un message d'erreur "Nom d'utilisateur incorrect" est affiché
