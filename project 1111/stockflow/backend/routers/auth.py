from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models
from .. import schemas
from ..auth import hash_password, verify_password, create_access_token

router = APIRouter(tags=["auth"])


@router.post("/signup", response_model=schemas.Token)
def signup(data: schemas.SignupRequest, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    org = models.Organization(name=data.organization_name)
    db.add(org)
    db.flush()  # get org.id

    password_hash = hash_password(data.password)
    user = models.User(email=data.email, password_hash=password_hash, organization_id=org.id)
    db.add(user)

    # Create default settings for org
    settings = models.OrganizationSettings(
        organization_id=org.id,
        default_low_stock_threshold=10,
    )
    db.add(settings)

    db.commit()
    db.refresh(user)

    token = create_access_token(
        schemas.UserInToken(id=user.id, email=user.email, organization_id=user.organization_id)
    )
    return schemas.Token(access_token=token)


@router.post("/login", response_model=schemas.Token)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    token = create_access_token(
        schemas.UserInToken(id=user.id, email=user.email, organization_id=user.organization_id)
    )
    return schemas.Token(access_token=token)