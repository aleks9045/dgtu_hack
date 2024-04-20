from pydantic import BaseModel, EmailStr, Field


class UserCreateSchema(BaseModel):
    first_name: str = Field(title="user's first_name")
    last_name: str = Field(title="user's last_name")
    father_name: str = Field(title="user's father_name")
    email: EmailStr = Field(title="user's email")
    password: str = Field(title="user's password")
    role: str = Field(title="user's role")
    about: str = Field(title="about user")


class UserLoginSchema(BaseModel):
    email: EmailStr = Field(title="user's email")
    password: str = Field(title="user's password")

class UserPatchSchema(BaseModel):
    first_name: str = Field(title="user's first_name", default=None)
    last_name: str = Field(title="user's last_name", default=None)
    father_name: str = Field(title="user's father_name", default=None)
    email: str = Field(title="user's email", default=None)
    password: str = Field(title="user's password", default=None)
    role: str = Field(title="user's role", default=None)
    company: str = Field(title="about user", default=None)