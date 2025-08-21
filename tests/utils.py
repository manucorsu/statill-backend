import pydantic
import fastapi.testclient
from typing import Any, Literal
import jsonschema
import pytest
import string
import random


def generate_json_schema(pydantic_model: type[pydantic.BaseModel]):
    """
    Generate a JSON Schema from a given Pydantic model.

    Args:
        pydantic_model (type[pydantic.BaseModel]): The Pydantic model class to generate the schema from.

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


def schema_test(instance: Any, schema: dict[str, Any] | type[pydantic.BaseModel]):
    """
    Validate a JSON instance against a given schema or Pydantic model,
    `pytest.fail`ing the test if validation fails.

    If a Pydantic model is provided, it will be converted to a JSONSchema
    dictionary before validation.

    Args:
        instance (Any): The JSON-like object (dict, list, etc.) to validate.
        schema (dict[str, Any] | type[pydantic.BaseModel]): The JSON Schema as a dictionary
            or a Pydantic model to validate against.

    Returns:
        None

    Raises:
        pytest.fail: If the instance does not match the schema, a test failure is triggered.
    """
    if isinstance(schema, type) and issubclass(schema, pydantic.BaseModel):
        schema = generate_json_schema(schema)
    try:
        jsonschema.validate(instance=instance, schema=schema)
    except jsonschema.ValidationError as ex:
        pytest.fail(f"Response did not match expected schema, {ex}")


def random_string(min_len: int = 1, max_len: int = 100):
    if min_len < 1:
        raise ValueError(
            f"Invalid min_len {min_len}: the string must be at least 1 character long"
        )
    characters = (
        string.ascii_letters
        + string.digits
        + string.punctuation
        + " "  # Basic printable
        + "".join(
            chr(c) for c in range(0x00C0, 0x024F + 1)
        )  # Latin-1 Supplement + Latin Extended-A/B
    )

    length = random.randint(min_len, max_len)
    return "".join(random.choice(characters) for _ in range(length))

def random_money(min: int = 0, max: int = 99999999.99):
    decimals: Literal[0, 1, 2] = random.choice([0, 1, 2])
    scale = 10 ** decimals

    randint = random.randint(int(min*scale), int(max*scale))

    return randint / scale