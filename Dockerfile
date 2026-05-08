# Imagem para Render (Docker). Evita confundir Start Command com "pip install".
# No painel: env → Docker / Runtime = Docker; Build: automático; Start: vazio (usa este CMD).

FROM python:3.11-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Render passa PORT; fallback 8000 útil em testes locais: docker run -p 8000:8000 -e PORT=8000 ...
CMD ["sh", "-c", "exec uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]
