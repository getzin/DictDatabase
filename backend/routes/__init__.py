from backend.routes.user_routes import router as user_router
from backend.routes.profile_routes import router as profile_router
from backend.routes.search_routes import router as search_router

routers = [user_router, profile_router, search_router]