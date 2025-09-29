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
    get_json_data,
)

import json

import random

client = TestClient(app)


def test_get_all_users():
    response = client.get("/api/v1/users/")
    assert response.status_code == 200

    schema_test(response.json(), GetAllUsersResponse)


def test_get_user():
    all_users = (get_json("/api/v1/users/", client))["data"]
    if all_users == []:
        pytest.skip(
            "For test_get_user to work there needs to be at least one GETtable user in the database."
        )
    random_user = random.choice(all_users)
    response = client.get(f"/api/v1/users/{random_user['id']}")
    assert response.status_code == 200

    schema_test(response.json(), GetUserResponse)


def test_get_user_by_store_id():
    random_store_id = random.choice(get_json_data("/api/v1/stores", client))["id"]
    response = client.get(f"/api/v1/users/store/{random_store_id}")
    assert response.status_code == 200

    schema_test(response.json(), GetAllUsersResponse)


# def test_create_user():
#     user = _random_product()
#     response = client.post("/api/v1/products/", data=json.dumps(product))
#     successful_post_response_test(response)
