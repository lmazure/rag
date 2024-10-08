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

Feature: Price Alerts
  As a customer
  I want to set price alerts for products
  So that I can purchase items when they reach my desired price

  Scenario: Set price alert
    Given I am viewing a product priced at "$199.99"
    When I set a price alert for "$150.00"
    Then I should receive a confirmation
    And I should be notified when the price drops to or below $150.00

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
