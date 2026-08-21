FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY dashboard_api.py .
EXPOSE 5001
CMD ["python", "dashboard_api.py"]
