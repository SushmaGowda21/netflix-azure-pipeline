# Base image — Python 3.11
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (for faster builds)
COPY requirements-local.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements-local.txt

# Copy all project files
COPY main.py .
COPY gold_layer.py .
COPY silver_layer.py .
COPY bronze_layer.py .
COPY data/ ./data/

# Expose port 8000
EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]