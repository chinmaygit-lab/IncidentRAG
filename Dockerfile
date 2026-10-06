FROM python:3.13-slim
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir ".[api]"
COPY data ./data
ENV INCIDENTRAG_DB=/data/incidentrag.db
EXPOSE 8000
CMD ["incidentrag", "serve", "--host", "0.0.0.0", "--port", "8000"]
