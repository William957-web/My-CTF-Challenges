FROM php:8.3-apache

WORKDIR /var/www/html

RUN a2enmod rewrite

COPY . /var/www/html/
COPY readflag.c /

RUN chown -R www-data:www-data /var/www/html \
    && chmod -R 775 /var/www/html && rm /var/www/html/Dockerfile && rm /var/www/html/readflag.c \
    && apt-get update && apt-get install -y gcc && gcc /readflag.c -o /readflag && rm /readflag.c && chmod 111 /readflag

EXPOSE 80

CMD ["apache2-foreground"]
