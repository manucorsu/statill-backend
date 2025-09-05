from __future__ import annotations
from typing import Any, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    import fastapi.testclient
    import httpx

import pydantic
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


def get_json_data(url: str, client: fastapi.testclient.TestClient):
    rjson = get_json(url, client)
    return rjson["data"]


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
    """
    Generate a random string of a specified length range.
    The generated string includes ASCII letters, digits, punctuation, spaces,
    and Latin-1 Supplement and Latin Extended-A/B Unicode characters.
    Args:
        min_len (int): Minimum length of the generated string (inclusive, default is 1).
        max_len (int): Maximum length of the generated string (inclusive, default is 100).
    Returns:
        str: A randomly generated string of length between min_len and max_len.
    Raises:
        ValueError: If min_len is less than 1.
        ValueError: If min_len is greater than max_len.
    """
    if min_len < 1:
        raise ValueError(
            f"Invalid min_len {min_len}: the string must be at least 1 character long"
        )
    if min_len > max_len:
        raise ValueError(
            f"Invalid min_len {min_len} and max_len {max_len}: min_len must be <= max_len"
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


def random_money(min: float = 0.01, max: float = 99999999.99):
    """
    Generate a random monetary value within a specified range, with a random number of decimal places (0, 1, or 2).
    Args:
        min (float, optional): The minimum value (inclusive). Must be >= 0. Defaults to 0.01.
        max (float, optional): The maximum value (inclusive). Must be > min. Defaults to 99999999.99.
    Returns:
        float: A random monetary value between min and max, rounded to 0, 1, or 2 decimal places.
    Raises:
        ValueError: If min is less than 0.
        ValueError: If max is less than or equal to min.
    """
    if min < 0:
        raise ValueError(f"Invalid min {min}: must be >= 0")
    if max <= min:
        raise ValueError(f"Invalid max {max}: must be > min {min}")

    decimals: Literal[0, 1, 2] = random.choice([0, 1, 2])
    scale = 10**decimals

    randint = random.randint(int(min * scale), int(max * scale))

    return randint / scale


def successful_post_response_test(response: httpx.Response):
    """
    Asserts that the given HTTPX response object represents a successful POST request.

    Checks that:
    - The response status code is 201 (Created).
    - The JSON response contains a "successful" field set to True.
    - The "data" field contains an "id" of type int.
    - The "message" field is a string.

    Args:
        response (httpx.Response): The HTTPX response object to test.

    Raises:
        AssertionError: If any of the assertions fail.
    """
    assert response.status_code == 201
    json_response = response.json()
    assert json_response["successful"]
    assert isinstance(json_response["data"]["id"], int)
    assert isinstance(json_response["message"], str)


def successful_rud_response_test(response: httpx.Response):
    assert response.status_code == 200
    jsonr = response.json()
    assert jsonr["successful"]
    assert isinstance(jsonr["message"], str)


def not_found_response_test(response: httpx.Response):
    assert response.status_code == 404
    jsonr = response.json()
    assert not jsonr["successful"]
    assert isinstance(jsonr["message"], str)


def bad_request_test(response: httpx.Response, code: int = 400):
    assert response.status_code == code
    jsonr = response.json()
    assert not jsonr["successful"]
    assert isinstance(jsonr["message"], str)
