from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import User, Post, Comment, Like
from app.security import get_current_user
from app.database import get_session
from app.schemas import (
    CreatePost,
    ListComments,
    ListLikes,
    ListPostsFeed,
    Posts,
    DeletePost,
    ListComment,
    ListLike,
    Unlike,
)


router = APIRouter()


@router.post("/", status_code=HTTPStatus.CREATED, response_model=Posts)
async def create_post(
    post: CreatePost,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    new_post = Post(
        description=post.description, image_url=post.image_url, user_id=user.id
    )

    session.add(new_post)
    await session.commit()
    await session.refresh(new_post)

    return new_post


@router.get("/", status_code=HTTPStatus.OK, response_model=ListPostsFeed)
async def get_posts(
    offset: int = 0, limit: int = 10, session: AsyncSession = Depends(get_session)
):
    db_posts = await session.scalars(select(Post).offset(offset).limit(limit))
    posts = db_posts.all()

    if not posts:
        raise HTTPException(detail="No posts found", status_code=HTTPStatus.NOT_FOUND)

    return {"posts": posts}


@router.get("/{post_id}", status_code=HTTPStatus.OK, response_model=Posts)
async def get_post(post_id: int, session: AsyncSession = Depends(get_session)):
    db_post = await session.scalar(select(Post).where(Post.id == post_id))

    if not db_post:
        raise HTTPException(detail="No post found", status_code=HTTPStatus.NOT_FOUND)

    return db_post


@router.put("/{post_id}", status_code=HTTPStatus.OK, response_model=Posts)
async def update_post(
    new_post: CreatePost,
    post_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    db_post = await session.scalar(
        select(Post).where((Post.id == post_id) & (Post.user_id == user.id))
    )

    if not db_post:
        raise HTTPException(
            detail="No posts to update", status_code=HTTPStatus.NOT_FOUND
        )

    db_post.description = new_post.description
    db_post.image_url = new_post.image_url

    await session.commit()
    await session.refresh(db_post)

    return db_post


@router.delete("/{post_id}", status_code=HTTPStatus.OK, response_model=DeletePost)
async def delete_post(
    post_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    db_post = await session.scalar(
        select(Post).where((Post.id == post_id) & (Post.user_id == user.id))
    )

    if not db_post:
        raise HTTPException(
            detail="No posts to delete", status_code=HTTPStatus.NOT_FOUND
        )

    await session.delete(db_post)
    await session.commit()

    return {"detail": "Post deleted"}


@router.post(
    "/{post_id}/comments", status_code=HTTPStatus.CREATED, response_model=ListComment
)
async def comment(
    post_id: int,
    comment: str,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    db_comment = Comment(user_id=user.id, post_id=post_id, comment=comment)

    session.add(db_comment)
    await session.commit()
    await session.refresh(db_comment)

    return db_comment


@router.post(
    "/{post_id}/likes", status_code=HTTPStatus.CREATED, response_model=ListLike
)
async def like(
    post_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    liked_post = await session.scalar(
        select(Like).where((Like.post_id == post_id) & (Like.user_id == user.id))
    )

    if liked_post:
        raise HTTPException(
            detail="You cannot like more than once", status_code=HTTPStatus.BAD_REQUEST
        )

    db_like = Like(post_id=post_id, user_id=user.id)

    session.add(db_like)
    await session.commit()
    await session.refresh(db_like)

    return db_like


@router.delete("/{post_id}/likes", status_code=HTTPStatus.OK, response_model=Unlike)
async def unlike(
    post_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    db_like = await session.scalar(
        select(Like).where((Like.post_id == post_id) & (Like.user_id == user.id))
    )

    if not db_like:
        raise HTTPException(
            detail="No like on this post found", status_code=HTTPStatus.NOT_FOUND
        )

    await session.delete(db_like)
    await session.commit()

    return {"detail": "Unliked successfully"}


@router.get(
    "/{post_id}/comments", status_code=HTTPStatus.OK, response_model=ListComments
)
async def get_comments(
    post_id: int, limit: int, offset: int, session: AsyncSession = Depends(get_session)
):
    db_comments = await session.scalars(
        select(Comment).where(Comment.post_id == post_id).offset(offset).limit(limit)
    )
    comments = db_comments.all()

    if not comments:
        raise HTTPException(
            detail="No comments found", status_code=HTTPStatus.NOT_FOUND
        )

    return comments


@router.get("/{post_id}/likes", status_code=HTTPStatus.OK, response_model=ListLikes)
async def get_likes(post_id: int, session: AsyncSession = Depends(get_session)):
    db_likes = await session.scalars(select(Like).where(Like.post_id == post_id))
    likes = db_likes.all()

    if not likes:
        raise HTTPException(detail="No likes found", status_code=HTTPStatus.NOT_FOUND)

    return {"count": len(likes), "likes": likes}
