import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.user import GetAllUsersResponse, GetUserResponse

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


def _random_user():
    """
    Generate a JSON string representing a random user with various attributes.

    Returns:
        dict[str, Any]: A JSON-formatted string containing randomly generated user data, including
            name, brand, price, type, quantity, description, hidden status, and optionally a barcode.
    """
    temp_store_id = random.choice(client.get("/api/v1/stores/").json()["data"])["id"]

    return {
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


def test_get_all_users():
    response = client.get("/api/v1/users/")
    assert response.status_code == 200

    schema_test(response.json(), GetAllUsersResponse)


def test_get_user():
    all_users = (get_json("/api/v1/users/", client))["data"]
    if all_users == []:
        raise ValueError(
            "For test_get_product to work there needs to be at least one GETtable user in the database."
        )
    random_user = random.choice(all_users)
    response = client.get(f"/api/v1/users/{random_user['id']}")
    assert response.status_code == 200

    schema_test(response.json(), GetUserResponse)


# def test_create_user():
#     user = _random_product()
#     response = client.post("/api/v1/products/", data=json.dumps(product))
#     successful_post_response_test(response)
