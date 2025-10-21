import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.product import GetAllProductsResponse, GetProductResponse

from ..utils import (
    get_json,
    get_json_data,
    schema_test,
    random_string,
    random_money,
    successful_post_response_test,
    successful_ud_response_test,
    not_found_response_test,
    bad_request_test,
)

import json

import random

client = TestClient(app)


def random_product():
    """
    Generate a JSON string representing a random order with various attributes.

    Returns:
        dict[str, Any]: A JSON-formatted string containing randomly generated product data, including
            name, brand, price, type, quantity, description, hidden status, and optionally a barcode.
    """
    temp_store_id = random.choice(client.get("/api/v1/stores/").json()["data"])["id"]

    return {
        "name": random_string(),
        "brand": random_string(max_len=30),
        "price": random_money(),
        "points_price": random.choice((None, random.randint(1, 100))),
        "type": random.randint(1, 255),
        "quantity": random.randint(1, 10000),
        "desc": random_string(max_len=512),
        "hidden": random.choice((True, False)),
        "barcode": random_string(64, 128) if random.choice((True, False)) else None,
        "store_id": temp_store_id,
    }


def _random_product_id():
    all_products = get_json("/api/v1/products/", client)["data"]
    return int(random.choice(all_products)["id"])


def test_get_all_products():
    response = client.get("/api/v1/products/")
    assert response.status_code == 200

    schema_test(response.json(), GetAllProductsResponse)


def test_get_all_products_including_anonymized():
    response = client.get("/api/v1/products/?include_anonymized=true")
    assert response.status_code == 200
    schema_test(response.json(), GetAllProductsResponse)


def test_create_product():
    product = random_product()
    response = client.post("/api/v1/products/", data=json.dumps(product))
    successful_post_response_test(response)


def test_get_product():
    all_products = (get_json("/api/v1/products/", client))["data"]
    if all_products == []:
        raise ValueError(
            "For test_get_product to work there needs to be at least one GETtable product in the database."
        )
    random_product = random.choice(all_products)
    response = client.get(f"/api/v1/products/{random_product['id']}")
    assert response.status_code == 200

    schema_test(response.json(), GetProductResponse)

def test_get_products_by_store_id():
    all_products = (get_json("/api/v1/products/", client))["data"]
    all_stores = (get_json("/api/v1/stores/", client))["data"]
    if all_products == []:
        raise ValueError(
            "For test_get_products_by_store_id to work there needs to be at least one GETtable product in the database."
        )
    random_store = random.choice(all_stores)
    response = client.get(f"/api/v1/products/store/{random_store['id']}")
    assert response.status_code == 200

    schema_test(response.json(), GetAllProductsResponse)


def test_update_product():
    id = random.choice(get_json("/api/v1/products/", client)["data"])["id"]
    product = random_product()
    response = client.put(f"/api/v1/products/{id}", data=json.dumps(product))
    successful_ud_response_test(response)


def test_delete_product():
    all_orders = get_json("/api/v1/orders", client)["data"]
    all_products = get_json("/api/v1/products/", client)["data"]

    ids_in_orders = []
    for order in all_orders:
        for product in order["products"]:
            ids_in_orders.append(product["product_id"])
    
    id = None

    for product in all_products:
        if product["id"] not in ids_in_orders:
            id = product["id"]
            break

    if id == None:
        pytest.skip("no hay productos sin orders")

    response = client.delete(f"/api/v1/products/{id}")
    successful_ud_response_test(response)


def test_get_not_existing_product():
    all_products = (get_json("/api/v1/products/", client))["data"]
    invalid_id: int = 1
    while invalid_id in [p["id"] for p in all_products]:
        invalid_id += 1
    response = client.get(f"/api/v1/products/{invalid_id}")
    assert response.status_code == 404

    not_found_response_test(response)


def test_product_create_data_hidden_none():
    product = random_product()
    product["hidden"] = None
    response = client.post("/api/v1/products/", data=json.dumps(product))
    successful_post_response_test(response)


def test_product_create_deleted_product_400():
    product = random_product()
    product["name"] = "Deleted Product"
    response = client.post("/api/v1/products/", data=json.dumps(product))
    bad_request_test(response)


def test_product_update_data_hidden_none():
    id = random.choice(get_json("/api/v1/products/", client)["data"])["id"]
    product = random_product()
    product["hidden"] = None
    response = client.put(f"/api/v1/products/{id}", data=json.dumps(product))
    successful_ud_response_test(response)


def test_delete_product_when_in_pa_orders():
    product = random.choice(get_json_data("/api/v1/products/", client))
    if product["quantity"] <= 1:
        pytest.skip(f"Invalid product quantity")
    # add a random amount to it to an order
    order_post_response = client.post(
        "/api/v1/orders/",
        data=json.dumps(
            {
                "store_id": product["store_id"],
                "products": [
                    {
                        "product_id": product["id"],
                        "quantity": random.randint(1, int(product["quantity"])),
                    }
                ],
                "payment_method": random.randint(0, 3),
                "user_id": 1,
            }
        ),
    )

    # 50% chance of it being set to accepted
    if random.choice((False, True)):
        opr_json = order_post_response.json()
        # assert opr_json == object()
        id = opr_json["data"]["id"]
        client.patch(f"/api/v1/orders/{id}/status")

    response = client.delete(f"/api/v1/products/{product['id']}")
    bad_request_test(response)
