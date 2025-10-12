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
from .test_users import (
    leading_zero_md,
    leading_zero_y,
    is_leap_year,
    random_day_of_month,
)

import random

import json

from typing import Literal

from datetime import date, timedelta

client = TestClient(app)


def _random_discount():
    all_products = get_json_data("/api/v1/products", client)
    today = date.today()
    year = random.randint(today.year, 9999)
    month = random.randint(today.month if year == today.year else 1, 12)
    day = random_day_of_month(
        year, month, min_day=today.day if year == today.year else 1
    )
    min_amount = random.randint(1, 100)
    max_amount = random.randint(min_amount, 200)
    days_usable = [random.choice((False, True)) for _ in range(6)]
    days_usable.append(True)

    return {
        "product_id": random.choice(all_products)["id"],
        "pct_off": random.randint(1, 100),
        "start_date": f"{leading_zero_y(year)}-{leading_zero_md(month)}-{leading_zero_md(day)}",
        "end_date": f"{leading_zero_y(year)}-{leading_zero_md(month)}-{leading_zero_md(day + 1)}",
        "days_usable": days_usable,
        "min_amount": min_amount,
        "max_amount": max_amount,
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
    schema_test(response.json(), GetDiscountResponse)


def test_get_discount_by_product_id_allownull():
    all_discounts = get_json_data("/api/v1/discounts", client)
    if len(all_discounts) == 0:
        pytest.skip("There are no discounts.")

    random_product_id = random.choice(all_discounts)["product_id"]

    response = client.get(f"/api/v1/discounts/product/{random_product_id}/allownull")
    schema_test(response.json(), GetDiscountResponse)


def test_create_discount():
    discount = _random_discount()
    response = client.post("/api/v1/discounts/", data=json.dumps(discount))
    if response.status_code != 201:
        assert response.json() == object()
    successful_post_response_test(response)


def test_create_discount_past_date():
    yesterday = date.today() - timedelta(days=1)
    discount = _random_discount()
    discount["start_date"] = (
        f"{leading_zero_y(yesterday.year)}-{leading_zero_md(yesterday.month)}-{leading_zero_md(yesterday.day)}"
    )
    response = client.post("/api/v1/discounts/", data=json.dumps(discount))
    bad_request_test(response)


def test_create_discount_end_before_start():
    today = date.today()
    yesterday = date.today() - timedelta(days=1)

    discount = _random_discount()
    discount["start_date"] = (
        f"{leading_zero_y(today.year)}-{leading_zero_md(today.month)}-{leading_zero_md(today.day)}"
    )
    discount["end_date"] = (
        f"{leading_zero_y(yesterday.year)}-{leading_zero_md(yesterday.month)}-{leading_zero_md(yesterday.day)}"
    )
    response = client.post("/api/v1/discounts/", data=json.dumps(discount))
    bad_request_test(response)


def test_create_discount_invalid_start_date():
    discount = _random_discount()
    discount["start_date"] = "Hola"
    response = client.post("/api/v1/discounts/", data=json.dumps(discount))
    bad_request_test(response)


def test_create_discount_invalid_end_date():
    discount = _random_discount()
    discount["end_date"] = "Hola"
    response = client.post("/api/v1/discounts/", data=json.dumps(discount))
    bad_request_test(response)


def test_create_discount_minamount_larger_than_maxamount():
    discount = _random_discount()
    discount["min_amount"] = 5
    discount["max_amount"] = 4
    response = client.post("/api/v1/discounts/", data=json.dumps(discount))
    bad_request_test(response)


def test_create_discount_no_usable_days():
    discount = _random_discount()
    discount["days_usable"] = [False, False, False, False, False, False, False]
    response = client.post("/api/v1/discounts/", data=json.dumps(discount))
    bad_request_test(response)


def test_get_invalid_discount():
    all_discounts = get_json_data("/api/v1/discounts", client)
    invalid_id: int = 1
    while invalid_id in [d["id"] for d in all_discounts]:
        invalid_id += 1
    response = client.get(f"/api/v1/discounts/{invalid_id}")
    assert response.status_code == 404

    not_found_response_test(response)


def test_get_invalid_discount_by_product_id():
    all_discounts = get_json_data("/api/v1/discounts", client)
    all_products = get_json_data("/api/v1/products", client)

    discounted_product_ids = {d["product_id"] for d in all_discounts}
    products_without_discounts = [
        p for p in all_products if p["id"] not in discounted_product_ids
    ]

    if len(all_discounts) == 0:
        pytest.skip("There are no discounts.")

    random_product_id = random.choice(products_without_discounts)["id"]

    response = client.get(f"/api/v1/discounts/product/{random_product_id}")
    not_found_response_test(response)


def test_create_existing_discount():
    all_discounts = get_json_data("/api/v1/discounts", client)

    discount = _random_discount()
    discount["product_id"] = random.choice(all_discounts)["product_id"]
    response = client.post("/api/v1/discounts/", data=json.dumps(discount))
    if response.status_code != 201:
        assert response.json() == object()
    successful_post_response_test(response)
