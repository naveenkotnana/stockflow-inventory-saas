from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models, schemas
from ..dependencies import get_current_user

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=schemas.SettingsOut)
def get_settings(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    org_id = current_user.organization_id
    settings = (
        db.query(models.OrganizationSettings)
        .filter(models.OrganizationSettings.organization_id == org_id)
        .first()
    )
    if not settings:
        settings = models.OrganizationSettings(
            organization_id=org_id,
            default_low_stock_threshold=10,
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return schemas.SettingsOut(default_low_stock_threshold=settings.default_low_stock_threshold)


@router.put("", response_model=schemas.SettingsOut)
def update_settings(
    data: schemas.SettingsUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    org_id = current_user.organization_id
    settings = (
        db.query(models.OrganizationSettings)
        .filter(models.OrganizationSettings.organization_id == org_id)
        .first()
    )
    if not settings:
        settings = models.OrganizationSettings(
            organization_id=org_id,
            default_low_stock_threshold=data.default_low_stock_threshold,
        )
        db.add(settings)
    else:
        settings.default_low_stock_threshold = data.default_low_stock_threshold

    db.commit()
    db.refresh(settings)
    return schemas.SettingsOut(default_low_stock_threshold=settings.default_low_stock_threshold)