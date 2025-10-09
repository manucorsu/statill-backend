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
from app.schemas.discount import GetAllDiscountsResponse, GetDiscountResponse

import random

import json

from typing import Literal

client = TestClient(app)

def random_discount():
    all_products = get_json_data("/api/v1/products", client)

    return {
        "product_id": random.choice(all_products)["product_id"],
        "pct_off": random.randrange(1, 100)
    }

def test_get_all_discounts():
    response = client.get("/api/v1/discounts/")
    assert response.status_code == 200
    schema_test(response.json(), GetAllDiscountsResponse)

def test_get_discount():
    all_discounts = get_json_data("/api/v1/discounts", client)
    if len(all_discounts) == 0:
        pytest.skip("There are no discounts.")

    id = random.choice(all_discounts)["id"]
    response = client.get(f"/api/v1/discounts/{id}")
    schema_test(response.json(), GetDiscountResponse)

def test_get_discount_by_product_id():
    all_discounts = get_json_data("/api/v1/discounts", client)
    if len(all_discounts) == 0:
        pytest.skip("There are no discounts.")

    random_product_id = random.choice(all_discounts)["product_id"]
    
    response = client.get(f"/api/v1/discounts/product/{random_product_id}")
    schema_test(response.json(), GetAllDiscountsResponse)

def test_get_discount_by_product_id():
    all_discounts = get_json_data("/api/v1/discounts", client)
    if len(all_discounts) == 0:
        pytest.skip("There are no discounts.")

    random_product_id = random.choice(all_discounts)["product_id"]
    
    response = client.get(f"/api/v1/discounts/product/{random_product_id}/allownull")
    schema_test(response.json(), GetAllDiscountsResponse)

def test_create_discount():

