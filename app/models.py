from sqlalchemy.orm import registry, Mapped, mapped_column, relationship
from sqlalchemy import func, ForeignKey
from datetime import datetime

table_registry = registry()


@table_registry.mapped_as_dataclass
class User:
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    username: Mapped[str] = mapped_column(unique=True)
    full_name: Mapped[str] = mapped_column(nullable=True)
    email: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    bio: Mapped[str] = mapped_column(nullable=True)
    link: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())

    posts: Mapped[list["Post"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="selectin", init=False
    )

    followers: Mapped[list["Follow"]] = relationship(
        back_populates="followed_user",
        cascade="all, delete-orphan",
        foreign_keys="[Follow.followed_id]",
        lazy="selectin",
        init=False,
    )

    followed: Mapped[list["Follow"]] = relationship(
        back_populates="follower_user",
        cascade="all, delete-orphan",
        foreign_keys="[Follow.follower_id]",
        lazy="selectin",
        init=False,
    )


@table_registry.mapped_as_dataclass
class Post:
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    description: Mapped[str] = mapped_column(nullable=True)
    image_url: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        init=False, server_onupdate=func.now(), nullable=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship(
        back_populates="posts", init=False, lazy="selectin"
    )

    likes: Mapped[list["Like"]] = relationship(
        back_populates="post", cascade="all, delete-orphan", lazy="selectin", init=False
    )

    comments: Mapped[list["Comment"]] = relationship(
        back_populates="post", cascade="all, delete-orphan", lazy="selectin", init=False
    )


@table_registry.mapped_as_dataclass
class Like:
    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())

    post: Mapped["Post"] = relationship(back_populates="likes", init=False)


@table_registry.mapped_as_dataclass
class Comment:
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    comment: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())

    post: Mapped["Post"] = relationship(back_populates="comments", init=False)


@table_registry.mapped_as_dataclass
class Follow:
    __tablename__ = "follows"

    follower_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    followed_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(init=False, server_default=func.now())

    follower_user: Mapped["User"] = relationship(
        back_populates="followed", foreign_keys=[follower_id], init=False
    )

    followed_user: Mapped["User"] = relationship(
        back_populates="followers", foreign_keys=[followed_id], init=False
    )
