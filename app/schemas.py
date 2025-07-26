from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr
from typing import List, Optional



class ListComment(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    post_id: int
    comment: str
    created_at: datetime


class ListLike(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    post_id: int
    created_at: datetime


class ListLikes(BaseModel):
    count: int
    likes: List[ListLike]


class ListComments(BaseModel):
    count: int
    comments: List[ListComment]


class CreateUser(BaseModel):
    email: EmailStr
    username: str
    password: str


class UpdateUser(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    link: Optional[str] = None


class Posts(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    description: str
    image_url: str
    created_at: datetime
    updated_at: Optional[datetime]
    user_id: int

    comments: Optional[List[ListComment]] = []
    likes: Optional[List[ListLike]] = []


class CreatePost(BaseModel):
    description: str
    image_url: str


class ListPosts(BaseModel):
    count: int
    posts: List[Posts]


class ListPostsFeed(BaseModel):
    posts: List[Posts]


class FollowSchema(BaseModel):
    follower_id: int
    followed_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ListFollowing(BaseModel):
    count: int
    following: list[FollowSchema]

class ListFollowers(BaseModel):
    count: int
    followers: List[FollowSchema]


class ListUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    full_name: Optional[str] = None
    email: EmailStr
    bio: Optional[str] = None
    link: Optional[str] = None
    created_at: datetime

    posts: Optional[List[Posts]] = []



class DeleteUser(BaseModel):
    detail: str


class DeletePost(BaseModel):
    detail: str


class Unlike(BaseModel):
    detail: str


class DeleteComment(BaseModel):
    detail: str


class FollowResponse(BaseModel):
    detail: str


class UnfollowResponse(BaseModel):
    detail: str
