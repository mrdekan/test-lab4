"""
Simple e-shop domain models: Product, ShoppingCart, Order, Shipment.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, List

from services import ShippingService


class Product:
    """Represents a product in the store."""

    def __init__(self, name: str, price: float, available_amount: int):
        self.name = name
        self.price = price
        self.available_amount = available_amount

    def is_available(self, requested_amount: int) -> bool:
        """Check if requested amount is available."""
        return self.available_amount >= requested_amount

    def buy(self, requested_amount: int) -> None:
        """Decrease available amount after purchase."""
        if requested_amount > self.available_amount:
            raise ValueError("Not enough items in stock")
        self.available_amount -= requested_amount

    def __eq__(self, other) -> bool:
        return isinstance(other, Product) and self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)

    def __str__(self) -> str:
        return self.name


class ShoppingCart:
    """Represents a shopping cart with products."""

    def __init__(self):
        self.products: Dict[Product, int] = {}

    def contains_product(self, product: Product) -> bool:
        """Check if product is in cart."""
        return product in self.products

    def calculate_total(self) -> float:
        """Calculate total price of cart."""
        return sum(p.price * count for p, count in self.products.items())

    def add_product(self, product: Product, amount: int) -> None:
        """Add product to cart or increase its quantity."""
        if amount <= 0:
            raise ValueError("Amount must be positive")

        if not product.is_available(amount):
            raise ValueError(
                f"Product {product} has only {product.available_amount} items"
            )

        self.products[product] = self.products.get(product, 0) + amount

    def remove_product(self, product: Product) -> None:
        """Remove product from cart."""
        if product in self.products:
            del self.products[product]

    def submit_cart_order(self) -> List[str]:
        """Finalize order: decrease stock and return product identifiers."""
        product_ids = []

        # Safeguard: If products is uninitialized or empty, safely return
        if not getattr(self, 'products', None):
            return product_ids

        for product, count in self.products.items():
            product.buy(count)
            product_ids.append(str(product))

        self.products.clear()
        return product_ids


@dataclass
class Order:
    """Represents an order with shipping."""

    cart: ShoppingCart
    shipping_service: ShippingService
    order_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def place_order(
        self,
        shipping_type: str,
        due_date: Optional[datetime] = None,
    ):
        """Place order and create shipment."""
        if due_date is None:
            due_date = datetime.now(timezone.utc) + timedelta(seconds=3)

        product_ids = self.cart.submit_cart_order()

        return self.shipping_service.create_shipping(
            shipping_type=shipping_type,
            product_ids=product_ids,
            order_id=self.order_id,
            due_date=due_date,
        )


@dataclass
class Shipment:
    """Represents a shipment."""

    shipping_id: str
    shipping_service: ShippingService

    def check_shipping_status(self):
        """Check shipment status."""
        return self.shipping_service.check_status(self.shipping_id)