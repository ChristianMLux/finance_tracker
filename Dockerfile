# Dockerfile.backend
FROM python:3.10-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend ./backend
# WICHTIG: Port muss über die Variable $PORT laufen (Cloud Run Requirement)
ENV PORT=8080
EXPOSE 8080
# Use shell form to ensure $PORT is expanded
CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT}"]