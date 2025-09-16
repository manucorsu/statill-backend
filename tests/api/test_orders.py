import pytest

from fastapi.testclient import TestClient

from app.main import app
from ..utils import (
    schema_test,
    get_json,
    not_found_response_test,
    successful_rud_response_test,
    successful_post_response_test,
    bad_request_test,
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
        "store_id": store_id,  # temp!!
        "payment_method": random.randint(0, 3),
        "products": [
            {"product_id": p["id"], "quantity": random.randint(1, int(p["quantity"]))}
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
    while invalid_id in [p["id"] for p in all_orders]:
        invalid_id += 1

    response = client.get(f"/api/v1/orders/{invalid_id}")
    not_found_response_test(response)


def test_get_order():
    id = random.choice(get_json("/api/v1/orders/", client)["data"])["id"]

    response = client.get(f"/api/v1/orders/{id}")
    schema_test(response.json(), GetOrderResponse)


def test_create_order():
    order = _random_order()
    response = client.post("/api/v1/orders/", data=json.dumps(order))
    successful_post_response_test(response)


def test_create_order_invalid_store():
    all_stores = (get_json("/api/v1/stores/", client))["data"]
    invalid_store_id = 1
    while invalid_store_id in [p["id"] for p in all_stores]:
        invalid_store_id += 1

    order = _random_order()
    order["store_id"] = invalid_store_id
    response = client.post("/api/v1/orders/", data=json.dumps(order))
    not_found_response_test(response)


def test_create_order_with_no_products():
    order = _random_order()
    order["products"] = []
    response = client.post("/api/v1/orders/", data=json.dumps(order))
    bad_request_test(response)


def test_create_order_with_too_high_qty_products():
    order = _random_order()
    product_id = order["products"][0]["product_id"]
    product_max_qty = get_json(f"/api/v1/products/{product_id}", client)["data"][
        "quantity"
    ]

    order["products"][0]["quantity"] = product_max_qty + 23.24

    response = client.post("/api/v1/orders/", data=json.dumps(order))
    bad_request_test(response)


def test_get_orders_by_store_id():
    all_stores = (get_json("/api/v1/stores", client))["data"]
    random_store_id = (random.choice(all_stores))["id"]

    response = client.get(f"/api/v1/orders/store/{random_store_id}")
    schema_test(response.json(), GetAllOrdersResponse)


def test_get_orders_by_user_id():
    all_users = (get_json("/api/v1/users", client))["data"]
    random_user_id = (random.choice(all_users))["id"]

    response = client.get(f"/api/v1/orders/user/{random_user_id}")
    schema_test(response.json(), GetAllOrdersResponse)


def test_update_order_products():
    id = random.choice(get_json("/api/v1/orders/", client)["data"])["id"]
    order = _random_order()
    response = client.patch(
        f"/api/v1/orders/{id}/products", data=json.dumps({"products": order["products"]})
    )
    successful_rud_response_test(response)

def test_update_order_status():
    all_orders = (get_json("/api/v1/orders/", client))["data"]
    order = None
    for o in all_orders:
        if o["status"] not in ["received", "cancelled"]:
            order = o
            break
    
    assert order is not None

    response = client.patch(
        f"/api/v1/orders/{order['id']}/status"
    )
    successful_rud_response_test(response)

def test_order_cancel():
    all_orders = (get_json("/api/v1/orders/", client))["data"]
    order = None
    for o in all_orders:
        if o["status"] not in ["received", "cancelled"]:
            order = o
            break
    
    assert order is not None

    response = client.patch(
        f"/api/v1/orders/{order['id']}/cancel"
    )
    successful_rud_response_test(response)

def test_create_order_product_from_other_store():
    invalid_product_id = 1
    order = _random_order()

    all_products = (get_json("/api/v1/products/", client))["data"]
    
    for product in all_products:
        if product["store_id"] == order["store_id"]:
            continue
        else:
            invalid_product_id = product["id"]
            break

    order["products"].append({"product_id": invalid_product_id, "quantity": 1})
    response = client.post("/api/v1/orders/", data=json.dumps(order))
    bad_request_test(response)
