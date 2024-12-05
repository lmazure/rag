Feature: Shopping Cart Management
  As a customer
  I want to manage items in my shopping cart
  So that I can purchase my desired products

  Background:
    Given I am logged in as a customer
    And my shopping cart is empty

  Scenario: Add single item to cart
    Given I am viewing a product with ID "PROD-001"
    When I select size "M"
    And I select color "Blue"
    And I set quantity to 1
    And I click "Add to Cart"
    Then my cart should contain 1 item
    And the cart total should be updated accordingly
    And I should see a confirmation message "Item added to cart"

  Scenario: Add multiple quantities of an item
    Given I am viewing a product with ID "PROD-001"
    When I select size "L"
    And I select color "Black"
    And I set quantity to 3
    And I click "Add to Cart"
    Then my cart should contain 3 items
    And the cart total should be updated accordingly
    And I should see the correct subtotal for 3 items

  Scenario: Remove item from cart
    Given I have the following items in my cart:
      | Product ID | Name          | Size | Color | Quantity | Price |
      | PROD-001   | Classic Tee   | M    | Blue  | 1        | 29.99 |
      | PROD-002   | Denim Jeans   | 32   | Black | 1        | 59.99 |
    When I remove "Classic Tee" from my cart
    Then my cart should contain 1 item
    And "Classic Tee" should not be in my cart
    And the cart total should be updated to 59.99
