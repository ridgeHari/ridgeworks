# Use the official Python base image
FROM python:3.9

# Install the SQLite client
RUN apt-get update && apt-get install -y sqlite3

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install project dependencies
RUN pip install -r requirements.txt

# Copy the entire project directory to the container
COPY . .

# Expose the default Django development server port
EXPOSE 8002

# Run the Django development server when the container starts
CMD python manage.py runserver 0.0.0.0:8000
