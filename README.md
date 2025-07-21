# E-Commerce API

<div align="center">
  <img width="800" alt="E-Commerce API Architecture" src="https://github.com/user-attachments/assets/65d8e44d-90bc-4ab4-a297-a425e6ecb06a" />
  
  <p>
    <strong>A modern e-commerce API built with FastAPI and MongoDB</strong>
  </p>
  
  <p>
    <a href="#features">Features</a> •
    <a href="#project-structure">Project Structure</a> •
    <a href="#installation">Installation</a> •
    <a href="#docker-setup">Docker Setup</a> •
    <a href="#api-documentation">API Documentation</a> •
    <a href="#development">Development</a>
  </p>
</div>

## 🚀 Features

- **Product Management**: Complete CRUD operations for products
- **Order Processing**: Order creation with inventory validation
- **Pagination & Filtering**: Efficient data retrieval with cursor-based pagination
- **MongoDB Integration**: Asynchronous database operations with Motor
- **Data Validation**: Request/response validation with Pydantic
- **Error Handling**: Comprehensive error handling with custom exceptions
- **API Documentation**: Auto-generated Swagger UI and ReDoc documentation
- **Containerization**: Docker support for easy deployment

## 📂 Project Structure

```
ecommerce_api/
├── core/                  # Configuration & Database
│   ├── config.py          # Application settings
│   ├── database.py        # MongoDB client setup
│   └── logging.py         # Logging configuration
├── models/                # MongoDB data models
│   ├── base.py            # Common types and base models
│   ├── product.py         # Product model
│   ├── order.py           # Order model
│   └── user.py            # User model
├── schemas/               # Pydantic validation schemas
│   ├── common.py          # Shared schemas
│   ├── product.py         # Product schemas
│   ├── order.py           # Order schemas
│   └── pagination.py      # Pagination schemas
├── routes/                # API endpoints
│   ├── __init__.py        # Router initialization
│   ├── product.py         # Product routes
│   ├── order.py           # Order routes
│   └── health.py          # Health check routes
├── services/              # Business logic
│   ├── product_service.py # Product service
│   └── order_service.py   # Order service
├── utils/                 # Helper functions
│   ├── pagination.py      # Pagination utilities
│   ├── bson_utils.py      # MongoDB ObjectId utilities
│   └── errors.py          # Error handling
├── main.py                # Application entry point
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose configuration
├── requirements.txt       # Project dependencies
└── .env.example           # Environment variables example
```

## 🔧 Installation

### Prerequisites

- Python 3.8+
- MongoDB (local installation or MongoDB Atlas)

### Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ecommerce_api
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy example env file
   cp .env.example .env
   
   # Edit .env file with your MongoDB connection string and other settings
   ```

5. **Run the application**
   ```bash
   uvicorn main:app --reload
   ```

## 🐳 Docker Setup

### Option 1: Using Docker Compose (Recommended)

1. **Create a Dockerfile**
   
   Create a file named `Dockerfile` in the root directory with the following content:
   ```dockerfile
   FROM python:3.9-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   EXPOSE 8000

   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Create a docker-compose.yml file**
   
   Create a file named `docker-compose.yml` with the following content:
   ```yaml
   version: '3'

   services:
     api:
       build: .
       ports:
         - "8000:8000"
       environment:
         - MONGODB_URL=mongodb://mongo:27017
         - MONGODB_DB_NAME=ecommerce
       depends_on:
         - mongo
       volumes:
         - .:/app
       restart: always

     mongo:
       image: mongo:5.0
       ports:
         - "27017:27017"
       volumes:
         - mongodb_data:/data/db

   volumes:
     mongodb_data:
   ```

3. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

### Option 2: Using Docker Only

1. **Build the Docker image**
   ```bash
   docker build -t ecommerce-api .
   ```

2. **Run the container**
   ```bash
   docker run -d -p 8000:8000 --name ecommerce-api \
     -e MONGODB_URL=<your-mongodb-url> \
     -e MONGODB_DB_NAME=ecommerce \
     ecommerce-api
   ```

## 📚 API Documentation

Once the application is running, you can access:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

<div align="center">
  <img width="800" alt="API Documentation" src="https://github.com/user-attachments/assets/7522e5ae-5f44-4d31-b5ee-679c353a45d1" />
</div>

## 💻 Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
# Install development dependencies
pip install black isort flake8

# Format code
black .
isort .

# Check for linting errors
flake8
```

## 📝 License

MIT 
