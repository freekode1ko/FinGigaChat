from fastapi import Response
from fastapi.security import APIKeyCookie
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


get_token = APIKeyCookie(name=constants.JWT_TOKEN_NAME)

# TODO: get_current_user для использования в Depends (?)
