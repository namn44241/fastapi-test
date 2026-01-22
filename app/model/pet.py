from typing import Optional

from sqlmodel import Field

from app.model.base_model import BaseModel


class Pet(BaseModel, table=True):
    name: str = Field()
    species: str = Field()
    breed: str = Field()
    age: int = Field()
    weight: float = Field()
    owner_name: str = Field()
    description: Optional[str] = Field(default=None, nullable=True)
    is_vaccinated: bool = Field(default=False)

