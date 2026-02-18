from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal


# ============== Category Schemas ==============

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    description: Optional[str] = Field(None, description="Category description")


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class Category(CategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============== Supplier Schemas ==============

class SupplierBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Supplier name")
    contact_name: Optional[str] = Field(None, max_length=200)
    email: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    contact_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class Supplier(SupplierBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============== Product Schemas ==============

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Product name")
    description: Optional[str] = None
    sku: str = Field(..., min_length=1, max_length=100, description="Stock Keeping Unit")
    price: Decimal = Field(..., gt=0, decimal_places=2, description="Unit price")
    stock_quantity: int = Field(default=0, ge=0, description="Current stock quantity")
    reorder_level: int = Field(default=10, ge=0, description="Minimum stock before reorder")
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    stock_quantity: Optional[int] = Field(None, ge=0)
    reorder_level: Optional[int] = Field(None, ge=0)
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None


class Product(ProductBase):
    id: int
    needs_reorder: bool = Field(description="Whether stock is below reorder level")
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class ProductWithRelations(Product):
    """Product with related category and supplier"""
    category: Optional[Category] = None
    supplier: Optional[Supplier] = None


# ============== Stock Movement Schemas ==============

class StockMovementBase(BaseModel):
    quantity: int = Field(..., description="Quantity (positive for in, negative for out)")
    movement_type: str = Field(..., max_length=50, description="Type: purchase, sale, adjustment, return")
    notes: Optional[str] = None


class StockMovementCreate(StockMovementBase):
    product_id: int


class StockMovement(StockMovementBase):
    id: int
    product_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


# ============== Stock Adjustment Schemas ==============

class StockAdjustment(BaseModel):
    """Schema for adjusting stock quantity"""
    quantity: int = Field(..., description="Quantity to add (positive) or remove (negative)")
    notes: Optional[str] = Field(None, description="Reason for adjustment")


# ============== Response Schemas ==============

class MessageResponse(BaseModel):
    message: str


class LowStockProduct(BaseModel):
    """Product that needs reordering"""
    id: int
    name: str
    sku: str
    stock_quantity: int
    reorder_level: int
    
    model_config = ConfigDict(from_attributes=True)