FROM ghcr.io/astral-sh/uv:python3.12-bookworm

WORKDIR /app

COPY pyproject.toml uv.lock* ./

RUN uv sync --frozen --no-dev

COPY . .

EXPOSE 8000

CMD ["uv", "run", "fastapi", "run", "app/main.py", "--workers", "4", "--host", "0.0.0.0", "--port", "8000"]