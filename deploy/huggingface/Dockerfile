# Hugging Face Space (Docker SDK) for the fraud risk scoring API.
# All files sit flat in the Space (easy web upload); this file rebuilds the project layout inside the image.

# 1. Python 3.13 = the same Python that trained the model on Kaggle
FROM python:3.13-slim

# 2. LightGBM needs the OpenMP runtime (libgomp1)
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 3. Hugging Face runs the container as user ID 1000
RUN useradd -m -u 1000 user
WORKDIR /home/user/app

# 4. Pinned libraries first (cached layer)
COPY requirements-serve.txt .
RUN pip install --no-cache-dir -r requirements-serve.txt

# 5. Rebuild the folders the code expects: src/, api/, models/
COPY --chown=user fraud_service.py ./src/
COPY --chown=user main.py demo.html ./api/
COPY --chown=user final_lightgbm_tuned.joblib isotonic_calibrator.joblib drift_reference.json feature_info.json ./models/
RUN touch src/__init__.py api/__init__.py

# 6. Run as the non-root user; give caches a writable place
USER user
ENV MODEL_DIR=/home/user/app/models \
    NUMBA_CACHE_DIR=/tmp/numba_cache \
    MPLCONFIGDIR=/tmp/matplotlib

# 7. Hugging Face sends web traffic to port 7860
EXPOSE 7860
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
