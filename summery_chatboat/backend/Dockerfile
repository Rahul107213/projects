FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all code
COPY . .

# Expose backend internal port
EXPOSE 8000

# Run uvicorn on port 8000 internally
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
