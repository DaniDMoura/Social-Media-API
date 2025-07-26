from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.auth import router as auth_router
from .routes.comments import router as comments_router
from .routes.posts import router as posts_router
from .routes.user import router as user_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware(
        allow_origins=["localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
)

app.include_router(router=auth_router, prefix="/auth", tags=["Auth"])
app.include_router(router=comments_router, prefix="/comment", tags=["Comments"])
app.include_router(router=posts_router, prefix="/posts", tags=["Posts"])
app.include_router(router=user_router, prefix="/users", tags=["Users"])
