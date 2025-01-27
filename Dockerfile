FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
COPY requirements-dev.txt .
# RUN pip install -r requirements.txt
RUN pip install -r requirements-dev.txt

COPY app/ /app

COPY pyproject.toml /app/pyproject.toml

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
