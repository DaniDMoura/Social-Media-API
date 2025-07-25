from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.models import User, Follow
from app.security import get_current_user, get_password_hash
from app.schemas import (
    CreateUser,
    FollowResponse,
    ListFollowers,
    ListFollowing,
    ListUser,
    DeleteUser,
    UnfollowResponse,
    UpdateUser,
    ListPosts,
)

router = APIRouter()


@router.post("/", status_code=HTTPStatus.CREATED, response_model=ListUser)
async def create_user(user: CreateUser, session: AsyncSession = Depends(get_session)):
    db_user = await session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.email == user.email:
            raise HTTPException(
                detail="Email already exists", status_code=HTTPStatus.CONFLICT
            )
        if db_user.username == user.username:
            raise HTTPException(
                detail="Username already exists", status_code=HTTPStatus.CONFLICT
            )

    hashed_password = get_password_hash(user.password)

    db_user = User(
        username=user.username,
        email=user.email,
        password=hashed_password,
        full_name=None,
        bio=None,
        link=None,
    )

    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.get("/{user_id}", status_code=HTTPStatus.OK, response_model=ListUser)
async def get_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    db_user = await session.scalar(select(User).where(User.id == user_id))

    if not db_user:
        raise HTTPException(detail="User not found", status_code=HTTPStatus.NOT_FOUND)

    return db_user


@router.put("/{user_id}", status_code=HTTPStatus.OK, response_model=ListUser)
async def update_user(
    user_id: int,
    new_user: UpdateUser,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    if user_id != user.id:
        raise HTTPException(
            detail="Not enough permissions", status_code=HTTPStatus.UNAUTHORIZED
        )
    try:
        user.username = new_user.username
        user.password = get_password_hash(new_user.password)
        user.email = new_user.email
        user.bio = new_user.bio
        user.link = new_user.link
        user.full_name = new_user.full_name

        await session.commit()
        await session.refresh(user)

        return user

    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Username or Email already exists",
        )


@router.delete("/{user_id}", status_code=HTTPStatus.OK, response_model=DeleteUser)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    if user_id != user.id:
        raise HTTPException(
            detail="Not enough permissions", status_code=HTTPStatus.UNAUTHORIZED
        )

    await session.delete(user)
    await session.commit()

    return {"detail": "User deleted"}


@router.get("/{user_id}/posts", status_code=HTTPStatus.OK, response_model=ListPosts)
async def get_posts(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    db_user = await session.scalar(
        select(User).options(selectinload(User.posts)).where(User.id == user_id)
    )

    if not db_user:
        raise HTTPException(detail="User not found", status_code=HTTPStatus.NOT_FOUND)

    return {"count": len(db_user.posts), "posts": db_user.posts}


@router.get("/{user_id}/followers", status_code=HTTPStatus.OK, response_model=ListFollowers)
async def get_followers(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    target_user = await session.scalar(select(User).where(User.id == user_id))
    if not target_user:
        raise HTTPException(detail="User not found", status_code=HTTPStatus.NOT_FOUND)

    followers = await session.scalars(
        select(Follow).where(Follow.followed_id == user_id)
    )
    followers = list(followers)

    return {"count": len(followers), "followers": followers}


@router.get("/{user_id}/following", status_code=HTTPStatus.OK, response_model=ListFollowing)
async def get_following(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    target_user = await session.scalar(select(User).where(User.id == user_id))
    if not target_user:
        raise HTTPException(detail="User not found", status_code=HTTPStatus.NOT_FOUND)

    followings = await session.scalars(
        select(Follow).where(Follow.follower_id == user_id)
    )
    followings = list(followings)

    return {"count": len(followings), "following": followings}


@router.post(
    "/{user_id}/follow", status_code=HTTPStatus.CREATED, response_model=FollowResponse
)
async def follow_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    if user_id == user.id:
        raise HTTPException(
            detail="You cannot follow yourself", status_code=HTTPStatus.BAD_REQUEST
        )

    target_user = await session.scalar(select(User).where(User.id == user_id))
    if not target_user:
        raise HTTPException(detail="User not found", status_code=HTTPStatus.NOT_FOUND)

    existing_follow = await session.scalar(
        select(Follow).where(
            Follow.follower_id == user.id,
            Follow.followed_id == user_id
        )
    )

    if existing_follow:
        raise HTTPException(
            detail="You are already following this user",
            status_code=HTTPStatus.CONFLICT,
        )

    follow = Follow(follower_id=user.id, followed_id=user_id)

    session.add(follow)
    await session.commit()
    await session.refresh(follow)

    return {"detail": f"You are now following {target_user.username}"}


@router.delete(
    "/{user_id}/follow", status_code=HTTPStatus.OK, response_model=UnfollowResponse
)
async def unfollow_user(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    if user_id == user.id:
        raise HTTPException(
            detail="You cannot unfollow yourself", status_code=HTTPStatus.BAD_REQUEST
        )

    target_user = await session.scalar(select(User).where(User.id == user_id))
    if not target_user:
        raise HTTPException(detail="User not found", status_code=HTTPStatus.NOT_FOUND)

    follow_relationship = await session.scalar(
        select(Follow).where(
            Follow.follower_id == user.id,
            Follow.followed_id == user_id
        )
    )

    if not follow_relationship:
        raise HTTPException(
            detail="You are not following this user", status_code=HTTPStatus.NOT_FOUND
        )

    await session.delete(follow_relationship)
    await session.commit()

    return {"detail": f"You have unfollowed {target_user.username}"}
