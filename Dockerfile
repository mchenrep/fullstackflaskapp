# Python image
FROM python:3.12-slim

# Working directory
WORKDIR /app

# Requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Make startup script executable
RUN chmod +x start.sh

# Expose Flask port
EXPOSE 5000

# Run application
CMD ["./start.sh"]

