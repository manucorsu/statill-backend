from fastapi.testclient import TestClient
from ..main import app
from jsonschema import validate, ValidationError
from pytest import fail

client = TestClient(app)

product_id = None


def test_get_all_products():
    response = client.get("/api/v1/products/")
    assert response.status_code == 200

    expected_schema = {
        "$defs": {
            "ProductRead": {
                "properties": {
                    "id": {"minimum": 1, "title": "Id", "type": "integer"},
                    "store_id": {"minimum": 1, "title": "Store Id", "type": "integer"},
                    "name": {
                        "minLength": 1,
                        "pattern": "\\S",
                        "title": "Name",
                        "type": "string",
                    },
                    "brand": {
                        "minLength": 1,
                        "pattern": "\\S",
                        "title": "Brand",
                        "type": "string",
                    },
                    "price": {
                        "maximum": 99999999.99,
                        "minimum": 0.01,
                        "title": "Price",
                        "type": "number",
                    },
                    "type": {"minimum": 0, "title": "Type", "type": "integer"},
                    "quantity": {"minimum": 0, "title": "Quantity", "type": "number"},
                    "desc": {
                        "minLength": 1,
                        "pattern": "\\S",
                        "title": "Desc",
                        "type": "string",
                    },
                    "barcode": {
                        "anyOf": [
                            {"minLength": 1, "pattern": "\\S", "type": "string"},
                            {"type": "null"},
                        ],
                        "title": "Barcode",
                    },
                },
                "required": [
                    "id",
                    "store_id",
                    "name",
                    "brand",
                    "price",
                    "type",
                    "quantity",
                    "desc",
                    "barcode",
                ],
                "title": "ProductRead",
                "type": "object",
            }
        },
        "properties": {
            "successful": {"const": True, "title": "Successful", "type": "boolean"},
            "data": {
                "items": {"$ref": "#/$defs/ProductRead"},
                "title": "Data",
                "type": "array",
            },
            "message": {
                "minLength": 1,
                "pattern": "\\S",
                "title": "Message",
                "type": "string",
            },
        },
        "required": ["successful", "data", "message"],
        "title": "GetAllProductsResponse",
        "type": "object",
    }
    try:
        validate(instance=response.json(), schema=expected_schema)
    except ValidationError as ex:
        fail(f"Response does not match schema {ex}")


def test_post_product():
    product = {
        "name": "SimCity 4 Deluxe",
        "brand": "EA-Maxis",
        "price": 7600,
        "quantity": 16000000,
        "desc": "SimCity es un juego donde simulás una city",
        "barcode": "AB010AF889199900AAFF",
        "store_id": 2,
    }
    response = client.post("/api/v1/products", json=product)

    assert response.status_code == 201
