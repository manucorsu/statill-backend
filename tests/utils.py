import pydantic


def generate_json_schema(pydantic_model: pydantic.BaseModel):
    return pydantic.json_schema.model_json_schema(pydantic_model)
