from http import HTTPStatus

from fastapi import Request
from fastapi.responses import JSONResponse


class DomainException(Exception):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(message)


RFCHEADER = {"Content-Type": "application/problem+json"}


def init_exception_handlers(app):
    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException):
        return JSONResponse(
            status_code=exc.status_code,
            headers=RFCHEADER
            if exc.status_code != 401
            else RFCHEADER | {"WWW-Authenticate": "Bearer"},
            content={
                # "type":"about:blank",
                "title": HTTPStatus(exc.status_code).phrase,
                "status": exc.status_code,
                "detail": exc.message,
                "instance": str(request.url),
            },
        )
