from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app import crud, schemas
from app.database import get_db

router = APIRouter()


@router.post(
    "/",
    response_model=schemas.ProductWithRelations,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new product"
)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new product with the following information:
    
    - **name**: Product name
    - **sku**: Stock Keeping Unit (must be unique)
    - **price**: Unit price
    - **stock_quantity**: Initial stock quantity
    - **reorder_level**: Minimum stock before reorder alert
    - **category_id**: Optional category ID
    - **supplier_id**: Optional supplier ID
    """
    return crud.create_product(db=db, product=product)


@router.get(
    "/",
    response_model=List[schemas.ProductWithRelations],
    summary="List all products"
)
def list_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    supplier_id: Optional[int] = Query(None, description="Filter by supplier ID"),
    search: Optional[str] = Query(None, description="Search in name, description, or SKU"),
    db: Session = Depends(get_db)
):
    """
    Get a list of all products with optional filtering:
    
    - **category_id**: Filter by category
    - **supplier_id**: Filter by supplier
    - **search**: Search in name, description, or SKU
    - **skip**: Pagination offset
    - **limit**: Maximum results per page
    """
    products = crud.get_products(
        db=db,
        skip=skip,
        limit=limit,
        category_id=category_id,
        supplier_id=supplier_id,
        search=search,
        with_relations=True
    )
    return products


@router.get(
    "/low-stock",
    response_model=List[schemas.LowStockProduct],
    summary="Get products with low stock"
)
def get_low_stock_products(db: Session = Depends(get_db)):
    """
    Get all products that need reordering (stock <= reorder_level).
    Useful for inventory management and purchase planning.
    """
    return crud.get_low_stock_products(db=db)


@router.get(
    "/{product_id}",
    response_model=schemas.ProductWithRelations,
    summary="Get a specific product"
)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific product by ID.
    """
    product = crud.get_product(db=db, product_id=product_id, with_relations=True)
    if not product:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    return product


@router.put(
    "/{product_id}",
    response_model=schemas.ProductWithRelations,
    summary="Update a product"
)
def update_product(
    product_id: int,
    product: schemas.ProductUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing product. Only provided fields will be updated.
    """
    return crud.update_product(db=db, product_id=product_id, product=product)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a product"
)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a product from the inventory.
    This will also delete all associated stock movement records.
    """
    crud.delete_product(db=db, product_id=product_id)


@router.post(
    "/{product_id}/adjust-stock",
    response_model=schemas.Product,
    summary="Adjust product stock"
)
def adjust_stock(
    product_id: int,
    adjustment: schemas.StockAdjustment,
    db: Session = Depends(get_db)
):
    """
    Adjust the stock quantity of a product.
    
    - **quantity**: Amount to add (positive) or remove (negative)
    - **notes**: Optional reason for adjustment
    
    This is the proper way to modify stock levels as it:
    1. Updates the product stock quantity
    2. Creates an audit trail in the stock_movements table
    3. Validates that stock doesn't go negative
    """
    return crud.adjust_product_stock(db=db, product_id=product_id, adjustment=adjustment)


@router.get(
    "/{product_id}/stock-history",
    response_model=List[schemas.StockMovement],
    summary="Get product stock movement history"
)
def get_stock_history(
    product_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get the complete stock movement history for a product.
    Shows all stock additions and removals with timestamps and notes.
    """
    return crud.get_product_stock_history(db=db, product_id=product_id, skip=skip, limit=limit)