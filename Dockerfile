# Use Python 3.12 slim as base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /vivaestate

# Install system dependencies (build essentials if needed)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt first for better caching
COPY requirements.txt /vivaestate/

# Install Python dependencies using pip
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . /vivaestate/

# Expose port 8000 (Django default)
EXPOSE 8000

# Command to run Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
