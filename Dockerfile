FROM python:3.12.0-alpine3.18 as builder

# Отключает сохранение кеша питоном
ENV PYTHONDONTWRITEBYTECODE 1
# Если проект крашнется, выведется сообщение из-за какой ошибки это произошло
ENV PYTHONUNBUFFERED 1


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .