import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.points import PointsRead, GetAllPointsResponse, GetUserPointsResponse
from .test_stores import random_store
from .test_products import random_product
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

def random_sale():
    random_store = random.choice(get_json("/api/v1/stores/", client)["data"])
    random_user = random.choice(get_json("/api/v1/users/", client)["data"])
    products_list = []

    for product in get_json("/api/v1/products/", client)["data"]:
        if product["store_id"] == random_store["id"] and product["quantity"] > 0:
            products_list.append(product)

    products_in_sale = []

    for i in range(random.randint(0, len(products_list))):
        products_in_sale.append(products_list[i])

    return {
        "store_id": random_store["id"],
        "products": products_in_sale,
        "payment_method": random.randint(1, 3),
        "user_id": random_user["id"]
    }

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

def test_gain_points_from_purchase():
    rand_sale = random_sale()
    rand_sale["products"] = []
    response = client.post("/api/v1/sales/", data=json.dumps(rand_sale))
    bad_request_test(response)

def test_buy_with_points_pointless_store():
    all_stores = get_json("/api/v1/stores/", client)["data"]
    all_users = get_json("/api/v1/users/", client)["data"]

    pointless_store = None
    for store in all_stores:
        if store["ps_value"] == None or store["ps_value"] <= 0:
            pointless_store = store

    store_products = get_json(f"/api/v1/products/store/{pointless_store['id']}", client)["data"]
    random_user = random.choice(all_users)

    response = client.post(f"/api/v1/points/product/{random.choice(store_products)['id']}?user_id={random_user['id']}")
    bad_request_test(response)

def test_buy_with_points_pointless_product():
    all_stores = get_json("/api/v1/stores/", client)["data"]

    chosen_store = None
    for store in all_stores:
        if store["ps_value"] != None and store["ps_value"] > 0:
            chosen_store = store

    store_products = get_json(f"/api/v1/products/store/{chosen_store['id']}", client)["data"]

    pointless_product = None
    for product in store_products:
        if product["points_price"] == None or product["points_price"] <= 0:
            pointless_product = product

    store_points = get_json(f"/api/v1/points/store/{chosen_store['id']}/all", client)["data"]

    if not store_points:
        pytest.skip("No hay usuarios que compraron en esta tienda")

    chosen_user = random.choice(store_points)["user_id"]

    response = client.post(f"/api/v1/points/product/{pointless_product['id']}?user_id={chosen_user}")
    bad_request_test(response)

def test_buy_with_points_guaranteed():
    r_store = random_store()
    r_store["ps_value"] = random.randint(1, 100000)
    new_store_id = (client.post(f"/api/v1/stores", data=json.dumps(r_store)).json())["data"]["id"]

    r_product = random_product()
    r_product["store_id"] = new_store_id
    new_product_id = (client.post(f"/api/v1/products", data=json.dumps(r_product)).json())["data"]["id"]
    
    r_sale = random_sale  ()
    r_sale["products"] = [{
        "product_id": new_product_id,
        "quantity": 1
    }]
    client.post("/api/v1/sales", data=json.dumps(r_sale))

    store_products = get_json(f"/api/v1/products/store/{new_store_id}", client)["data"]

    pointless_product = None
    for product in store_products:
        if product["points_price"] == None or product["points_price"] <= 0:
            pointless_product = product

    store_points = get_json(f"/api/v1/points/store/{new_store_id}/all", client)["data"]

    if not store_points:
        pytest.skip("No hay usuarios que compraron en esta tienda")

    chosen_user = random.choice(store_points)["user_id"]

    response = client.post(f"/api/v1/points/product/{pointless_product['id']}?user_id={chosen_user}")
    bad_request_test(response)