import json
from http import HTTPStatus

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class DomainException(Exception):
    def __init__(self, title: str, status_code: int, message: str):
        self.title = title
        self.status_code = status_code
        self.message = message
        super().__init__(message)


class ValidationErrorDetail(BaseModel):
    name: str
    reason: str


class ProblemDetails(BaseModel):
    title: str
    status: int
    detail: str | None = None
    instance: str | None = None
    errors: list[ValidationErrorDetail] | None = None


RFCHEADER = {"Content-Type": "application/problem+json"}

ERROR_EXAMPLES = {
    401: {
        "value": {
            "title": "Authentication Error",
            "status": 401,
            "detail": "Could not validate credentials.",
            "instance": "/episodes/12345/logs",
        },
    },
    404: {
        "value": {
            "title": "Show Not Found",
            "status": 404,
            "detail": "Show with ID 12345 not found.",
            "instance": "/shows/12345",
        }
    },
    422: {
        "value": {
            "title": "Validation Error",
            "status": 422,
            "detail": "The request payload contains validation errors.",
            "instance": "/users/12345",
            "invalid-params": [
                {
                    "name": "username",
                    "reason": "String should have at least 3 characters.",
                }
            ],
        },
    },
    500: {
        "value": {
            "title": "Internal Server Error",
            "status": 500,
            "detail": "An unexpected error occurred.",
            "instance": "/users/me",
        },
    },
    502: {
        "value": {
            "title": "TMDB Client Error",
            "status": 502,
            "detail": "The TMDB API encountered an error and could not fulfill the request.",
            "instance": "/shows/12345",
        },
    },
    503: {
        "value": {
            "title": "TMDB Client Error",
            "status": 503,
            "detail": "The TMDB API is currently unavailable. Please try again later.",
            "instance": "/seasons/12345",
        },
    },
    504: {
        "value": {
            "title": "TMDB Client Error",
            "status": 504,
            "detail": "The TMDB API request timed out. Please try again later.",
            "instance": "/episodes/12345",
        },
    },
}


def init_exception_handlers(app):
    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException):
        return JSONResponse(
            status_code=exc.status_code,
            headers=RFCHEADER
            if exc.status_code != 401
            else RFCHEADER | {"WWW-Authenticate": "Bearer"},
            content={
                "title": exc.title,
                "status": exc.status_code,
                "detail": exc.message,
                "instance": str(request.url.path),
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        errors = exc.errors()

        error_messages = []
        for error in errors:
            error_messages.append(
                {
                    'name': f"{str(error['loc'][-1])}",
                    'reason': f"{error['msg']}".split(' ', 1)[-1].capitalize(),
                }
            )

        return JSONResponse(
            status_code=422,
            headers=RFCHEADER,
            content={
                "title": "Validation Error",
                "status": 422,
                "detail": "The request payload contains validation errors.",
                "instance": str(request.url.path),
                "invalid-params": error_messages,
            },
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            headers=RFCHEADER,
            content={
                "title": "Internal Server Error",
                "status": 500,
                "detail": "An unexpected error occurred.",
                "instance": str(request.url.path),
            },
        )

    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = FastAPI.openapi(app)

        if "components" not in openapi_schema:
            openapi_schema['components'] = {}
        if "schemas" not in openapi_schema['components']:
            openapi_schema['components']['schemas'] = {}

        problem_detail_schema = ProblemDetails.model_json_schema()

        if "$defs" in problem_detail_schema:
            for sub_model_name, sub_model_schema in problem_detail_schema[
                "$defs"
            ].items():
                openapi_schema['components']['schemas'][sub_model_name] = (
                    sub_model_schema
                )
            del problem_detail_schema["$defs"]

        openapi_schema['components']['schemas']['ProblemDetails'] = (
            problem_detail_schema
        )

        schema_json_str = json.dumps(openapi_schema)

        schema_json_str = schema_json_str.replace("#/$defs/", "#/components/schemas/")

        openapi_schema = json.loads(schema_json_str)

        for path, methods in openapi_schema.get("paths", {}).items():
            for _, operation in methods.items():
                if path in ["/openapi.json", "/docs", "/redoc"]:
                    continue

                responses = operation.get("responses", {})

                for code in list(responses.keys()):
                    try:
                        int_code = int(code)
                    except ValueError:
                        continue

                    if int_code in ERROR_EXAMPLES:
                        example_data = ERROR_EXAMPLES[int_code]

                        title = HTTPStatus(int_code).phrase

                        responses[code] = {
                            "description": HTTPStatus(int_code).phrase,
                            "content": {
                                "application/problem+json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ProblemDetails"
                                    },
                                    "examples": {
                                        f"err_{code}": {
                                            "summary": title,
                                            "value": example_data["value"],
                                        }
                                    },
                                }
                            },
                        }

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi
