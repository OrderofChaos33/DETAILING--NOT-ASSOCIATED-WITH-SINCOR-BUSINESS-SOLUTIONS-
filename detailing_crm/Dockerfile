# Build from the REPO ROOT so the frontend ships with the API:
#   docker build -f detailing_crm/Dockerfile .
FROM python:3.12-slim
WORKDIR /app
COPY detailing_crm/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY detailing_crm/app ./app
COPY frontend ./frontend
ENV PYTHONUNBUFFERED=1
ENV FRONTEND_DIR=/app/frontend
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
