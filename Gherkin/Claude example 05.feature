Feature: Product Reviews
  As a customer
  I want to read and write product reviews
  So that I can make informed decisions and share my experience

  Background:
    Given I am logged in as a customer

  Scenario: Submit a product review
    Given I have purchased product "PROD-001"
    And I navigate to the product review section
    When I submit a review with the following details:
      | Field       | Value                              |
      | Rating      | 4                                  |
      | Title       | Great product with minor issues    |
      | Description | The quality is good but sizing... |
      | Photos      | 2 photos                          |
    Then my review should be visible on the product page
    And the product's average rating should be updated
    And I should receive a confirmation email

  Scenario: Filter product reviews
    Given I am on a product page with multiple reviews
    When I filter reviews by:
      | Filter    | Value     |
      | Rating    | 4+ stars  |
      | Has Photos| Yes       |
      | Date      | Last month|
    Then I should only see reviews matching my filters
    And the review count should update accordingly
