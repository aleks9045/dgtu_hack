from pydantic import BaseModel, EmailStr, Field


class TeamCreateSchema(BaseModel):
    id_u: int = Field("creator id")
    name: str = Field("team's name")
    about: str = Field("about team")
