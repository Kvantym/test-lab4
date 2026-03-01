import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import uuid
import boto3
import pytest
import random
from datetime import datetime, timedelta, timezone
from eshop import Product, ShoppingCart, Order
from services.service import ShippingService
from services.repository import ShippingRepository
from services.publisher import ShippingPublisher
from services.config import AWS_ENDPOINT_URL, AWS_REGION, SHIPPING_QUEUE


@pytest.fixture
def shipping_service():
    return ShippingService(ShippingRepository(), ShippingPublisher())


def test_place_order_with_mocked_repo(mocker):
    mock_repo = mocker.Mock()
    mock_publisher = mocker.Mock()
    service = ShippingService(mock_repo, mock_publisher)
    mock_repo.create_shipping.return_value = "ship_123"

    cart = ShoppingCart()
    cart.add_product(Product("Test", 100, 10), 1)
    order = Order(cart, service, "order_123")

    res = order.place_order("Нова Пошта")
    assert res == "ship_123"


def test_create_shipping_persistence(shipping_service):
    sid = shipping_service.create_shipping("Укр Пошта", ["p1"], "ord_1", datetime.now(timezone.utc) + timedelta(days=1))
    item = shipping_service.repository.get_shipping(sid)
    assert item is not None
    assert item['shipping_type'] == "Укр Пошта"


def test_sqs_message_published(shipping_service):
    sid = shipping_service.create_shipping("Нова Пошта", ["p2"], "ord_2",
                                           datetime.now(timezone.utc) + timedelta(days=1))
    messages = shipping_service.publisher.poll_shipping()
    assert sid in messages


def test_invalid_shipping_type_fails(shipping_service):
    with pytest.raises(ValueError, match="Shipping type is not available"):
        shipping_service.create_shipping("Дрон", ["p1"], "o1", datetime.now(timezone.utc) + timedelta(days=1))


def test_past_due_date_fails(shipping_service):
    past_date = datetime.now(timezone.utc) - timedelta(hours=1)
    with pytest.raises(ValueError, match="Shipping due datetime must be greater"):
        shipping_service.create_shipping("Нова Пошта", ["p1"], "o1", past_date)


def test_full_cart_to_shipping_flow(shipping_service):
    cart = ShoppingCart()
    cart.add_product(Product("Laptop", 1000, 5), 1)
    order = Order(cart, shipping_service)
    shipping_id = order.place_order("Meest Express")
    assert shipping_service.check_status(shipping_id) == "in progress"


def test_process_batch_integration(shipping_service):
    shipping_service.create_shipping("Самовивіз", ["p3"], "order_batch", datetime.now(timezone.utc) + timedelta(days=1))

    results = shipping_service.process_shipping_batch()
    assert len(results) > 0

    shipping_id = results[0].get('shipping_id')
    item = shipping_service.repository.get_shipping(shipping_id)

    assert item is not None
    assert item['status'] == "completed"


def test_shipping_failure_on_overdue(shipping_service):
    sid = shipping_service.repository.create_shipping(
        "Нова Пошта", ["p5"], "o5", "in progress", (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    )
    shipping_service.process_shipping(sid)
    assert shipping_service.check_status(sid) == "failed"


def test_status_update_logic(shipping_service):
    sid = shipping_service.repository.create_shipping("Самовивіз", ["p"], "o", "created",
                                                      (datetime.now(timezone.utc) + timedelta(days=1)).isoformat())
    shipping_service.repository.update_shipping_status(sid, "completed")
    assert shipping_service.check_status(sid) == "completed"


def test_get_shipping_details(shipping_service):
    sid = shipping_service.create_shipping("Нова Пошта", ["item123"], "order999",
                                           datetime.now(timezone.utc) + timedelta(days=2))
    details = shipping_service.repository.get_shipping(sid)
    assert "item123" in details['product_ids']
    assert details['order_id'] == "order999"