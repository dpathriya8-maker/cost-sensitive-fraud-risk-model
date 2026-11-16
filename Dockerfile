# Fraud risk scoring API in a container.
# Build:  docker build -t fraud-api .
# Run:    docker run -p 8000:8000 fraud-api      → open http://127.0.0.1:8000/docs
# Needs the 4 trained files in models/ first (run the notebook up to §10).

# 1. Small official Linux image with Python 3.12 already installed
FROM python:3.12-slim

# 2. LightGBM needs the OpenMP runtime (libgomp1), which the slim image doesn't include
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 3. Folder inside the container where our app lives
WORKDIR /app

# 4. Library list FIRST, then install → this slow layer is cached when only code changes
COPY requirements-serve.txt .
RUN pip install --no-cache-dir -r requirements-serve.txt

# 5. Our code and the trained files (change often → copied last)
COPY src/ ./src/
COPY api/ ./api/
COPY models/ ./models/

# 6. Don't run as the all-powerful root user
RUN useradd --create-home appuser
USER appuser

# 7. Tell the app where the model files are, and which door (port) it listens on
ENV MODEL_DIR=/app/models
EXPOSE 8000

# 8. Start the server; 0.0.0.0 = accept requests coming from outside the container
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
