# FROM python:3.12-slim
FROM python:3.11.15-slim-bookworm

WORKDIR /app

COPY ./pyproject.toml /app/
COPY ./tj_express /app/tj_express

RUN pip install --no-cache-dir -e .

CMD ["python", "-m", "tj_express"]