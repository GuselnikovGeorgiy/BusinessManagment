FROM python:3.12 as python-base

RUN mkdir -p /app/utils/certs
WORKDIR /app/utils/certs
RUN openssl genrsa -out jwt-private.pem 2048
RUN openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem

# Install uv
RUN pip install uv

WORKDIR /bms

COPY pyproject.toml /bms/

# Install dependencies with uv pip
RUN uv pip install .

COPY . .
