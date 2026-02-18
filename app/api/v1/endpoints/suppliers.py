from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas
from app.database import get_db

router = APIRouter()


@router.post(
    "/",
    response_model=schemas.Supplier,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new supplier"
)
def create_supplier(
    supplier: schemas.SupplierCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new supplier/vendor.
    Supplier names must be unique.
    """
    return crud.create_supplier(db=db, supplier=supplier)


@router.get(
    "/",
    response_model=List[schemas.Supplier],
    summary="List all suppliers"
)
def list_suppliers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get a list of all suppliers.
    """
    return crud.get_suppliers(db=db, skip=skip, limit=limit)


@router.get(
    "/{supplier_id}",
    response_model=schemas.Supplier,
    summary="Get a specific supplier"
)
def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific supplier.
    """
    supplier = crud.get_supplier(db=db, supplier_id=supplier_id)
    if not supplier:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier with id {supplier_id} not found"
        )
    return supplier


@router.get(
    "/{supplier_id}/products",
    response_model=List[schemas.ProductWithRelations],
    summary="Get all products from a supplier"
)
def get_supplier_products(
    supplier_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get all products supplied by a specific supplier.
    """
    supplier = crud.get_supplier(db=db, supplier_id=supplier_id)
    if not supplier:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier with id {supplier_id} not found"
        )
    
    return crud.get_products(
        db=db,
        supplier_id=supplier_id,
        skip=skip,
        limit=limit,
        with_relations=True
    )


@router.put(
    "/{supplier_id}",
    response_model=schemas.Supplier,
    summary="Update a supplier"
)
def update_supplier(
    supplier_id: int,
    supplier: schemas.SupplierUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing supplier.
    """
    return crud.update_supplier(db=db, supplier_id=supplier_id, supplier=supplier)


@router.delete(
    "/{supplier_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a supplier"
)
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a supplier.
    Products from this supplier will have their supplier_id set to NULL.
    """
    crud.delete_supplier(db=db, supplier_id=supplier_id)