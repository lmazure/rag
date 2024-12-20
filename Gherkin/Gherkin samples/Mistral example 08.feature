Feature: Navigation dans le catalogue de produits
  En tant qu'utilisateur, je veux naviguer dans le catalogue de produits afin de pouvoir trouver et explorer les différentes catégories de produits.

  Scenario: Naviguer vers la catégorie "Vêtements pour homme"
    Given l'utilisateur est sur la page d'accueil
    When l'utilisateur clique sur le menu "Vêtements"
    And l'utilisateur clique sur la sous-catégorie "Homme"
    Then les produits de la catégorie "Vêtements pour homme" sont affichés

  Scenario: Naviguer vers la catégorie "Vêtements pour femme"
    Given l'utilisateur est sur la page d'accueil
    When l'utilisateur clique sur le menu "Vêtements"
    And l'utilisateur clique sur la sous-catégorie "Femme"
    Then les produits de la catégorie "Vêtements pour femme" sont affichés

  Scenario: Naviguer vers la catégorie "Vêtements pour enfant"
    Given l'utilisateur est sur la page d'accueil
    When l'utilisateur clique sur le menu "Vêtements"
    And l'utilisateur clique sur la sous-catégorie "Enfant"
    Then les produits de la catégorie "Vêtements pour enfant" sont affichés

  Scenario: Naviguer vers la catégorie "Livres pour adultes"
    Given l'utilisateur est sur la page d'accueil
    When l'utilisateur clique sur le menu "Livres"
    And l'utilisateur clique sur la sous-catégorie "Adultes"
    Then les produits de la catégorie "Livres pour adultes" sont affichés

  Scenario: Naviguer vers la catégorie "Livres pour adolescents"
    Given l'utilisateur est sur la page d'accueil
    When l'utilisateur clique sur le menu "Livres"
    And l'utilisateur clique sur la sous-catégorie "Adolescents"
    Then les produits de la catégorie "Livres pour adolescents" sont affichés

  Scenario: Naviguer vers la catégorie "Livres pour enfants"
    Given l'utilisateur est sur la page d'accueil
    When l'utilisateur clique sur le menu "Livres"
    And l'utilisateur clique sur la sous-catégorie "Enfants"
    Then les produits de la catégorie "Livres pour enfants" sont affichés

  Scenario: Naviguer vers la catégorie "Jouets"
    Given l'utilisateur est sur la page d'accueil
    When l'utilisateur clique sur le menu "Jouets"
    Then les produits de la catégorie "Jouets" sont affichés

  Scenario: Naviguer vers la catégorie "DVD de films"
    Given l'utilisateur est sur la page d'accueil
    When l'utilisateur clique sur le menu "DVD de films"
    Then les produits de la catégorie "DVD de films" sont affichés

  Scenario: Naviguer vers la catégorie "CD audio"
    Given l'utilisateur est sur la page d'accueil
    When l'utilisateur clique sur le menu "CD audio"
    Then les produits de la catégorie "CD audio" sont affichés
