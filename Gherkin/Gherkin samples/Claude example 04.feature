Feature: Product Search and Filtering
  As a customer
  I want to search and filter products
  So that I can find what I'm looking for quickly

  Background:
    Given I am on the product listing page

  Scenario: Search products by keyword
    When I enter "winter jacket" in the search bar
    And I click the search button
    Then I should see products related to "winter jacket"
    And the search results should show the number of items found
    And each product should contain the word "jacket" in its name or description

  Scenario: Filter products by multiple criteria
    When I apply the following filters:
      | Filter Category | Selection |
      | Price Range    | $50-$100  |
      | Size           | Medium    |
      | Color          | Blue      |
      | Brand          | Nike      |
    Then I should see only products that match all selected criteria
    And I should be able to remove filters individually
    And the product count should update automatically
