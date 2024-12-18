from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

from exceptions import ApplicationError, InfrastructureError


async def _handle_application_error(_, error: ApplicationError) -> JSONResponse:
    return JSONResponse(content={"detail": str(error)}, status_code=status.HTTP_400_BAD_REQUEST)


async def _handle_infrastructure_error(_, error: InfrastructureError) -> JSONResponse:
    return JSONResponse(content={"detail": str(error)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


def set_exception_handlers(app: FastAPI) -> None:
    """Обработчики кастомных исключений в приложении"""

    app.add_exception_handler(ApplicationError, _handle_application_error)
    app.add_exception_handler(InfrastructureError, _handle_infrastructure_error)
