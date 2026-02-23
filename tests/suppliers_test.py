from fastapi import status


def test_create_supplier(client):
    """Test creating a new supplier"""
    response = client.post(
        "/api/v1/suppliers/",
        json={
            "name": "Office Supplies Co",
            "contact_name": "Jane Smith",
            "email": "jane@officesupplies.com",
            "phone": "+1987654321",
            "address": "123 Business St, City"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Office Supplies Co"
    assert data["email"] == "jane@officesupplies.com"


def test_create_duplicate_supplier(client, sample_supplier):
    """Test that duplicate supplier names are rejected"""
    response = client.post(
        "/api/v1/suppliers/",
        json={
            "name": sample_supplier.name,
            "email": "different@email.com"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_list_suppliers(client, sample_supplier):
    """Test listing all suppliers"""
    response = client.get("/api/v1/suppliers/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_supplier(client, sample_supplier):
    """Test getting a specific supplier"""
    response = client.get(f"/api/v1/suppliers/{sample_supplier.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == sample_supplier.id
    assert data["name"] == sample_supplier.name


def test_update_supplier(client, sample_supplier):
    """Test updating a supplier"""
    response = client.put(
        f"/api/v1/suppliers/{sample_supplier.id}",
        json={"email": "newemail@techsupplies.com"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == "newemail@techsupplies.com"


def test_delete_supplier(client, sample_supplier):
    """Test deleting a supplier"""
    response = client.delete(f"/api/v1/suppliers/{sample_supplier.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_get_supplier_products(client, sample_supplier, sample_product):
    """Test getting all products from a supplier"""
    response = client.get(f"/api/v1/suppliers/{sample_supplier.id}/products")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1