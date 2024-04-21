from pydantic import BaseModel, EmailStr, Field


class ExpertCreateSchema(BaseModel):
    first_name: str = Field(title="user's first_name")
    last_name: str = Field(title="user's last_name")
    father_name: str = Field(title="user's father_name")
    email: EmailStr = Field(title="user's email")
    password: str = Field(title="user's password")
    role: str = Field(title="user's role")
    company: str = Field(title="company")


class ExpertLoginSchema(BaseModel):
    email: str = Field(title="user's email")
    password: str = Field(title="user's password")

class AddCaseSchema(BaseModel):
    name: str = Field(title="case name")
    about: str = Field(title="case about")
    id_co: int = Field()

class AddCaseFileSchema(BaseModel):
    id_ca: int = Field()

class AddMarkSchema(BaseModel):
    design: int = Field()
    usability: int = Field()
    backend: int = Field()
    frontend: int = Field()
    realization: int = Field()
    expert: int = Field(default=None)
    user: int = Field(default=None)


class ChangeMarkSchema(BaseModel):
    design: int = Field(default=None)
    usability: int = Field(default=None)
    backend: int = Field(default=None)
    frontend: int = Field(default=None)
    realization: int = Field(default=None)
    expert: int = Field(default=None)
    user: int = Field(default=None)
