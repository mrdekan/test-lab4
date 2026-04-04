Feature: Testing System Limits and Invalid Inputs
Verifying how the e-commerce platform handles bad data types and extreme edge conditions.

Scenario: Inserting a negative quantity into the basket
Given The item has a stock count of 100
And A new shopping basket
When I attempt to put -10 units of the item into the basket
Then An exception should be thrown

Scenario: Attempting to buy more than what is available
Given The item has a stock count of 5
And A new shopping basket
When I attempt to put 6 units of the item into the basket
Then An exception should be thrown

Scenario: Providing None for the quantity
Given The item has a stock count of 100
And A new shopping basket
When I provide a None value for the item quantity
Then An exception should be thrown

Scenario: Providing a string for the quantity
Given The item has a stock count of 100
And A new shopping basket
When I provide a string "invalid" for the item quantity
Then An exception should be thrown

Scenario: Free item pricing check
Given An item named "Freebie" is created with price 0 and 10 in stock
Then The item's price must equal 0

Scenario: Handling items with sub-zero prices
Given An item named "Bug" is created with price -50 and 10 in stock
Then The item's price must equal -50

Scenario: Validation of blank item names
Given An item with no name, price 10, and 10 in stock
Then The item's name must be an empty string

Scenario: Deleting an item when the basket is already empty
Given A new shopping basket
When I delete the item "Non-existent" from the basket
Then The basket must stay empty

Scenario: Finalizing checkout without any items
Given A new shopping basket
When I finalize the checkout
Then The application should not crash

Scenario: Calculating total for several items
Given An item named "Item1" is created with price 10 and 5 in stock
And An item named "Item2" is created with price 20 and 5 in stock
And A new shopping basket
When I insert 1 of "Item1" and 2 of "Item2" into the basket
Then The total basket value should be 50