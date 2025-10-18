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
        f"/api/v1/points/product/{random_product['id']}?user_id={user_id}"
    )

    assert response.status_code == 201
    json_response = response.json()
    assert json_response["successful"]


def test_get_user_points_invalid_ps_value():
    all_points = get_json("/api/v1/points/", client)["data"]
    all_stores = get_json("/api/v1/stores/", client)["data"]

    invalid_store = None
    for store in all_stores:
        if store["ps_value"] == None or store["ps_value"] <= 0:
            invalid_store = store
            break

    if not invalid_store:
        pytest.skip("No hay stores sin sistema de puntos")

    random_point = random.choice(all_points)

    store_id = invalid_store["id"]
    user_id = random_point["user_id"]

    response = client.get(f"/api/v1/points/store/{store_id}?user_id={user_id}")
    bad_request_test(response)


def test_get_user_points_pointless_user():
    all_stores = get_json("/api/v1/stores/", client)["data"]
    all_users = get_json("/api/v1/users/", client)["data"]

    random_store = None

    for store in all_stores:
        if store["ps_value"] != None and store['ps_value'] > 0:
            random_store = store["id"]
            break
    all_users_in_store = []

    for points in get_json_data(f"/api/v1/points/store/{random_store}/all", client):
        all_users_in_store.append(points["user_id"])

    invalid_user_id = None
    for user in all_users:
        if user["id"] not in all_users_in_store:
            invalid_user_id = user["id"]
            break

    if not invalid_user_id:
        pytest.skip("No hay usuarios que no tengan puntos en esta tienda")

    response = client.get(
        f"/api/v1/points/store/{random_store}?user_id={invalid_user_id}"
    )
    not_found_response_test(response)

def test_buy_with_points_not_points_enabled():
    all_products = get_json("/api/v1/products/", client)["data"]
    all_users = get_json("/api/v1/users/", client)["data"]
    all_stores = get_json("/api/v1/stores/", client)["data"]

    random_user = random.choice(all_users)

    pointless_store = None
    for store in all_stores:
        if (store["ps_value"] != None and store["ps_value"] <= 0) or store["ps_value"] == None:
            pointless_store = store["id"]
            break

    random_product = None
    for product in all_products:
        if product["store_id"] == pointless_store:
            random_product = product
            break

    response = client.post(
        f"/api/v1/points/product/{random_product['id']}?user_id={random_user["id"]}"
    )

    bad_request_test(response)

def test_buy_with_not_enough_points():
    all_products = get_json("/api/v1/products/", client)["data"]
    all_stores = get_json("/api/v1/stores/", client)["data"]

    random_store = None
    for store in all_stores:
        if store["ps_value"] != None and store["ps_value"] > 0:
            random_store = store["id"]
            break

    random_product = None
    for product in all_products:
        if product["store_id"] == random_store:
            random_product = product
            break

    broke_user = None
    for points in get_json_data(f"/api/v1/points/store/{random_store}/all", client):
        if(points["amount"] < random_product["points_price"]):
            broke_user = points["user_id"]

    if broke_user == None:
        pytest.skip("Todos los usuarios tienen suficiente plata")

    response = client.post(
        f"/api/v1/points/product/{random_product['id']}?user_id={broke_user}"
    )

    bad_request_test(response)


