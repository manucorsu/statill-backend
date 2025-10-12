import pytest

from fastapi.testclient import TestClient
from datetime import time

from app.main import app
from .test_users import random_user

client = TestClient(app)

from app.schemas.store import (
    GetAllStoresResponse,
    GetStoreResponse,
    StoreCreate,
    StoreRead,
)

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


def _random_store():
    """
    Generate a dict representing a random store with various attributes.

    Returns:
        dict[str, Any]: A JSON-formatted string containing randomly generated store data, including
            name, category, address, preorder_enabled, ps_value, opening_times, closing_times and payement_methods.
    """
    random_opening_times = []
    random_closing_times = []

    for _ in range(7):
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 58)
        random_opening_times.append(time(hour, minute, second).isoformat())
        random_closing_times.append(time(hour, minute, second + 1).isoformat())

    all_users = get_json_data("/api/v1/users", client)
    unemployed_users = [u for u in all_users if u["store_id"] is None]
    temp_user_id = int(random.choice(unemployed_users)["id"])

    return {
        "name": random_string(1, 60),
        "category": random.randint(1, 255),
        "address": random_string(),
        "preorder_enabled": random.choice((True, False)),
        "ps_value": random.choice((None, random.randint(1, 10000))),
        "opening_times": random_opening_times,
        "closing_times": random_closing_times,
        "payment_methods": [random.choice((False, True)) for _ in range(4)],
        "user_id": temp_user_id,
    }


def test_get_all_stores():
    response = client.get("/api/v1/stores/")
    assert response.status_code == 200

    schema_test(response.json(), GetAllStoresResponse)


def test_get_store():
    all_stores = (get_json("/api/v1/stores/", client))["data"]
    if all_stores == []:
        pytest.skip(
            "For test_get_store to work there needs to be at least one GETtable store in the database."
        )
    random_store = random.choice(all_stores)
    response = client.get(f"/api/v1/stores/{random_store['id']}")
    assert response.status_code == 200

    schema_test(response.json(), GetStoreResponse)


def test_create_store():
    random_user_generate = random_user()
    new_user = (
        client.post("/api/v1/users", data=json.dumps(random_user_generate))
    ).json()
    store = _random_store()
    store["user_id"] = new_user["data"]["id"]
    response = client.post("/api/v1/stores/", data=json.dumps(store))
    if response.status_code != 201:
        assert response.json() == object()
    successful_post_response_test(response)
