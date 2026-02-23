from fastapi import status
from decimal import Decimal


def test_create_product(client, sample_category, sample_supplier):
    """Test creating a new product"""
    response = client.post(
        "/api/v1/products/",
        json={
            "name": "Wireless Mouse",
            "description": "Ergonomic wireless mouse",
            "sku": "MOU-001",
            "price": 29.99,
            "stock_quantity": 50,
            "reorder_level": 10,
            "category_id": sample_category.id,
            "supplier_id": sample_supplier.id
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Wireless Mouse"
    assert data["sku"] == "MOU-001"
    assert float(data["price"]) == 29.99
    assert data["stock_quantity"] == 50


def test_create_product_duplicate_sku(client, sample_product):
    """Test that duplicate SKUs are rejected"""
    response = client.post(
        "/api/v1/products/",
        json={
            "name": "Another Product",
            "sku": sample_product.sku,  # Duplicate SKU
            "price": 100.00,
            "stock_quantity": 10
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"].lower()


def test_create_product_invalid_category(client):
    """Test creating product with non-existent category"""
    response = client.post(
        "/api/v1/products/",
        json={
            "name": "Test Product",
            "sku": "TEST-001",
            "price": 50.00,
            "category_id": 99999  # Non-existent
        }
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_products(client, sample_product):
    """Test listing all products"""
    response = client.get("/api/v1/products/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_list_products_with_filters(client, sample_product, sample_category):
    """Test listing products with category filter"""
    response = client.get(f"/api/v1/products/?category_id={sample_category.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert all(p["category"]["id"] == sample_category.id for p in data)


def test_list_products_with_search(client, sample_product):
    """Test searching products"""
    response = client.get(f"/api/v1/products/?search={sample_product.name[:3]}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1


def test_get_product(client, sample_product):
    """Test getting a specific product"""
    response = client.get(f"/api/v1/products/{sample_product.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == sample_product.id
    assert data["name"] == sample_product.name
    assert "category" in data
    assert "supplier" in data


def test_update_product(client, sample_product):
    """Test updating a product"""
    response = client.put(
        f"/api/v1/products/{sample_product.id}",
        json={
            "name": "Updated Laptop",
            "price": 1099.99
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Laptop"
    assert float(data["price"]) == 1099.99


def test_delete_product(client, sample_product):
    """Test deleting a product"""
    response = client.delete(f"/api/v1/products/{sample_product.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify it's deleted
    response = client.get(f"/api/v1/products/{sample_product.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_adjust_stock_add(client, sample_product):
    """Test adding stock to a product"""
    initial_stock = sample_product.stock_quantity
    response = client.post(
        f"/api/v1/products/{sample_product.id}/adjust-stock",
        json={
            "quantity": 20,
            "notes": "Received new shipment"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["stock_quantity"] == initial_stock + 20


def test_adjust_stock_remove(client, sample_product):
    """Test removing stock from a product"""
    initial_stock = sample_product.stock_quantity
    response = client.post(
        f"/api/v1/products/{sample_product.id}/adjust-stock",
        json={
            "quantity": -5,
            "notes": "Sold items"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["stock_quantity"] == initial_stock - 5


def test_adjust_stock_insufficient(client, sample_product):
    """Test that removing more stock than available fails"""
    response = client.post(
        f"/api/v1/products/{sample_product.id}/adjust-stock",
        json={
            "quantity": -(sample_product.stock_quantity + 10),
            "notes": "Try to oversell"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "insufficient" in response.json()["detail"].lower()


def test_get_stock_history(client, sample_product):
    """Test getting stock movement history"""
    # Make some stock adjustments
    client.post(
        f"/api/v1/products/{sample_product.id}/adjust-stock",
        json={"quantity": 10, "notes": "Test adjustment 1"}
    )
    client.post(
        f"/api/v1/products/{sample_product.id}/adjust-stock",
        json={"quantity": -5, "notes": "Test adjustment 2"}
    )
    
    response = client.get(f"/api/v1/products/{sample_product.id}/stock-history")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2


def test_get_low_stock_products(client, db, sample_category, sample_supplier):
    """Test getting products with low stock"""
    # Create a product with low stock
    from app import models
    low_stock_product = models.Product(
        name="Low Stock Item",
        sku="LOW-001",
        price=50.00,
        stock_quantity=3,
        reorder_level=5,
        category_id=sample_category.id,
        supplier_id=sample_supplier.id
    )
    db.add(low_stock_product)
    db.commit()
    
    response = client.get("/api/v1/products/low-stock")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert any(p["sku"] == "LOW-001" for p in data)


def test_pagination(client, db, sample_category, sample_supplier):
    """Test pagination of product list"""
    # Create multiple products
    from app import models
    for i in range(15):
        product = models.Product(
            name=f"Product {i}",
            sku=f"PRD-{i:03d}",
            price=10.00,
            stock_quantity=10,
            category_id=sample_category.id,
            supplier_id=sample_supplier.id
        )
        db.add(product)
    db.commit()
    
    # Test first page
    response = client.get("/api/v1/products/?skip=0&limit=10")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 10
    
    # Test second page
    response = client.get("/api/v1/products/?skip=10&limit=10")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 5