FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    php8.1-cli \
    php8.1-dev \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m whale

WORKDIR /app

COPY index.php /app/index.php
COPY whalecrypt.so /app/whalecrypt.so
COPY getflag /getflag

RUN chmod 111 /getflag && \
    chown -R whale:whale /app && \
    chmod -R 755 /app

RUN echo "extension=/app/whalecrypt.so" >> /etc/php/8.1/cli/php.ini

EXPOSE 8080

USER whale

CMD ["php", "-S", "0.0.0.0:8080", "-t", "/app"]