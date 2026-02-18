from fastapi import APIRouter

from app.api.v1.endpoints import products, categories, suppliers

api_router = APIRouter()

api_router.include_router(
    products.router,
    prefix="/products",
    tags=["products"]
)

api_router.include_router(
    categories.router,
    prefix="/categories",
    tags=["categories"]
)

api_router.include_router(
    suppliers.router,
    prefix="/suppliers",
    tags=["suppliers"]
)