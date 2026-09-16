FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV ENVIRONMENT=production
ENV HOST=0.0.0.0
ENV PORT=8080
EXPOSE 8080

# HOST/PORT/ENVIRONMENT come from the environment; main.py reads them.
CMD ["sh", "-c", "alembic upgrade head && python main.py"]
