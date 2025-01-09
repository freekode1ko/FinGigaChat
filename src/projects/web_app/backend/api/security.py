from fastapi import Response
from constants import constants


def set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=constants.JWT_TOKEN_NAME,
        value=token,
        httponly=True,
        secure=True,
        expires=constants.JWT_TOKEN_EXPIRE,
    )
    response.set_cookie(
        key=constants.AUTH_TOKEN_NAME,
        value="true",
        expires=constants.JWT_TOKEN_EXPIRE,
    )
