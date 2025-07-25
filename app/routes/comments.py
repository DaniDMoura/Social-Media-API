from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.security import get_current_user
from app.models import User, Comment
from app.database import get_session
from app.schemas import ListComment, DeleteComment

router = APIRouter()


@router.get("/{comment_id}", status_code=HTTPStatus.OK, response_model=ListComment)
async def get_comment(
    comment_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    db_comment = await session.scalar(select(Comment).where(Comment.id == comment_id))

    if not db_comment:
        raise HTTPException(detail="No comment found", status_code=HTTPStatus.NOT_FOUND)

    return db_comment


@router.put("/{comment_id}", status_code=HTTPStatus.OK, response_model=ListComment)
async def update_comment(
    new_comment: str,
    comment_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    db_comment = await session.scalar(select(Comment).where(Comment.id == comment_id))

    if not db_comment:
        raise HTTPException(detail="No comment found", status_code=HTTPStatus.NOT_FOUND)

    if db_comment.user_id != user.id:
        raise HTTPException(
            detail="Not enough permissions", status_code=HTTPStatus.UNAUTHORIZED
        )

    db_comment.comment = new_comment

    await session.commit()
    await session.refresh(db_comment)

    return db_comment


@router.delete("/{comment_id}", status_code=HTTPStatus.OK, response_model=DeleteComment)
async def delete_comment(
    comment_id: int,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
):
    db_comment = await session.scalar(select(Comment).where(Comment.id == comment_id))

    if not db_comment:
        raise HTTPException(detail="No comment found", status_code=HTTPStatus.NOT_FOUND)

    if db_comment.user_id != user.id:
        raise HTTPException(
            detail="Not enough permissions", status_code=HTTPStatus.UNAUTHORIZED
        )

    await session.delete(db_comment)
    await session.commit()

    return {"detail": "Comment deleted"}
