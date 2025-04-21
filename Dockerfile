FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create upload directory
RUN mkdir -p uploads

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UPLOAD_FOLDER=/app/uploads

# Expose port
EXPOSE 8000

# Run the service
CMD ["python", "-m", "src.main", "--host", "0.0.0.0", "--port", "8000"] 