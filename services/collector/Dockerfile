FROM python:3.10-slim

WORKDIR /app

# Explicitly add the working directory to the PYTHONPATH
# This ensures that 'app' can be imported as a top-level package.
ENV PYTHONPATH "${PYTHONPATH}:/app"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run the main script as a module within the 'app' package
CMD ["python", "-m", "app.main"]
