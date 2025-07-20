# Use the official Python base image
FROM python:3.12.9-slim

# Set the working directory in the container
WORKDIR /app
ENV APP_ENV=production

# Copy the requirements file to the container
COPY ./requirements.txt .

# Install the Python dependencies
RUN pip install -r requirements.txt

# Copy the Django project to the container
COPY . .

# Expose the port that Django runs on
EXPOSE 8000

# Set the command to run when the container starts
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
