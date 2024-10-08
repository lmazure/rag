Feature: Price Alerts
  As a customer
  I want to set price alerts for products
  So that I can purchase items when they reach my desired price

  Scenario: Set price alert
    Given I am viewing a product priced at "$199.99"
    When I set a price alert for "$150.00"
    Then I should receive a confirmation
    And I should be notified when the price drops to or below $150.00
