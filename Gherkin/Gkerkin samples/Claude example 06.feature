Feature: Wishlist Management
  As a customer
  I want to manage my wishlist
  So that I can keep track of products I'm interested in

  Scenario: Add items to wishlist
    Given I am logged in
    When I click the "Add to Wishlist" button on a product
    Then the product should be added to my wishlist
    And I should see a confirmation message
    And the wishlist counter should increment

  Scenario: Share wishlist
    Given I have items in my wishlist
    When I click "Share Wishlist"
    And I enter an email address
    And I add a personal message
    Then a wishlist link should be sent to the specified email
    And I should see a confirmation message
