Feature: Shopping cart and Order validation

  Scenario: Add exact available amount
    Given The product has availability of 10
    And An empty shopping cart
    When I add product to the cart in amount 10
    Then Product is added to the cart successfully

  Scenario: Add more than available
    Given The product has availability of 10
    And An empty shopping cart
    When I add product to the cart in amount 11
    Then Product is not added to cart successfully

  Scenario: Add negative amount
    Given The product has availability of 10
    And An empty shopping cart
    When I add product to the cart in amount -1
    Then Product is not added to cart successfully

  Scenario: Add zero amount
    Given The product has availability of 5
    And An empty shopping cart
    When I add product to the cart in amount 0
    Then Product is added to the cart successfully

  Scenario: Add None instead of amount
    Given The product has availability of 10
    And An empty shopping cart
    When I try to add None amount
    Then System should handle error

  Scenario: Add string instead of amount
    Given The product has availability of 10
    And An empty shopping cart
    When I try to add "text" amount
    Then System should handle error

  Scenario: Calculate total for multiple items
    Given A cart with price 100 and 2 items
    Then Total price should be 200

  Scenario: Successful order reduces stock
    Given The product "Phone" has availability 5
    And An empty shopping cart
    When I add product "Phone" to the cart in amount 1
    And I place an order
    Then Product "Phone" should have availability 4

  Scenario: Remove product from cart
    Given A cart with a product
    When I remove that product
    Then The cart should be empty

  Scenario: Clear cart after order
    Given A cart with a product
    When I place an order
    Then The cart should be empty