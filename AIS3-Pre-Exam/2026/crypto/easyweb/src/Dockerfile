FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir Flask==3.0.3 pycryptodome==3.20.0 \
    && useradd --create-home --shell /usr/sbin/nologin ctf

COPY app.py /app/app.py

RUN chown -R ctf:ctf /app

USER ctf

EXPOSE 48763

CMD ["python", "app.py"]
