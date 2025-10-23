import pytest

from fastapi.testclient import TestClient

from app.main import app
from ..utils import (
    schema_test,
    get_json,
    not_found_response_test,
    successful_ud_response_test,
    successful_post_response_test,
    bad_request_test,
    get_json_data,
)
from app.schemas.order import GetAllOrdersResponse, GetOrderResponse

import random

import json

from typing import Literal

client = TestClient(app)


# random valid qty product
def fp(products_list):
    random.shuffle(products_list)
    for p in products_list:
        if int(p["quantity"]) > 1:
            return p
    pytest.skip("No products have enough qty")


def usable_products_list(products_list):
    random.shuffle(products_list)
    usable_products = []
    for p in products_list:
        if int(p["quantity"]) > 1 and p not in usable_products:
            usable_products.append(p)

    match (len(usable_products)):
        case 0:
            pytest.skip("Not enough usable products")
        case 1:
            return usable_products
        case _:
            return [
                p for p in usable_products[: random.randint(1, len(usable_products))]
            ]


def _random_order():
    store_id = random.choice(get_json_data("/api/v1/stores/", client))["id"]
    all_products = get_json_data(f"/api/v1/products/store/{store_id}", client)
    temp_user_id = random.choice(get_json_data("/api/v1/users/", client))["id"]

    return {
        "user_id": temp_user_id,  # temp!!
        "store_id": store_id,
        "payment_method": random.randint(0, 3),
        "products": [
            {
                "product_id": product["id"],
                "quantity": random.randint(1, int(product["quantity"])),
            }
            for product in usable_products_list(all_products)
        ],
    }


def get_order_with_status(
    status: Literal["pending", "accepted", "received", "cancelled"],
):
    all_orders = get_json_data("/api/v1/orders/", client)
    for o in all_orders:
        if o["status"] == status:
            return o

    pytest.skip(f"Found no orders with status {status}")


def test_get_all_orders():
    response = client.get("/api/v1/orders/")
    assert response.status_code == 200
    schema_test(response.json(), GetAllOrdersResponse)


def test_get_order_invalid_id():
    all_orders = get_json_data("/api/v1/orders/", client)
    random.shuffle(all_orders)
    invalid_id = 1
    while invalid_id in [p["id"] for p in all_orders]:
        invalid_id += 1

    response = client.get(f"/api/v1/orders/{invalid_id}")
    not_found_response_test(response)


def test_get_order():
    all_orders = get_json_data("/api/v1/orders", client)
    if len(all_orders) == 0:
        pytest.skip("There are no orders.")

    id = random.choice(all_orders)["id"]
    response = client.get(f"/api/v1/orders/{id}")
    schema_test(response.json(), GetOrderResponse)


def test_create_order():
    order = _random_order()
    response = client.post("/api/v1/orders/", data=json.dumps(order))
    # assert response.json() == object()
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
    store_id = random.choice(get_json_data("/api/v1/stores/", client))["id"]
    temp_user_id = random.choice(get_json_data("/api/v1/users/", client))["id"]
    response = client.post(
        "/api/v1/orders/",
        data=json.dumps(
            {
                "user_id": temp_user_id,  # temp!!
                "store_id": store_id,
                "payment_method": random.randint(0, 3),
                "products": [],
            }
        ),
    )
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


def test_update_pending_order_products():
    order = get_order_with_status("pending")

    all_products = get_json_data(f"/api/v1/products/store/{order['store_id']}/", client)
    products = [
        {"product_id": p["id"], "quantity": random.randint(1, int(p["quantity"]))}
        for p in usable_products_list(all_products)
    ]
    response = client.patch(
        f"/api/v1/orders/{order['id']}/products",
        data=json.dumps({"products": products}),
    )

    successful_ud_response_test(response)


def test_update_non_pending_order_products():
    order = None
    for o in get_json_data("/api/v1/orders/", client):
        if o["status"] != "pending":
            order = o
    if order is None:
        pytest.skip("Found no orders that weren't pending.")

    products = [
        {"product_id": p["id"], "quantity": random.randint(1, int(p["quantity"]))}
        for p in usable_products_list(
            get_json_data(f"/api/v1/products/store/{order['store_id']}/", client)
        )
    ]
    response = client.patch(
        f"/api/v1/orders/{order['id']}/products",
        data=json.dumps({"products": products}),
    )
    bad_request_test(response)


def test_update_order_products_with_empty_products_list():
    order = get_order_with_status("pending")
    response = client.patch(
        f"/api/v1/orders/{order['id']}/products", data=json.dumps({"products": []})
    )
    bad_request_test(response)


def test_update_order_products_with_product_from_other_store():
    order = get_order_with_status("pending")

    all_stores = get_json_data("/api/v1/stores/", client)
    random.shuffle(all_stores)
    other_store_id = None
    for store in all_stores:
        id = store["id"]
        if id != order["store_id"]:
            other_store_id = id
    if other_store_id is None:
        pytest.skip(f"No other stores apart from {order['store_id']}")

    product = fp(get_json_data(f"/api/v1/products/store/{other_store_id}/", client))
    response = client.patch(
        f"/api/v1/orders/{order['id']}/products/",
        data=json.dumps(
            {
                "products": [
                    {
                        "product_id": product["id"],
                        "quantity": random.randint(1, int(product["quantity"])),
                    }
                ]
            }
        ),
    )

    bad_request_test(response)


def test_update_order_products_with_too_high_qty_product():
    order = get_order_with_status("pending")

    product_id = random.choice(order["products"])["product_id"]
    product_max_qty = get_json_data(f"/api/v1/products/{product_id}", client)[
        "quantity"
    ]
    order["products"][0]["quantity"] = product_max_qty + 23.24

    response = client.patch(
        f"/api/v1/orders/{order['id']}/products/",
        data=json.dumps({"products": order["products"]}),
    )

    bad_request_test(response)


def test_update_order_products_invalid_product_id():
    all_products = get_json_data("/api/v1/products/", client)
    random.shuffle(all_products)
    invalid_id = 1
    while invalid_id in [p["id"] for p in all_products]:
        invalid_id += 1

    order = get_order_with_status("pending")
    order["products"] = [{"product_id": invalid_id, "quantity": 1}]
    response = client.patch(
        f"/api/v1/orders/{order['id']}/products/",
        data=json.dumps({"products": order["products"]}),
    )
    not_found_response_test(response)


def test_update_order_status():
    all_orders = get_json_data("/api/v1/orders", client)
    order = None
    for o in all_orders:
        if o["status"] not in ["received", "cancelled"]:
            order = o
            break

    assert order is not None

    response = client.patch(f"/api/v1/orders/{order['id']}/status")
    # assert response.json() == object()
    successful_ud_response_test(response)


def test_cancel_order():
    all_orders = get_json_data("/api/v1/orders", client)
    order = None
    for o in all_orders:
        if o["status"] not in ["received", "cancelled"]:
            order = o
            break

    if order is None:
        pytest.skip("No orders were received or cancelled.")

    response = client.patch(f"/api/v1/orders/{order['id']}/cancel")
    successful_ud_response_test(response)


def test_cancel_received_order():
    order = get_order_with_status("received")
    response = client.patch(f"/api/v1/orders/{order['id']}/cancel")
    bad_request_test(response)


def test_create_order_product_from_other_store():
    invalid_product_id = None
    order = _random_order()

    all_products = get_json_data(f"/api/v1/products/", client)
    random.shuffle(all_products)
    for product in all_products:
        if product["store_id"] != order["store_id"]:
            invalid_product_id = product["id"]
            break
    if invalid_product_id is None:
        pytest.skip(
            f"No products from other stores (that aren't {order['store_id']}) found"
        )

    order["products"].append({"product_id": invalid_product_id, "quantity": 1})
    response = client.post("/api/v1/orders/", data=json.dumps(order))
    bad_request_test(response)


def test_update_received_order_status():
    order = get_order_with_status("received")
    response = client.patch(f"/api/v1/orders/{order['id']}/status")
    bad_request_test(response)


def test_update_cancelled_order_status():
    all_orders = (get_json("/api/v1/orders/", client))["data"]
    order = None
    for o in all_orders:
        if o["status"] == "cancelled":
            order = o
            break

    response = client.patch(f"/api/v1/orders/{order['id']}/status")
    bad_request_test(response)


def test_update_accepted_order_status():
    order = get_order_with_status("accepted")
    response = client.patch(f"/api/v1/orders/{order['id']}/status")

    if response.status_code == 400:
        message = response.json()["data"]["message"]
        if message.startswith("Not enough") and message.endswith("in stock"):
            pytest.skip(
                "Not enough stock to update order status, skipped because if not this would take 85 years longer to run"
            )

    successful_ud_response_test(response)
