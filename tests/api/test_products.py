import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.product import GetAllProductsResponse, GetProductResponse
from ..utils import get_json, schema_test, random_string

import jsonschema

import random

client = TestClient(app)

def _random_product():
    return {
        "name": random_string(),
        "brand": random_string(),
    }

def test_get_all_products():
    response = client.get("/api/v1/products/")
    assert response.status_code == 200

    schema_test(response.json(), GetAllProductsResponse)


def test_get_product():
    all_products = get_json("/api/v1/products/", client)

    random_product = random.choice(all_products["data"])
    response = client.get(f"/api/v1/products/{random_product['id']}")
    assert response.status_code == 200

    schema_test(response.json(), GetProductResponse)
