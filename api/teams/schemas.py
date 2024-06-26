from pydantic import BaseModel, Field


class TeamCreateSchema(BaseModel):
    id_u: int = Field("creator id")
    name: str = Field("team's name")
    about: str = Field("about team")



class AddUserSchema(BaseModel):
    id_u: int = Field("user id")
    id_t: int = Field("team id")


class TeamPatchSchema(BaseModel):
    id_t: int = Field("team id")
    name: str = Field(default=None)
    about: str = Field(default=None)

class AddJobSchema(BaseModel):
    github: str = Field(default=None)
    id_ca: int = Field()
    id_t: int = Field()

class PatchJobSchema(BaseModel):
    id_j: int = Field()
    github: str = Field()