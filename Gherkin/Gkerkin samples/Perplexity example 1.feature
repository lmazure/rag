Feature: Online Shopping Cart

  As a customer
  I want to add items to my shopping cart
  So that I can purchase them

  Background:
    Given the user is logged in
    And the following products are available:
      | Product Name | Price  | Stock |
      | T-shirt      | $19.99 | 100   |
      | Jeans        | $49.99 | 50    |
      | Sneakers     | $79.99 | 25    |
      | Hat          | $14.99 | 75    |

  Scenario: Add a single item to the cart
    When the user adds 1 "T-shirt" to the cart
    Then the cart should contain 1 item
    And the total price should be $19.99

  Scenario: Add multiple items to the cart
    When the user adds the following items to the cart:
      | Product Name | Quantity |
      | T-shirt      | 2        |
      | Jeans        | 1        |
    Then the cart should contain 3 items
    And the total price should be $89.97

  Scenario Outline: Apply discount codes
    Given the user has added "<Product>" to the cart
    When the user applies the discount code "<Code>"
    Then the total price should be "<Final Price>"

    Examples:
      | Product  | Code     | Final Price |
      | T-shirt  | SAVE10   | $17.99      |
      | Jeans    | SALE20   | $39.99      |
      | Sneakers | NEWCUST  | $71.99      |

  Scenario: Remove item from cart
    Given the user has the following items in the cart:
      | Product Name | Quantity |
      | T-shirt      | 2        |
      | Jeans        | 1        |
    When the user removes 1 "T-shirt" from the cart
    Then the cart should contain 2 items
    And the total price should be $69.98

  Scenario: Check stock availability
    When the user checks the stock for "Sneakers"
    Then the system should display "25 items available"

  Scenario Outline: Update quantity in cart
    Given the user has <Initial Quantity> "<Product>" in the cart
    When the user updates the quantity to <New Quantity>
    Then the cart should contain <New Quantity> "<Product>"
    And the total price should be <Total Price>

    Examples:
      | Product | Initial Quantity | New Quantity | Total Price |
      | T-shirt | 1                | 3            | $59.97      |
      | Jeans   | 2                | 1            | $49.99      |
      | Hat     | 3                | 5            | $74.95      |

  Scenario: Proceed to checkout
    Given the user has items in the cart
    When the user proceeds to checkout
    Then the system should display the order summary
    And prompt for shipping information

  Scenario: Empty cart
    Given the user has items in the cart
    When the user empties the cart
    Then the cart should be empty
    And the total price should be $0.00
