from fastapi import FastAPI
from .routes.auth import router as auth_router
from .routes.comments import router as comments_router
from .routes.posts import router as posts_router
from .routes.user import router as user_router

app = FastAPI()


app.include_router(router=auth_router, prefix="/auth", tags=["Auth"])
app.include_router(router=comments_router, prefix="/comment", tags=["Comments"])
app.include_router(router=posts_router, prefix="/posts", tags=["Posts"])
app.include_router(router=user_router, prefix="/users", tags=["Users"])
