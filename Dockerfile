ARG PYTHON_IMAGE=python:3.13-slim
FROM ${PYTHON_IMAGE}
ARG MODEL_VERSION

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    PROJECT_ROOT=/app
WORKDIR /app
COPY requirements-service.lock.txt .
RUN python -m pip install --no-cache-dir --only-binary=:all: -r requirements-service.lock.txt
COPY src/ src/
COPY service/ service/
COPY reports/bundle-manifest.json reports/golden-profiles.json reports/
COPY models/artifacts/${MODEL_VERSION}/bundle.joblib models/artifacts/${MODEL_VERSION}/bundle.joblib
USER 10001:10001
EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=5s --start-period=60s --retries=3 \
    CMD python -c "from urllib.request import urlopen; urlopen('http://127.0.0.1:8000/ready', timeout=3)"
CMD ["python", "-m", "uvicorn", "service.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--no-access-log"]
