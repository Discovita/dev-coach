# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /server

# Copy the dependencies file to the working directory
COPY ./requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the content of the local src directory to the working directory
COPY . .

# Create static files directory
RUN mkdir -p .staticfiles

ENV DJANGO_SETTINGS_MODULE=settings.development

# Collect static files
RUN python manage.py collectstatic --noinput

# Make port 81 available to the world outside this container
EXPOSE 81

# Run the Django application with Gunicorn 
# NOTE: Added the timeout to extend the default timeout of 60 seconds because to allow more time for
# LLM processing. 
CMD ["gunicorn", "asgi:application", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:81", "--timeout", "600"]