Feature: Returns and Refunds
  As a customer
  I want to return items and receive refunds
  So that I can manage unsatisfactory purchases

  Scenario: Initiate a return
    Given I have an eligible order for return
    When I initiate a return request
    And I select the following details:
      | Field          | Value                    |
      | Items          | 2 of 3 items             |
      | Return Reason  | Wrong size               |
      | Return Method  | Drop-off at local store  |
    Then I should receive return shipping labels
    And I should receive return instructions
    And the return should be tracked in my account
