# Warehouse API

A production-ready RESTful API for warehouse inventory management built with Python, FastAPI, PostgreSQL, and Docker.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)
![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)

## 🎯 Project Overview

This project demonstrates professional backend API development with a focus on:

- **RESTful API Design**: Clean, intuitive endpoints following REST principles
- **Database Architecture**: Well-structured relational database with proper foreign keys and indexing
- **Business Logic**: Stock management with audit trails and inventory tracking
- **Production Ready**: Docker containerization, testing, and deployment-ready configuration

### Key Features

- ✅ Complete CRUD operations for Products, Categories, and Suppliers
- ✅ Advanced filtering and search capabilities
- ✅ Stock adjustment system with automatic audit logging
- ✅ Low stock alerts and reorder level tracking
- ✅ Relationship management (products ↔ categories ↔ suppliers)
- ✅ Comprehensive test coverage
- ✅ Auto-generated API documentation (Swagger/OpenAPI)
- ✅ Docker containerization for easy deployment
- ✅ Database migrations with Alembic

## 🏗️ Architecture

### Technology Stack

- **Framework**: FastAPI (async Python web framework)
- **Database**: PostgreSQL 15 with SQLAlchemy ORM
- **Testing**: pytest with coverage reporting
- **Containerization**: Docker & Docker Compose
- **Migrations**: Alembic
- **Validation**: Pydantic v2

### Database Schema

```text
┌─────────────────┐
│ categories │
├─────────────────┤
│ id (PK) │
│ name │
│ description │
│ created_at │
│ updated_at │
└─────────────────┘
│
│ 1:N
│
┌─────────────────┐ ┌─────────────────┐
│ products      │ N:1 │     suppliers │
├─────────────────┤──────├─────────────────┤
│ id (PK)         │ │ id (PK) │
│ name            │ │ name │
│ sku (UNIQUE)    │ │ contact_name │
│ description     │ │ email │
│ price           │ │ phone │
│ stock_quantity  │ │ address │
│ reorder_level   │ │ created_at │
│ category_id (FK)│ │ updated_at │
│ supplier_id (FK)│ └─────────────────┘
│ created_at │
│ updated_at │
└─────────────────┘
│
│ 1:N
│
┌─────────────────┐
│ stock_movements │
├─────────────────┤
│ id (PK) │
│ product_id (FK) │
│ quantity │
│ movement_type │
│ notes │
│ created_at │
└─────────────────┘
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for containerized setup)
- PostgreSQL 15+ (if running locally without Docker)

### Option 1: Docker Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/warehouse-api.git
   cd warehouse-api
    ```

2. **Start the application**
    ```bash
   docker-compose up -d
   ```

3. **Access the API**

    API: http://localhost:8000
    Interactive docs: http://localhost:8000/api/v1/docs
    ReDoc: http://localhost:8000/api/v1/redoc

That's it! The API is now running with a PostgreSQL database.

***Option 2: Local Setup***

1. **Clone and setup virtual environment**
    ```bash
    git clone https://github.com/yourusername/warehouse-api.git
    cd warehouse-api
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2. **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3. **Configure environment**
    ```bash
    cp .env.example .env
    # Edit .env with your database credentials
    ```

4. **Run database migrations**
    ```bash
    alembic upgrade head
    ```

5. **Start the server**
    ```bash
    uvicorn app.main:app --reload
    ```

## 📚 API Documentation

    http://localhost:8000/api/v1

### Endpoints Overview
**Products**
- POST /products - Create a new product
- GET /products - List all products (with filtering)
- GET /products/{id} - Get product details
- PUT /products/{id} - Update product
- DELETE /products/{id} - Delete product
- POST /products/{id}/adjust-stock - Adjust stock quantity
- GET /products/{id}/stock-history - Get stock movement history
- GET /products/low-stock - Get products needing reorder

**Categories**
- POST /categories - Create a new category
- GET /categories - List all categories
- GET /categories/{id} - Get category details
- PUT /categories/{id} - Update category
- DELETE /categories/{id} - Delete category
- GET /categories/{id}/products - Get products in category

**Suppliers**
- POST /suppliers - Create a new supplier
- GET /suppliers - List all suppliers
- GET /suppliers/{id} - Get supplier details
- PUT /suppliers/{id} - Update supplier
- DELETE /suppliers/{id} - Delete supplier
- GET /suppliers/{id}/products - Get products from supplier

### Example requests:

- Create a product:
```bash
curl -X POST "http://localhost:8000/api/v1/products/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop",
    "sku": "LAP-001",
    "description": "High-performance laptop",
    "price": 999.99,
    "stock_quantity": 10,
    "reorder_level": 5,
    "category_id": 1,
    "supplier_id": 1
  }'
```

- Adjust Stock:
```bash
curl -X POST "http://localhost:8000/api/v1/products/1/adjust-stock" \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": -3,
    "notes": "Sold 3 units"
  }'
```

- Search Products:
```bash
curl "http://localhost:8000/api/v1/products/?search=laptop&category_id=1"
```

## 🧪 Testing

### Run All Tests
```bash
pytest tests/ -v
```

**Run with coverage**
```bash
pytest tests/ --cov=app --cov-report=html --cov-report=term
```

**View Coverage Report**

```bash
open htmlcov/index.html  # On macOS
# Or navigate to htmlcov/index.html in your browser
```

# Test structure
```text
tests/
├── config_test.py           # Test fixtures and configuration
├── categories_test.py       # Category endpoint tests
├── suppliers_test.py        # Supplier endpoint tests
└── products_test.py         # Product endpoint tests
```

## Project Structure
```text
warehouse-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── database.py          # Database setup
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── crud.py              # Database operations
│   └── api/
│       └── v1/
│           ├── __init__.py
│           └── endpoints/
│               ├── products.py
│               ├── categories.py
│               └── suppliers.py
├── tests/                   # Test suite
├── alembic/                 # Database migrations
├── docker-compose.yml       # Docker configuration
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

## Development

### Using Make Commands

```bash
make help          # Show available commands
make install       # Install dependencies
make dev          # Run development server
make test         # Run tests
make coverage     # Run tests with coverage
make format       # Format code with black
make lint         # Lint code
make docker-up    # Start Docker containers
make docker-down  # Stop Docker containers
```

**Database Migrations**

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Deployment

### AWS Deployment

1. **AWS Elastic Beanstalk (Recommended for beginners)**
```bash
# Install EB CLI
pip install awsebcli

# Initialize EB application
eb init -p docker warehouse-api

# Create environment and deploy
eb create warehouse-api-prod --database.engine postgres
```

## 🔐 Security Considerations
- ✅ SQL injection prevention via ORM
- ✅ Input validation with Pydantic
- ✅ Environment-based configuration
- ✅ Database connection pooling
- ✅ CORS configuration
- 🔄 Future: JWT authentication
- 🔄 Future: Rate limiting
- 🔄 Future: API key management

## Author

Joseph Burgy-VanHoose
- Github: [JoeAlexBV](https://github.com/JoeAlexBV)
- LinkedIn: [JosephB-V](https://www.linkedin.com/in/joseph-burgy-vanhoose-3787b5171/)
