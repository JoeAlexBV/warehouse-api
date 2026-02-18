from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List

from app import crud, schemas
from app.database import get_db

router = APIRouter()


@router.post(
    "/",
    response_model=schemas.Category,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category"
)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new product category.
    Category names must be unique.
    """
    return crud.create_category(db=db, category=category)


@router.get(
    "/",
    response_model=List[schemas.Category],
    summary="List all categories"
)
def list_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get a list of all product categories.
    """
    return crud.get_categories(db=db, skip=skip, limit=limit)


@router.get(
    "/{category_id}",
    response_model=schemas.Category,
    summary="Get a specific category"
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific category.
    """
    category = crud.get_category(db=db, category_id=category_id)
    if not category:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found"
        )
    return category


@router.get(
    "/{category_id}/products",
    response_model=List[schemas.ProductWithRelations],
    summary="Get all products in a category"
)
def get_category_products(
    category_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get all products belonging to a specific category.
    This demonstrates handling of relationships in the API.
    """
    # Verify category exists
    category = crud.get_category(db=db, category_id=category_id)
    if not category:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found"
        )
    
    return crud.get_products(
        db=db,
        category_id=category_id,
        skip=skip,
        limit=limit,
        with_relations=True
    )


@router.put(
    "/{category_id}",
    response_model=schemas.Category,
    summary="Update a category"
)
def update_category(
    category_id: int,
    category: schemas.CategoryUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing category.
    """
    return crud.update_category(db=db, category_id=category_id, category=category)


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a category"
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a category.
    Products in this category will have their category_id set to NULL.
    """
    crud.delete_category(db=db, category_id=category_id)