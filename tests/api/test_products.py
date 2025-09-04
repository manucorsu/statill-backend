import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.product import GetAllProductsResponse, GetProductResponse
from ..utils import (
    get_json,
    schema_test,
    random_string,
    random_money,
    successful_post_response_test,
    successful_rud_response_test,
    not_found_response_test,
    bad_request_test,
)

import json

import random

client = TestClient(app)


def _random_product():
    """
    Generate a JSON string representing a random product with various attributes.

    Returns:
        str: A JSON-formatted string containing randomly generated product data, including
            name, brand, price, type, quantity, description, hidden status, and optionally a barcode.
    """
    temp_store_id = random.choice(client.get("/api/v1/stores/").json()["data"])["id"]
    return json.dumps(
        {
            "name": random_string(),
            "brand": random_string(max_len=30),
            "price": random_money(),
            "type": random.randint(1, 255),
            "quantity": random.randint(1, 10000),
            "desc": random_string(max_len=512),
            "hidden": random.choice((True, False)),
            "barcode": random_string(64, 128) if random.choice((True, False)) else None,
            "store_id": temp_store_id,
        }
    )


def test_get_all_products():
    response = client.get("/api/v1/products/")
    assert response.status_code == 200

    schema_test(response.json(), GetAllProductsResponse)


def test_get_all_products_including_anonymized():
    response = client.get("/api/v1/products/?include_anonymized=true")
    assert response.status_code == 200
    schema_test(response.json(), GetAllProductsResponse)


def test_create_product():
    product = _random_product()
    response = client.post("/api/v1/products/", data=product)
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


def test_update_product():
    id = random.choice(get_json("/api/v1/products/", client)["data"])["id"]
    product = _random_product()
    response = client.put(f"/api/v1/products/{id}", data=product)
    successful_rud_response_test(response)


def test_delete_product():
    id = random.choice(get_json("/api/v1/products/", client)["data"])["id"]
    response = client.delete(f"/api/v1/products/{id}")
    successful_rud_response_test(response)


def test_get_not_existing_product():
    all_products = (get_json("/api/v1/products/", client))["data"]
    invalid_id = len(all_products) + 1
    response = client.get(f"/api/v1/products/{invalid_id}")
    assert response.status_code == 404

    not_found_response_test(response)


def test_product_create_data_hidden_none():
    product = json.loads(_random_product())
    product["hidden"] = None
    response = client.post("/api/v1/products/", data=json.dumps(product))
    successful_post_response_test(response)


def test_product_create_deleted_product():
    product = json.loads(_random_product())
    product["name"] = "Deleted Product"
    response = client.post("/api/v1/products/", data=json.dumps(product))
    bad_request_test(response)


def test_product_update_data_hidden_none():
    id = random.choice(get_json("/api/v1/products/", client)["data"])["id"]
    product = json.loads(_random_product())
    product["hidden"] = None
    response = client.put(f"/api/v1/products/{id}", data=json.dumps(product))
    successful_rud_response_test(response)
