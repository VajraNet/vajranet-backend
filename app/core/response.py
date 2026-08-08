from typing import Any, Optional, Generic, TypeVar
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi import status

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    success: bool
    data: Optional[T] = None
    message: str


def success_response(data: Any = None, message: str = "Operation completed successfully", status_code: int = status.HTTP_200_OK) -> JSONResponse:
    """Helper to return consistent JSON success responses."""
    # If data is a Pydantic model, convert to dict
    serialized_data = data
    if hasattr(data, "model_dump"):
        serialized_data = data.model_dump(mode="json")
    elif isinstance(data, list):
        serialized_data = [
            item.model_dump(mode="json") if hasattr(item, "model_dump") else item
            for item in data
        ]
    
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "data": serialized_data,
            "message": message,
        }
    )


def error_response(message: str = "An error occurred", status_code: int = status.HTTP_400_BAD_REQUEST, data: Any = None) -> JSONResponse:
    """Helper to return consistent JSON error responses."""
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "data": data,
            "message": message,
        }
    )
