# Start with Python
FROM python:3.10-slim

# Environment variables which make Python work better in containers
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a directory for application
WORKDIR /app

# Install system packages 
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy and install requirements first 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now install gunicorn for production
RUN pip install gunicorn

# Copy the rest of code
COPY . .

# Make start script executable
RUN chmod +x /app/start.sh

# Create the static files directory
RUN mkdir -p staticfiles

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "bearing_dashboard.wsgi:application"]