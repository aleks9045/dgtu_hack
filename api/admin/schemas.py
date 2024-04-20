from pydantic import BaseModel, Field

class AdminLoginSchema(BaseModel):
    name: str = Field(...)
    password: str = Field(...)