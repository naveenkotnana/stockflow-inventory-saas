from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from .. import models, schemas
from ..dependencies import get_current_user
from .products import _is_low_stock

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard", response_model=schemas.DashboardStats)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    org_id = current_user.organization_id

    settings = (
        db.query(models.OrganizationSettings)
        .filter(models.OrganizationSettings.organization_id == org_id)
        .first()
    )
    default_threshold = settings.default_low_stock_threshold if settings else 10

    total_products = (
        db.query(func.count(models.Product.id))
        .filter(models.Product.organization_id == org_id)
        .scalar()
        or 0
    )

    total_inventory_units = (
        db.query(func.coalesce(func.sum(models.Product.quantity_on_hand), 0))
        .filter(models.Product.organization_id == org_id)
        .scalar()
        or 0
    )

    products = (
        db.query(models.Product)
        .filter(models.Product.organization_id == org_id)
        .all()
    )

    low_stock_products = []
    for p in products:
        is_low, threshold = _is_low_stock(p, default_threshold)
        if is_low:
            out = schemas.ProductOut.from_orm(p)
            out.is_low_stock = True
            out.effective_threshold = threshold
            low_stock_products.append(out)

    return schemas.DashboardStats(
        total_products=total_products,
        total_inventory_units=total_inventory_units,
        low_stock_products=low_stock_products,
    )