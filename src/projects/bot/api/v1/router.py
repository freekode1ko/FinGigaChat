from fastapi import APIRouter

from api.v1.testing.router import router as testing_router


router = APIRouter()

router.include_router(testing_router, prefix='/test')
