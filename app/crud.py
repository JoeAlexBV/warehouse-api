from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from typing import Optional, List
from fastapi import HTTPException, status

from app import models, schemas


# ============== Category CRUD ==============

def get_category(db: Session, category_id: int) -> Optional[models.Category]:
    """Get a category by ID"""
    return db.query(models.Category).filter(models.Category.id == category_id).first()


def get_category_by_name(db: Session, name: str) -> Optional[models.Category]:
    """Get a category by name"""
    return db.query(models.Category).filter(models.Category.name == name).first()


def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[models.Category]:
    """Get all categories with pagination"""
    return db.query(models.Category).offset(skip).limit(limit).all()


def create_category(db: Session, category: schemas.CategoryCreate) -> models.Category:
    """Create a new category"""
    # Check if category with same name already exists
    existing = get_category_by_name(db, category.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name '{category.name}' already exists"
        )
    
    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(
    db: Session, 
    category_id: int, 
    category: schemas.CategoryUpdate
) -> models.Category:
    """Update a category"""
    db_category = get_category(db, category_id)
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found"
        )
    
    # Check if new name conflicts with existing category
    if category.name:
        existing = get_category_by_name(db, category.name)
        if existing and existing.id != category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with name '{category.name}' already exists"
            )
    
    update_data = category.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int) -> None:
    """Delete a category"""
    db_category = get_category(db, category_id)
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found"
        )
    
    db.delete(db_category)
    db.commit()


# ============== Supplier CRUD ==============

def get_supplier(db: Session, supplier_id: int) -> Optional[models.Supplier]:
    """Get a supplier by ID"""
    return db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()


def get_supplier_by_name(db: Session, name: str) -> Optional[models.Supplier]:
    """Get a supplier by name"""
    return db.query(models.Supplier).filter(models.Supplier.name == name).first()


def get_suppliers(db: Session, skip: int = 0, limit: int = 100) -> List[models.Supplier]:
    """Get all suppliers with pagination"""
    return db.query(models.Supplier).offset(skip).limit(limit).all()


def create_supplier(db: Session, supplier: schemas.SupplierCreate) -> models.Supplier:
    """Create a new supplier"""
    existing = get_supplier_by_name(db, supplier.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Supplier with name '{supplier.name}' already exists"
        )
    
    db_supplier = models.Supplier(**supplier.model_dump())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier


def update_supplier(
    db: Session, 
    supplier_id: int, 
    supplier: schemas.SupplierUpdate
) -> models.Supplier:
    """Update a supplier"""
    db_supplier = get_supplier(db, supplier_id)
    if not db_supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier with id {supplier_id} not found"
        )
    
    if supplier.name:
        existing = get_supplier_by_name(db, supplier.name)
        if existing and existing.id != supplier_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Supplier with name '{supplier.name}' already exists"
            )
    
    update_data = supplier.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_supplier, field, value)
    
    db.commit()
    db.refresh(db_supplier)
    return db_supplier


def delete_supplier(db: Session, supplier_id: int) -> None:
    """Delete a supplier"""
    db_supplier = get_supplier(db, supplier_id)
    if not db_supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supplier with id {supplier_id} not found"
        )
    
    db.delete(db_supplier)
    db.commit()


# ============== Product CRUD ==============

def get_product(
    db: Session, 
    product_id: int, 
    with_relations: bool = False
) -> Optional[models.Product]:
    """Get a product by ID, optionally with relationships loaded"""
    query = db.query(models.Product)
    if with_relations:
        query = query.options(
            joinedload(models.Product.category),
            joinedload(models.Product.supplier)
        )
    return query.filter(models.Product.id == product_id).first()


def get_product_by_sku(db: Session, sku: str) -> Optional[models.Product]:
    """Get a product by SKU"""
    return db.query(models.Product).filter(models.Product.sku == sku).first()


def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    supplier_id: Optional[int] = None,
    search: Optional[str] = None,
    with_relations: bool = False
) -> List[models.Product]:
    """Get products with optional filtering"""
    query = db.query(models.Product)
    
    if with_relations:
        query = query.options(
            joinedload(models.Product.category),
            joinedload(models.Product.supplier)
        )
    
    if category_id:
        query = query.filter(models.Product.category_id == category_id)
    
    if supplier_id:
        query = query.filter(models.Product.supplier_id == supplier_id)
    
    if search:
        search_filter = or_(
            models.Product.name.ilike(f"%{search}%"),
            models.Product.description.ilike(f"%{search}%"),
            models.Product.sku.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    return query.offset(skip).limit(limit).all()


def get_low_stock_products(db: Session) -> List[models.Product]:
    """Get products that need reordering"""
    return db.query(models.Product).filter(
        models.Product.stock_quantity <= models.Product.reorder_level
    ).all()


def create_product(db: Session, product: schemas.ProductCreate) -> models.Product:
    """Create a new product"""
    # Check if SKU already exists
    existing = get_product_by_sku(db, product.sku)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product with SKU '{product.sku}' already exists"
        )
    
    # Verify foreign keys exist
    if product.category_id:
        category = get_category(db, product.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {product.category_id} not found"
            )
    
    if product.supplier_id:
        supplier = get_supplier(db, product.supplier_id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Supplier with id {product.supplier_id} not found"
            )
    
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    # Create initial stock movement record
    if product.stock_quantity > 0:
        stock_movement = models.StockMovement(
            product_id=db_product.id,
            quantity=product.stock_quantity,
            movement_type="initial_stock",
            notes="Initial stock entry"
        )
        db.add(stock_movement)
        db.commit()
    
    return db_product


def update_product(
    db: Session, 
    product_id: int, 
    product: schemas.ProductUpdate
) -> models.Product:
    """Update a product"""
    db_product = get_product(db, product_id)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    
    # Check SKU uniqueness
    if product.sku:
        existing = get_product_by_sku(db, product.sku)
        if existing and existing.id != product_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product with SKU '{product.sku}' already exists"
            )
    
    # Verify foreign keys
    if product.category_id:
        category = get_category(db, product.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {product.category_id} not found"
            )
    
    if product.supplier_id:
        supplier = get_supplier(db, product.supplier_id)
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Supplier with id {product.supplier_id} not found"
            )
    
    update_data = product.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int) -> None:
    """Delete a product"""
    db_product = get_product(db, product_id)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    
    db.delete(db_product)
    db.commit()


def adjust_product_stock(
    db: Session,
    product_id: int,
    adjustment: schemas.StockAdjustment
) -> models.Product:
    """Adjust product stock quantity and record movement"""
    db_product = get_product(db, product_id)
    if not db_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    
    new_quantity = db_product.stock_quantity + adjustment.quantity
    
    if new_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Current: {db_product.stock_quantity}, Requested: {abs(adjustment.quantity)}"
        )
    
    # Update stock quantity
    db_product.stock_quantity = new_quantity
    
    # Record stock movement
    movement_type = "stock_in" if adjustment.quantity > 0 else "stock_out"
    stock_movement = models.StockMovement(
        product_id=product_id,
        quantity=adjustment.quantity,
        movement_type=movement_type,
        notes=adjustment.notes
    )
    db.add(stock_movement)
    
    db.commit()
    db.refresh(db_product)
    return db_product


def get_product_stock_history(
    db: Session,
    product_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[models.StockMovement]:
    """Get stock movement history for a product"""
    return db.query(models.StockMovement).filter(
        models.StockMovement.product_id == product_id
    ).order_by(models.StockMovement.created_at.desc()).offset(skip).limit(limit).all()