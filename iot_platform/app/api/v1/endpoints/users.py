from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user=Depends(get_current_user)) -> UserResponse:
    return current_user


@router.get("/", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), admin=Depends(require_admin)) -> list[UserResponse]:
    repository = UserRepository(db)
    return repository.list_all()
