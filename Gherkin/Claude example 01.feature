Feature: User Authentication
  As a customer
  I want to be able to create an account and sign in
  So that I can access my personal account features

  Background:
    Given the e-commerce website is accessible
    And I am on the home page

  Scenario: Successful user registration
    When I click on "Register"
    And I fill in the following details:
      | Field           | Value                |
      | First Name     | John                 |
      | Last Name      | Doe                  |
      | Email          | john.doe@example.com |
      | Password       | SecurePass123!       |
      | Confirm Password| SecurePass123!       |
    And I accept the terms and conditions
    And I click "Create Account"
    Then I should see a confirmation message
    And I should receive a welcome email
    And I should be logged in automatically

  Scenario Outline: Invalid registration attempts
    When I click on "Register"
    And I fill in the following details:
      | Field           | Value          |
      | First Name     | <firstName>    |
      | Last Name      | <lastName>     |
      | Email          | <email>        |
      | Password       | <password>     |
    And I click "Create Account"
    Then I should see the error message "<errorMessage>"

    Examples:
      | firstName | lastName | email            | password | errorMessage                |
      | ""        | Doe      | john@example.com | Pass123! | First name is required     |
      | John      | ""       | john@example.com | Pass123! | Last name is required      |
      | John      | Doe      | invalid-email    | Pass123! | Invalid email format       |
      | John      | Doe      | john@example.com | weak     | Password is too weak       |
