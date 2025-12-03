# Use Red Hat UBI (Universal Base Image) for OpenShift compatibility
FROM registry.access.redhat.com/ubi9/python-39:latest

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY config/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/app.py .
COPY src/templates/ templates/

# OpenShift runs containers as arbitrary user IDs
# Ensure proper permissions
RUN chmod -R g+rwX /app

# Expose port 8080 (OpenShift default)
EXPOSE 8080

# Set environment variable
ENV PORT=8080

# Run the application
CMD ["python", "app.py"]
