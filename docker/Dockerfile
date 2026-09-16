# Optional container build - App Platform deploys this repo with the Python
# buildpack (see .do/app.yaml), and a Dockerfile in the repo root would take
# precedence over the buildpack, which is why this lives in docker/.
#
# Build from the repo root so the build context includes the app:
#   docker build -f docker/Dockerfile -t acrova-backend .
#   docker run --rm -p 8080:8080 --env-file .env acrova-backend

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

# Install dependencies first so the layer is cached when only app code changes.
# --locked fails the build if uv.lock is out of date with pyproject.toml.
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-default-groups --compile-bytecode

COPY . .

ENV ENVIRONMENT=production
ENV HOST=0.0.0.0
ENV PORT=8080
EXPOSE 8080

# HOST/PORT/ENVIRONMENT come from the environment; main.py reads them.
CMD ["sh", "-c", "uv run --no-sync alembic upgrade head && uv run --no-sync main.py"]
