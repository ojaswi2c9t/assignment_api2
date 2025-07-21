#!/usr/bin/env bash
# Build script for render.com deployment

# Exit on error
set -e

# Print Python and pip versions
echo "🐍 Python version:"
python --version
echo "📦 Pip version:"
pip --version

# Install dependencies directly with pre-built wheels
echo "📦 Installing dependencies directly (skipping requirements.txt)..."
pip install --no-cache-dir --only-binary :all: \
  fastapi==0.103.1 \
  uvicorn==0.22.0 \
  motor==3.1.2 \
  pymongo==4.3.3 \
  pydantic==2.4.2 \
  python-dotenv==1.0.0

echo "🔁 Replacing v1 files with Pydantic v2 compatible versions if they exist..."

# Replace models/order.py with models/order_v2.py
if [ -f models/order_v2.py ]; then
    cp models/order_v2.py models/order.py
    echo "✅ Replaced models/order.py with v2 version"
fi

# Replace schemas/common.py with schemas/common_v2.py
if [ -f schemas/common_v2.py ]; then
    cp schemas/common_v2.py schemas/common.py
    echo "✅ Replaced schemas/common.py with v2 version"
fi

# Replace schemas/order.py with schemas/order_v2.py
if [ -f schemas/order_v2.py ]; then
    cp schemas/order_v2.py schemas/order.py
    echo "✅ Replaced schemas/order.py with v2 version"
fi

# Create a minimal deployment app
echo "📝 Creating minimal deployment app..."
cat > main_deploy.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="E-Commerce API",
    description="E-Commerce API with FastAPI and MongoDB",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/", include_in_schema=False)
async def root():
    return {
        "message": "Welcome to E-Commerce API!",
        "docs_url": "/api/docs",
        "health_endpoint": "/health"
    }

# Health check
@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "healthy"}
EOF

echo "🚀 Deployment preparation complete!"
