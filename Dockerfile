FROM python:3.12-slim AS base
RUN apt-get -y update; apt-get -y install curl
RUN pip install poetry==1.7.1

FROM base AS codebase
WORKDIR /app
COPY . .

FROM codebase AS development
RUN poetry install --no-dev
RUN poetry run prisma generate
CMD poetry run dev