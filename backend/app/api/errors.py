"""统一错误处理"""
from fastapi import Request, HTTPException, status
from pydantic import BaseModel
from app.api.errors import ErrorResponse, NotFoundError, BusinessErrorResponse


async def not_found(resource: str) -> None:
    raise NotFoundError(
        detail=f"{resource} not found"
    )


async def business_error(message: str) -> None:
    raise BusinessErrorResponse(
        detail=message
    )


async def validation_error(message: str) -> None:
    raise ErrorResponse(
        code="VALIDATION_ERROR",
        message=message
    )


async def database_error(message: str) -> None:
    raise ErrorResponse(
        code="DATABASE_ERROR",
        message=message
    )


def format_error_response(
    exception: Exception
) -> dict:
    from fastapi import status
    if isinstance(exception, HTTPException):
        return {
            "code": exception.status_code,
            "message": exception.detail
        }
    else:
        return {
            "code": 500,
            "message": str(exception)
        }