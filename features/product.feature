Feature: Inventory Check
Ensuring that the system correctly validates the available stock of items.

Scenario: Sufficient stock for purchase
Given An item called "Product1" is set with a stock level of 123
When I verify if 123 units of the item can be purchased
Then The item is confirmed available

Scenario: Insufficient stock for purchase
Given An item called "Product1" is set with a stock level of 123
When I verify if 124 units of the item can be purchased
Then The item is confirmed unavailable