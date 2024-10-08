Feature: Gift Cards
  As a customer
  I want to purchase and redeem gift cards
  So that I can give gifts or use store credit

  Scenario: Purchase digital gift card
    When I select "Buy Gift Card"
    And I enter the following details:
      | Field           | Value                |
      | Amount         | $100                 |
      | Recipient Email| friend@example.com   |
      | Message        | Happy Birthday!      |
      | Delivery Date  | 2024-12-25          |
    Then the gift card should be scheduled for delivery
    And I should receive a purchase confirmation

  Scenario: Redeem gift card
    Given I have a gift card with code "GC-12345-ABCDE"
    When I enter the gift card code at checkout
    Then the gift card balance should be applied to my order
    And any remaining balance should be saved to my account
