from fastapi import HTTPException, status


class APIError(HTTPException):
    def __init__(self, status_code: int, code: str, message: str) -> None:
        super().__init__(
            status_code=status_code,
            detail={"error": {"code": code, "message": message}},
        )


def not_found(code: str, message: str) -> APIError:
    return APIError(status.HTTP_404_NOT_FOUND, code, message)


def bad_request(code: str, message: str) -> APIError:
    return APIError(status.HTTP_400_BAD_REQUEST, code, message)


def unprocessable(code: str, message: str) -> APIError:
    return APIError(status.HTTP_422_UNPROCESSABLE_ENTITY, code, message)


def conflict(code: str, message: str) -> APIError:
    return APIError(status.HTTP_409_CONFLICT, code, message)
