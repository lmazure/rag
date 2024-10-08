Feature: Order Management
  As a customer
  I want to manage my orders
  So that I can track and modify my purchases

  Scenario: Track order status
    Given I have placed an order with ID "ORD-12345"
    When I view my order details
    Then I should see the current status of my order
    And I should see the estimated delivery date
    And I should see the shipping carrier and tracking number

  Scenario: Cancel order
    Given I have placed an order within the last 24 hours
    When I select "Cancel Order"
    And I provide a reason for cancellation
    Then the order should be cancelled
    And I should receive a cancellation confirmation email
    And any payment should be refunded
