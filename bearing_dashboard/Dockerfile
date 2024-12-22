# Start with Python slim image - this keeps our container small
FROM python:3.10-slim

# These environment variables make Python work better in containers
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a directory for our application
WORKDIR /app

# Install system packages we need
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy and install requirements first - this improves Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now install gunicorn - we need this for production
RUN pip install gunicorn

# Copy the rest of our code
COPY . .

# Make our start script executable
RUN chmod +x /app/start.sh

# Create the static files directory
RUN mkdir -p staticfiles

# Collect static files
RUN python manage.py collectstatic --noinput

# Tell Docker what port we'll use
EXPOSE 8000

# Use gunicorn in production instead of Django's development server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "bearing_dashboard.wsgi:application"]