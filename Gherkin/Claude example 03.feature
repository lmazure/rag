Feature: Checkout Process
  As a customer
  I want to complete the checkout process
  So that I can receive my ordered items

  Background:
    Given I am logged in as a customer
    And I have items in my cart
    And I am on the checkout page

  Scenario: Successful checkout with saved address and card
    Given I have a saved shipping address
    And I have a saved payment method
    When I select my saved shipping address
    And I select my saved payment method
    And I choose "Standard Shipping"
    And I click "Place Order"
    Then I should see an order confirmation
    And I should receive an order confirmation email
    And my cart should be empty
    And the order should appear in my order history

  Scenario: Checkout with new shipping address
    When I click "Add New Address"
    And I fill in the following address details:
      | Field           | Value           |
      | Street Address | 123 Main St     |
      | City           | Springfield     |
      | State          | IL              |
      | ZIP Code       | 62701           |
      | Phone          | 555-0123        |
    And I fill in valid payment details
    And I choose "Express Shipping"
    And I click "Place Order"
    Then I should see an order confirmation
    And the new address should be saved to my account
    And I should have the option to use this address for future orders
