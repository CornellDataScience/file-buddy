# Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's source code into the container
COPY . .

# Set the environment variable for the directory to monitor
ENV MONITOR_DIR=/path/in/container

# Run the application
CMD ["python", "app.py"]
