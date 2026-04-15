FROM python:3.11-slim

WORKDIR /app

# Copy requirements file into the container
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the project
COPY . /app

EXPOSE 80

CMD ["python", "app.py"]
