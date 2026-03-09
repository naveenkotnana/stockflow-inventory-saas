from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from .. import models, schemas
from ..dependencies import get_current_user

router = APIRouter(prefix="/products", tags=["products"])


def _is_low_stock(product: models.Product, default_threshold: int) -> (bool, int):
    threshold = product.low_stock_threshold if product.low_stock_threshold is not None else default_threshold
    return product.quantity_on_hand <= threshold, threshold


@router.get("", response_model=list[schemas.ProductOut])
def list_products(
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

    products = (
        db.query(models.Product)
        .filter(models.Product.organization_id == org_id)
        .order_by(models.Product.created_at.desc())
        .all()
    )

    result = []
    for p in products:
        is_low, threshold = _is_low_stock(p, default_threshold)
        out = schemas.ProductOut.from_orm(p)
        out.is_low_stock = is_low
        out.effective_threshold = threshold
        result.append(out)
    return result


@router.post("", response_model=schemas.ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    data: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    org_id = current_user.organization_id

    existing_sku = (
        db.query(models.Product)
        .filter(
            models.Product.organization_id == org_id,
            models.Product.sku == data.sku,
        )
        .first()
    )
    if existing_sku:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SKU already exists for this organization",
        )

    product = models.Product(
        organization_id=org_id,
        **data.dict(),
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    settings = (
        db.query(models.OrganizationSettings)
        .filter(models.OrganizationSettings.organization_id == org_id)
        .first()
    )
    default_threshold = settings.default_low_stock_threshold if settings else 10
    is_low, threshold = _is_low_stock(product, default_threshold)
    out = schemas.ProductOut.from_orm(product)
    out.is_low_stock = is_low
    out.effective_threshold = threshold
    return out


@router.get("/{product_id}", response_model=schemas.ProductOut)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    org_id = current_user.organization_id
    product = (
        db.query(models.Product)
        .filter(
            models.Product.organization_id == org_id,
            models.Product.id == product_id,
        )
        .first()
    )
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    settings = (
        db.query(models.OrganizationSettings)
        .filter(models.OrganizationSettings.organization_id == org_id)
        .first()
    )
    default_threshold = settings.default_low_stock_threshold if settings else 10
    is_low, threshold = _is_low_stock(product, default_threshold)
    out = schemas.ProductOut.from_orm(product)
    out.is_low_stock = is_low
    out.effective_threshold = threshold
    return out


@router.put("/{product_id}", response_model=schemas.ProductOut)
def update_product(
    product_id: int,
    data: schemas.ProductUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    org_id = current_user.organization_id
    product = (
        db.query(models.Product)
        .filter(
            models.Product.organization_id == org_id,
            models.Product.id == product_id,
        )
        .first()
    )
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # SKU uniqueness check if sku is changing
    if data.sku and data.sku != product.sku:
        existing_sku = (
            db.query(models.Product)
            .filter(
                models.Product.organization_id == org_id,
                models.Product.sku == data.sku,
                models.Product.id != product_id,
            )
            .first()
        )
        if existing_sku:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="SKU already exists for this organization",
            )

    for field, value in data.dict(exclude_unset=True).items():
        setattr(product, field, value)

    # updated_at auto via app code (simple)
    from datetime import datetime as dt
    product.updated_at = dt.utcnow()

    db.add(product)
    db.commit()
    db.refresh(product)

    settings = (
        db.query(models.OrganizationSettings)
        .filter(models.OrganizationSettings.organization_id == org_id)
        .first()
    )
    default_threshold = settings.default_low_stock_threshold if settings else 10
    is_low, threshold = _is_low_stock(product, default_threshold)
    out = schemas.ProductOut.from_orm(product)
    out.is_low_stock = is_low
    out.effective_threshold = threshold
    return out


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    org_id = current_user.organization_id
    product = (
        db.query(models.Product)
        .filter(
            models.Product.organization_id == org_id,
            models.Product.id == product_id,
        )
        .first()
    )
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    db.delete(product)
    db.commit()
    return None