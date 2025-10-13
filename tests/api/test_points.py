import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.points import PointsRead, GetAllPointsResponse, GetUserPointsResponse

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


def test_get_all_points():
    response = client.get("/api/v1/points/")
    assert response.status_code == 200

    schema_test(response.json(), GetAllPointsResponse)


def test_get_user_points():

    all_points = get_json("/api/v1/points/", client)["data"]
    random_point = random.choice(all_points)

    store_id = random_point["store_id"]
    user_id = random_point["user_id"]

    response = client.get(f"/api/v1/points/store/{store_id}?user_id={user_id}")
    assert response.status_code == 200

    schema_test(response.json(), GetUserPointsResponse)


def test_buy_with_points():

    all_points = get_json("/api/v1/points/", client)["data"]
    all_products = get_json("/api/v1/products/", client)["data"]

    random_product = None
    for product in all_products:
        if product["points_price"] != None:
            random_product = product
            break
    if random_product is None:
        pytest.skip("No hay productos comprables con puntos")

    user_points = None
    for point in all_points:
        if (point["store_id"] == random_product["store_id"]) and (
            point["amount"] > random_product["points_price"]
        ):
            user_points = point
            break
    if not user_points:
        pytest.skip("No hay usuarios con suficientes puntos para comprar esto")

    user_id = user_points["user_id"]

    response = client.post(
        f"/api/v1/points/product/{random_product["id"]}?user_id={user_id}"
    )

    successful_post_response_test(response)
