from pydantic import BaseModel, EmailStr, Field


class ExpertCreateSchema(BaseModel):
    first_name: str = Field(title="user's first_name")
    last_name: str = Field(title="user's last_name")
    father_name: str = Field(title="user's father_name")
    email: EmailStr = Field(title="user's email")
    password: str = Field(title="user's password")
    role: str = Field(title="user's role")
    about: str = Field(title="about user")


class ExpertLoginSchema(BaseModel):
    email: str = Field(title="user's email")
    password: str = Field(title="user's password")

class AddCaseSchema(BaseModel):
    name: str = Field()
    about: str = Field()