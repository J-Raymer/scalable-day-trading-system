from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        content={"success": False, "data": exc.detail},
        status_code=exc.status_code)

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"success": False, "data": "Invalid Payload"})
