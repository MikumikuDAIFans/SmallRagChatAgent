FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (excludes data/ and doc/ via .dockerignore)
COPY . .

# Ensure data directory exists for volume mount
RUN mkdir -p data

# Expose the port (Optional, actual port is controlled by APP_PORT env)
# EXPOSE 8000

# Run the server using python to leverage APP_PORT in server.py
CMD ["python", "server.py"]
