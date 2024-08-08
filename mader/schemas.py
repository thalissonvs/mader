from pydantic import BaseModel, EmailStr


class UserSchema(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    id: int
    username: str
    email: EmailStr


class UsersList(BaseModel):
    users: list[UserPublic]


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class RomancistSchema(BaseModel):
    name: str


class RomancistPublic(RomancistSchema):
    id: int


class BookSchema(BaseModel):
    title: str
    year: str
    romancist_id: int


class BookPublic(BookSchema):
    id: int


class RomancistsList(BaseModel):
    romancists: list[RomancistPublic]


class RomancistUpdate(BaseModel):
    name: str | None


class Message(BaseModel):
    message: str
