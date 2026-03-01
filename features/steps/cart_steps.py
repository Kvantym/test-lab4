from behave import given, when, then
from eshop import Product, ShoppingCart, Order

@given("The product has availability of {availability}")
def step_impl(context, availability):
    context.product = Product("Test", 100, int(availability))

@given("An empty shopping cart")
def step_impl(context):
    context.cart = ShoppingCart()

@when("I add product to the cart in amount {amount}")
def step_impl(context, amount):
    try:
        context.cart.add_product(context.product, int(amount))
        context.status = True
    except:
        context.status = False

@when('I try to add {val} amount')
def step_impl(context, val):
    try:
        # Обробка тексту "None" або рядка "text"
        actual_val = None if val == "None" else val
        context.cart.add_product(context.product, actual_val)
        context.status = True
    except:
        context.status = False

@then("Product is added to the cart successfully")
def step_impl(context):
    assert context.status is True

@then("Product is not added to cart successfully")
@then("System should handle error")
def step_impl(context):
    assert context.status is False

@given("A cart with price {price} and {amount} items")
def step_impl(context, price, amount):
    context.cart = ShoppingCart()
    p = Product("Item", int(price), 100)
    context.cart.add_product(p, int(amount))

@then("Total price should be {total}")
def step_impl(context, total):
    assert context.cart.calculate_total() == int(total)

@given('The product "{name}" has availability {stock}')
def step_impl(context, name, stock):
    context.product = Product(name, 100, int(stock))

@when('I add product "{name}" to the cart in amount {amount}')
def step_impl(context, name, amount):
    context.cart.add_product(context.product, int(amount))

@when("I place an order")
def step_impl(context):
    Order(context.cart).place_order()

@then('Product "{name}" should have availability {count}')
def step_impl(context, name, count):
    assert context.product.available_amount == int(count)

@given("A cart with a product")
def step_impl(context):
    context.cart = ShoppingCart()
    context.product = Product("X", 10, 10)
    context.cart.add_product(context.product, 1)

@when("I remove that product")
def step_impl(context):
    context.cart.remove_product(context.product)

@then("The cart should be empty")
def step_impl(context):
    assert len(context.cart.products) == 0