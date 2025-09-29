import pytest, string

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

def _random_email():
    """Generates a syntactically valid random email address."""
    
    # Generate a random string for the local part (username)
    local_part_length = random.randint(5, 15)  # Random length between 5 and 15
    local_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=local_part_length))

    # Choose a common domain
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
    domain = random.choice(domains)

    return f"{local_part}@{domain}"

def _random_date():
    year = random.randint(1000, 9999)
    month = random.randint(10, 12)
    day = random.randint(10, 28 if month == 2 else 30)
    return f"{year}-{month}-{day}"

def random_user():
    return {
        "first_names": random_string(max_len=39),
        "last_name": random_string(max_len=49),
        "email": _random_email(),
        "password": random_string(),
        "birthdate": _random_date(),
        "gender": random.choice(("M", "F", "X")),
        "res_area": random_string(max_len=49)
    }

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
