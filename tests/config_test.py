import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app import models

# Use in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with database dependency override"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_category(db):
    """Create a sample category for testing"""
    category = models.Category(
        name="Electronics",
        description="Electronic products"
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@pytest.fixture
def sample_supplier(db):
    """Create a sample supplier for testing"""
    supplier = models.Supplier(
        name="Tech Supplies Inc",
        contact_name="John Doe",
        email="john@techsupplies.com",
        phone="+1234567890"
    )
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@pytest.fixture
def sample_product(db, sample_category, sample_supplier):
    """Create a sample product for testing"""
    product = models.Product(
        name="Laptop",
        description="High-performance laptop",
        sku="LAP-001",
        price=999.99,
        stock_quantity=10,
        reorder_level=5,
        category_id=sample_category.id,
        supplier_id=sample_supplier.id
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product