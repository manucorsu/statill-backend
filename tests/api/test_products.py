import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.product import GetAllProductsResponse
from ..utils import generate_json_schema

import jsonschema

import random

client = TestClient(app)


def test_get_all_products():
    response = client.get("/api/v1/products/")
    assert response.status_code == 200

    expected_schema = generate_json_schema(GetAllProductsResponse)
    try:
        jsonschema.validate(instance=response.json(), schema=expected_schema)
    except jsonschema.ValidationError as ex:
        pytest.fail(f"Response did not match expected schema, {ex}")


def test_get_product():
    all_products = (client.get("/api/v1/products")).json()

    response = client.get(f"/api/v1/products/{(random.choice(all_products.data)).id}")
