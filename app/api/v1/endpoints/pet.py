from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends

from app.core.container import Container
from app.core.middleware import inject
from app.core.security import JWTBearer
from app.schema.base_schema import Blank
from app.schema.pet_schema import FindPet, FindPetResult, Pet, UpsertPet
from app.services.pet_service import PetService

router = APIRouter(prefix="/pet", tags=["pet"], dependencies=[Depends(JWTBearer())])


@router.post("", response_model=Pet)
@inject
def create_pet(
    pet: UpsertPet,
    service: PetService = Depends(Provide[Container.pet_service]),
):
    return service.add(pet)


@router.get("", response_model=FindPetResult)
@inject
def get_pet_list(
    find_query: FindPet = Depends(),
    service: PetService = Depends(Provide[Container.pet_service]),
):
    return service.get_list(find_query)


@router.get("/{pet_id}", response_model=Pet)
@inject
def get_pet(
    pet_id: int,
    service: PetService = Depends(Provide[Container.pet_service]),
):
    return service.get_by_id(pet_id)


@router.patch("/{pet_id}", response_model=Pet)
@inject
def update_pet(
    pet_id: int,
    pet: UpsertPet,
    service: PetService = Depends(Provide[Container.pet_service]),
):
    return service.patch(pet_id, pet)


@router.delete("/{pet_id}", response_model=Blank)
@inject
def delete_pet(
    pet_id: int,
    service: PetService = Depends(Provide[Container.pet_service]),
):
    service.remove_by_id(pet_id)
    return Blank()

