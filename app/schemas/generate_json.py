GENERATE_JSON_SCHEMAS = False  # set to True only if needed to create postman tests

if GENERATE_JSON_SCHEMAS:
    import json

    from pydantic.json_schema import model_json_schema

    from .product import (
        GetAllProductsResponse,
        GetProductResponse,
    )

    from .sale import (
        GetAllSalesResponse,
        GetSaleResponse,
    )

    from .store import (
        GetAllStoresResponse,
        GetStoreResponse,
    )

    from .user import GetAllUsersResponse, GetUserResponse
    import warnings

    schemas = [
        GetAllProductsResponse,
        GetProductResponse,
        GetAllSalesResponse,
        GetSaleResponse,
        GetAllStoresResponse,
        GetStoreResponse,
        GetAllUsersResponse,
        GetUserResponse,
    ]

    for schema in schemas:
        with open(f"./json/{schema.__name__}.json", "w") as out_file:
            json.dump(model_json_schema(schema, mode="validation"), out_file, indent=2)

    warnings.warn("⚠️   Please remember to set GENERATE_JSON_SCHEMAS to False before pushing, or deploying WILL fail!")
