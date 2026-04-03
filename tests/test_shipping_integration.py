import uuid
import pytest
import boto3
import random
from datetime import datetime, timedelta, timezone

from app.eshop import Product, ShoppingCart, Order
from services import ShippingService
from services.repository import ShippingRepository
from services.publisher import ShippingPublisher
from services.config import AWS_ENDPOINT_URL, AWS_REGION, SHIPPING_QUEUE


def test_create_shipping_persists_in_dynamodb(dynamo_resource):
    service = ShippingService(ShippingRepository(), ShippingPublisher())

    shipping_id = service.create_shipping(
        ShippingService.list_available_shipping_type()[0],
        ["Product1"],
        "order_123",
        datetime.now(timezone.utc) + timedelta(minutes=1)
    )

    repo = ShippingRepository()
    shipping = repo.get_shipping(shipping_id)

    assert shipping["shipping_id"] == shipping_id


def test_shipping_status_after_creation_is_in_progress(dynamo_resource):
    service = ShippingService(ShippingRepository(), ShippingPublisher())

    shipping_id = service.create_shipping(
        ShippingService.list_available_shipping_type()[0],
        ["Product1"],
        "order_123",
        datetime.now(timezone.utc) + timedelta(minutes=1)
    )

    status = service.check_status(shipping_id)
    assert status == ShippingService.SHIPPING_IN_PROGRESS


def test_when_place_order_then_shipping_in_queue(dynamo_resource):
    service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart = ShoppingCart()

    cart.add_product(Product("Product", random.random() * 10000, 10), 2)
    order = Order(cart, service)

    sqs_client = boto3.client(
        "sqs",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION
    )

    queue_url = sqs_client.get_queue_url(QueueName=SHIPPING_QUEUE)["QueueUrl"]

    sqs_client.purge_queue(QueueUrl=queue_url)

    shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[0],
        datetime.now(timezone.utc) + timedelta(minutes=1)
    )

    response = sqs_client.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=10
    )

    messages = response.get("Messages", [])

    assert len(messages) == 1
    assert messages[0]["Body"] == shipping_id


def test_process_shipping_completes_valid_shipping(dynamo_resource):
    service = ShippingService(ShippingRepository(), ShippingPublisher())

    shipping_id = service.create_shipping(
        ShippingService.list_available_shipping_type()[0],
        ["Product1"],
        "order_123",
        datetime.now(timezone.utc) + timedelta(minutes=5)
    )

    service.process_shipping(shipping_id)

    status = service.check_status(shipping_id)
    assert status == ShippingService.SHIPPING_COMPLETED


def test_process_shipping_fails_if_expired(dynamo_resource):
    service = ShippingService(ShippingRepository(), ShippingPublisher())

    shipping_id = service.repository.create_shipping(
        ShippingService.list_available_shipping_type()[0],
        ["Product1"],
        "order_123",
        ShippingService.SHIPPING_CREATED,
        datetime.now(timezone.utc) - timedelta(minutes=1)
    )

    service.process_shipping(shipping_id)

    status = service.check_status(shipping_id)
    assert status == ShippingService.SHIPPING_FAILED


def test_process_shipping_batch(dynamo_resource):
    service = ShippingService(ShippingRepository(), ShippingPublisher())

    sqs_client = boto3.client(
        "sqs",
        endpoint_url=AWS_ENDPOINT_URL,
        region_name=AWS_REGION
    )
    queue_url = sqs_client.get_queue_url(QueueName=SHIPPING_QUEUE)["QueueUrl"]

    sqs_client.purge_queue(QueueUrl=queue_url)

    for _ in range(3):
        service.create_shipping(
            ShippingService.list_available_shipping_type()[0],
            ["Product"],
            str(uuid.uuid4()),
            datetime.now(timezone.utc) + timedelta(minutes=1)
        )

    result = service.process_shipping_batch()

    assert len(result) == 3


def test_order_full_integration_flow(dynamo_resource):
    service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart = ShoppingCart()

    cart.add_product(Product("Product", 100, 10), 2)

    order = Order(cart, service)

    shipping_id = order.place_order(
        ShippingService.list_available_shipping_type()[0],
        datetime.now(timezone.utc) + timedelta(minutes=1)
    )

    status = service.check_status(shipping_id)

    assert status == ShippingService.SHIPPING_IN_PROGRESS


def test_cart_cleared_after_order(dynamo_resource):
    service = ShippingService(ShippingRepository(), ShippingPublisher())
    cart = ShoppingCart()

    product = Product("Product", 100, 10)
    cart.add_product(product, 2)

    order = Order(cart, service)

    order.place_order(
        ShippingService.list_available_shipping_type()[0],
        datetime.now(timezone.utc) + timedelta(minutes=1)
    )

    assert len(cart.products) == 0


def test_create_shipping_with_past_due_date_fails(dynamo_resource):
    service = ShippingService(ShippingRepository(), ShippingPublisher())

    with pytest.raises(ValueError):
        service.create_shipping(
            ShippingService.list_available_shipping_type()[0],
            ["Product"],
            "order_123",
            datetime.now(timezone.utc) - timedelta(seconds=1)
        )


def test_check_status_returns_correct_value(dynamo_resource):
    service = ShippingService(ShippingRepository(), ShippingPublisher())

    shipping_id = service.create_shipping(
        ShippingService.list_available_shipping_type()[0],
        ["Product"],
        "order_123",
        datetime.now(timezone.utc) + timedelta(minutes=1)
    )

    status = service.check_status(shipping_id)

    assert status in [
        ShippingService.SHIPPING_IN_PROGRESS,
        ShippingService.SHIPPING_COMPLETED,
        ShippingService.SHIPPING_FAILED
    ]