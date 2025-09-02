import pytest

from fastapi.testclient import TestClient

from app.main import app
from ..utils import schema_test
from app.schemas.order import GetAllOrdersResponse

import random

client = TestClient(app)


# def _random_order():
#     all_products = ((client.get("/api/v1/products/")).json())["data"]
#     store_id = random.choice(client.get("/api/v1/stores/").json()["data"])["id"]


def test_get_all_orders():
    response = client.get("/api/v1/orders/")
    assert response.status_code == 200
    schema_test(response.json(), GetAllOrdersResponse)


# def test_create_order():
#     response = client.post("/api/v1/orders/")
