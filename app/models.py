from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.database import Base


class Category(Base):
    """
    Product categories (e.g., Electronics, Clothing, Food)
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    products = relationship("Product", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


class Supplier(Base):
    """
    Product suppliers/vendors
    """
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    contact_name = Column(String(200), nullable=True)
    email = Column(String(200), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    products = relationship("Product", back_populates="supplier", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Supplier(id={self.id}, name='{self.name}')>"


class Product(Base):
    """
    Products in the warehouse inventory
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    sku = Column(String(100), unique=True, nullable=False, index=True)  # Stock Keeping Unit
    price = Column(Numeric(10, 2), nullable=False)  # Unit price
    stock_quantity = Column(Integer, nullable=False, default=0)
    reorder_level = Column(Integer, nullable=False, default=10)  # Minimum stock before reorder
    
    # Foreign Keys
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    category = relationship("Category", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    stock_movements = relationship("StockMovement", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', sku='{self.sku}', stock={self.stock_quantity})>"

    @property
    def needs_reorder(self) -> bool:
        """Check if product stock is below reorder level"""
        return self.stock_quantity <= self.reorder_level


class StockMovement(Base):
    """
    Track all stock movements (in/out) for audit trail
    """
    __tablename__ = "stock_movements"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)  # Positive for incoming, negative for outgoing
    movement_type = Column(String(50), nullable=False)  # e.g., 'purchase', 'sale', 'adjustment', 'return'
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="stock_movements")

    def __repr__(self):
        return f"<StockMovement(id={self.id}, product_id={self.product_id}, quantity={self.quantity}, type='{self.movement_type}')>"