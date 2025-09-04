import pytest

from fastapi.testclient import TestClient

from app.main import app
from ..utils import (
    schema_test,
    get_json,
    not_found_response_test,
    successful_rud_response_test,
    successful_post_response_test,
)
from app.schemas.order import GetAllOrdersResponse, GetOrderResponse

import random

import json

client = TestClient(app)


def _random_order():
    store_id = random.choice(client.get("/api/v1/stores/").json()["data"])["id"]
    all_products = ((client.get(f"/api/v1/products/store/{store_id}")).json())["data"]
    temp_user_id = random.choice(client.get("/api/v1/users/").json()["data"])["id"]

    random.shuffle(all_products)
    return {
        "user_id": temp_user_id,
        "store_id": store_id, #temp!!
        "payment_method": random.randint(0, 3),
        "products": [
            {"product_id": p["id"], "quantity": random.randint(1, p["quantity"])}
            for p in all_products[: random.randint(1, len(all_products))]
        ],
    }


def test_get_all_orders():
    response = client.get("/api/v1/orders/")
    assert response.status_code == 200
    schema_test(response.json(), GetAllOrdersResponse)


def test_get_order_invalid_id():
    all_orders = (get_json("/api/v1/orders/", client))["data"]
    invalid_id = 1
    while invalid_id in (p["id"] for p in all_orders):
        invalid_id += 1

    response = client.get(f"/api/v1/orders/{invalid_id}")
    not_found_response_test(response)


def test_get_order():
    id = random.choice(get_json("/api/v1/orders/", client)["data"])["id"]

    response = client.get(f"/api/v1/orders/{id}")
    successful_rud_response_test(response)


# def test_get_all_orders_by_store_id():
# id = random.choice(get_json("/api/v1/stores/", client)["data"])["id"]

# response = client.get(f"/api/v1/orders/store/{id}")

# def test_get_all_by_user_id():


def test_create_order():
    order = _random_order()
    response = client.post("/api/v1/orders/", data=json.dumps(order))
    successful_post_response_test(response)
