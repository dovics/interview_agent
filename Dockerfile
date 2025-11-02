# Multi-stage build: Stage 1 - Build React frontend
FROM node:18-alpine AS frontend-build

WORKDIR /app

# Copy package files for frontend
COPY frontend/package*.json ./
RUN npm ci

# Copy frontend source
COPY frontend/. .

# Build frontend
RUN npm run build

# Multi-stage build: Stage 2 - Build Python backend with frontend assets
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy poetry files
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Create directory for frontend build
RUN mkdir -p frontend/build

# Copy built frontend files from frontend-build stage
COPY --from=frontend-build /app/build ./frontend/build

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the server with uvicorn
CMD ["uvicorn", "interview_agent.server:app", "--host", "0.0.0.0", "--port", "8000"]