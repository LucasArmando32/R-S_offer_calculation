FROM python:3.11-slim

WORKDIR /app

# Copy requirements file into the container
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the project
COPY . /app

EXPOSE 8000

CMD ["python", "app.py", gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "app:app"]
