import pydantic
import fastapi.testclient
from typing import Any
import jsonschema
import pytest


def generate_json_schema(pydantic_model: pydantic.BaseModel):
    """
    Generate a JSON Schema from a given Pydantic model.

    Args:
        pydantic_model (pydantic.BaseModel): The Pydantic model class to generate the schema from.

    Returns:
        dict: A dictionary representing the JSON Schema for the provided model.
    """
    return pydantic.json_schema.model_json_schema(pydantic_model)


def get_json(url: str, client: fastapi.testclient.TestClient):
    """
    Send a GET request to a given URL using a FastAPI TestClient and return the response JSON.

    Args:
        url (str): The endpoint URL to request.
        client (fastapi.testclient.TestClient): The FastAPI TestClient instance to send the request with.

    Returns:
        Any: Parsed JSON response from the endpoint.
    """
    response = client.get(url)
    return response.json()


def schema_test(instance: Any, schema: dict[str, Any] | pydantic.BaseModel):
    """
    Validate a JSON instance against a given schema or Pydantic model,
    `pytest.fail`ing the test if validation fails.

    If a Pydantic model is provided, it will be converted to a JSONSchema
    dictionary before validation.

    Args:
        instance (Any): The JSON-like object (dict, list, etc.) to validate.
        schema (dict[str, Any] | pydantic.BaseModel): The JSON Schema as a dictionary
            or a Pydantic model to validate against.

    Returns:
        None

    Raises:
        pytest.fail: If the instance does not match the schema, a test failure is triggered.
    """
    if isinstance(schema, pydantic.BaseModel):
        schema = generate_json_schema(schema)

    try:
        jsonschema.validate(instance, schema)
    except jsonschema.ValidationError as ex:
        pytest.fail(f"Response did not match expected schema, {ex}")
