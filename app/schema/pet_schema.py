from typing import List, Optional

from pydantic import BaseModel

from app.schema.base_schema import FindBase, ModelBaseInfo, SearchOptions
from app.util.schema import AllOptional


class BasePet(BaseModel):
    name: str
    species: str
    breed: str
    age: int
    weight: float
    owner_name: str
    description: Optional[str]
    is_vaccinated: bool

    class Config:
        orm_mode = True


class Pet(ModelBaseInfo, BasePet, metaclass=AllOptional):
    ...


class FindPet(FindBase, BasePet, metaclass=AllOptional):
    species__eq: str
    breed__eq: str
    is_vaccinated__eq: bool
    ...


class UpsertPet(BasePet, metaclass=AllOptional):
    ...


class FindPetResult(BaseModel):
    founds: Optional[List[Pet]]
    search_options: Optional[SearchOptions]

