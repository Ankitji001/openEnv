FROM python:3.10-slim

WORKDIR /app

# Install necessary libraries
RUN pip install --no-cache-dir openenv-core openai pydantic fastapi uvicorn

# Copy project files
COPY . .

# Environment setups
ENV PYTHONPATH=/app

CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]
