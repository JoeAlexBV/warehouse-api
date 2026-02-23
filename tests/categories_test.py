from fastapi import status


def test_create_category(client):
    """Test creating a new category"""
    response = client.post(
        "/api/v1/categories/",
        json={
            "name": "Furniture",
            "description": "Office and home furniture"
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Furniture"
    assert data["description"] == "Office and home furniture"
    assert "id" in data
    assert "created_at" in data


def test_create_duplicate_category(client, sample_category):
    """Test that duplicate category names are rejected"""
    response = client.post(
        "/api/v1/categories/",
        json={
            "name": sample_category.name,
            "description": "Duplicate category"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"].lower()


def test_list_categories(client, sample_category):
    """Test listing all categories"""
    response = client.get("/api/v1/categories/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["name"] == sample_category.name


def test_get_category(client, sample_category):
    """Test getting a specific category"""
    response = client.get(f"/api/v1/categories/{sample_category.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == sample_category.id
    assert data["name"] == sample_category.name


def test_get_nonexistent_category(client):
    """Test getting a category that doesn't exist"""
    response = client.get("/api/v1/categories/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_category(client, sample_category):
    """Test updating a category"""
    response = client.put(
        f"/api/v1/categories/{sample_category.id}",
        json={"name": "Updated Electronics"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Updated Electronics"


def test_delete_category(client, sample_category):
    """Test deleting a category"""
    response = client.delete(f"/api/v1/categories/{sample_category.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify it's deleted
    response = client.get(f"/api/v1/categories/{sample_category.id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_category_products(client, sample_category, sample_product):
    """Test getting all products in a category"""
    response = client.get(f"/api/v1/categories/{sample_category.id}/products")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["category"]["id"] == sample_category.id