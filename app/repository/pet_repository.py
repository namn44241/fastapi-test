from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from app.model.pet import Pet
from app.repository.base_repository import BaseRepository


class PetRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory
        super().__init__(session_factory, Pet)
