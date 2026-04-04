from behave import given, when, then
from eshop import Product

@given('An item called "{name}" is set with a stock level of {availability}')
def define_item_stock(context, name, availability):
    context.target_item = Product(name=name, price=100, available_amount=int(availability))

@when('I verify if {amount} units of the item can be purchased')
def verify_stock_level(context, amount):
    context.has_sufficient_stock = context.target_item.is_available(int(amount))

@then('The item is confirmed available')
def assert_item_available(context):
    assert context.has_sufficient_stock is True

@then('The item is confirmed unavailable')
def assert_item_unavailable(context):
    assert context.has_sufficient_stock is False