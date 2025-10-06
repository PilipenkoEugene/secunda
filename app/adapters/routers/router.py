from fastapi import APIRouter
from app.adapters.routers import organizations, buildings, activities

router = APIRouter(prefix='/secunda')

router.include_router(organizations.router)
router.include_router(buildings.router)
router.include_router(activities.router)