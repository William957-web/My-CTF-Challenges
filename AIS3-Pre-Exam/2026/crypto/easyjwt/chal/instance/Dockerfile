FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV MOZ_HEADLESS=1
ENV MOZ_DISABLE_CONTENT_SANDBOX=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        firefox-esr \
        fonts-liberation \
    && ln -sf /usr/bin/firefox-esr /usr/local/bin/firefox \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 ctf

WORKDIR /app

RUN pip install flask

COPY app.py jwt.py solve_pow.py ./

RUN mkdir -p /app/upload \
    && chown -R ctf:ctf /app

USER ctf

EXPOSE 5000

CMD ["python3", "app.py"]
