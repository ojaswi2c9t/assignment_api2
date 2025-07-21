# Backend Assignment

<div align="center">
  
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
api/
├── core/                  # Configuration & Database
├── models/                # MongoDB data models
├── schemas/               # Pydantic validation schemas
├── routes/                # API endpoints
├── services/              # Business logic
├── utils/                 # Helper functions
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

## 📚 API Documentation

Once the application is running, you can access:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

<div align="center">
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
