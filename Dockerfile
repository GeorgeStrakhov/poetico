# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create data directory and set permissions
RUN mkdir -p /data && chmod 777 /data

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Ensure frontend/public exists
RUN mkdir -p frontend/public

# Make sure the script is executable
RUN chmod +x deploy.sh

# Expose the port the app runs on
EXPOSE 8888

# Command to run the application
CMD ["python", "main.py", "prod"] 