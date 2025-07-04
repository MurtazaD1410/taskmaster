# This is the blueprint for your Django app container.

# Use an official Python image as a starting point.
FROM python:3.10-slim

# Set environment variables to make Python run better inside Docker.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container.
WORKDIR /app

# Copy the file that lists your Python libraries.
# This command will now succeed because you've created the file.
COPY requirements.txt .

# Install those libraries, plus Gunicorn for running the server.
RUN pip install --no-cache-dir gunicorn psycopg2-binary
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your Django project code into the container.
COPY . .

# Tell Docker that your app will listen on port 8000.
EXPOSE 8000

# The default command to run when the container starts.
# Replace 'yourprojectname' with the name of your Django project folder (the one with settings.py).
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "yourprojectname.wsgi:application"]