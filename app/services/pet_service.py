from app.repository.pet_repository import PetRepository
from app.services.base_service import BaseService


class PetService(BaseService):
    def __init__(self, pet_repository: PetRepository):
        self.pet_repository = pet_repository
        super().__init__(pet_repository)

