FROM php:8.3-apache

WORKDIR /var/www/html

RUN a2enmod rewrite

COPY . /var/www/html/

RUN chown -R www-data:www-data /var/www/html \
    && chmod -R 775 /var/www/html && rm /var/www/html/Dockerfile

EXPOSE 80

CMD ["apache2-foreground"]
