FROM python:3.11.5-alpine

ENV PYTHONPATH=/app
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .