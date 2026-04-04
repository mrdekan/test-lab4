from behave import given, when, then
from app.eshop import Product, ShoppingCart, Order

@given('An item named "{name}" is created with price {price:d} and {stock:d} in stock')
def build_custom_item(context, name, price, stock):
    context.current_item = Product(name, price, stock)
    if not hasattr(context, 'items_catalog'):
        context.items_catalog = {}
    context.items_catalog[name] = context.current_item

@given('An item with no name, price {price:d}, and {stock:d} in stock')
def build_nameless_item(context, price, stock):
    context.current_item = Product("", price, stock)

@then("The item's price must equal {price:d}")
def verify_item_price(context, price):
    assert context.current_item.price == price, f"Expected {price}, got {context.current_item.price}"

@then("The item's name must be an empty string")
def verify_blank_name(context):
    assert context.current_item.name == ""

@when('I attempt to put {amount} units of the item into the basket')
def attempt_add_to_basket(context, amount):
    try:
        context.basket.add_product(context.current_item, int(amount))
        context.threw_exception = False
    except ValueError:
        context.threw_exception = True

@when('I provide a None value for the item quantity')
def attempt_add_none(context):
    try:
        context.basket.add_product(context.current_item, None)
        context.threw_exception = False
    except Exception:
        context.threw_exception = True

@when('I provide a string "{val}" for the item quantity')
def attempt_add_string(context, val):
    try:
        context.basket.add_product(context.current_item, val)
        context.threw_exception = False
    except Exception:
        context.threw_exception = True

@then('An exception should be thrown')
def check_for_exception(context):
    assert context.threw_exception is True

@then('The total basket value should be {total:d}')
def verify_basket_total(context, total):
    assert context.basket.calculate_total() == total

@when('I delete the item "{name}" from the basket')
def remove_item_by_name(context, name):
    dummy_item = Product(name, 0, 0)
    context.basket.remove_product(dummy_item)

@then('The basket must stay empty')
def verify_empty_basket(context):
    assert len(context.basket.products) == 0

@when('I finalize the checkout')
def process_checkout(context):
    try:
        new_order = Order(context.basket)
        new_order.place_order()
        context.system_crashed = False
    except Exception:
        context.system_crashed = True

@then('The application should not crash')
def verify_no_crash(context):
    assert context.system_crashed is False

@then('The item is successfully placed in the basket')
def verify_successful_addition(context):
    assert len(context.basket.products) > 0

@when('I insert {a1:d} of "{n1}" and {a2:d} of "{n2}" into the basket')
def insert_multiple_items(context, a1, n1, a2, n2):
    context.basket.add_product(context.items_catalog[n1], a1)
    context.basket.add_product(context.items_catalog[n2], a2)

@given('The item has a stock count of {stock:d}')
def setup_item_stock(context, stock):
    context.current_item = Product("Default", 100, stock)

@given('A new shopping basket')
def setup_empty_basket(context):
    context.basket = ShoppingCart()