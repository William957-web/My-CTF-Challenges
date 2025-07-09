FROM php:8.0.11-fpm-alpine3.13

# Copy the php config file
COPY ./docker/php/php-fpm.conf /usr/local/etc/php-fpm.d/www.conf

# Copy the application code
COPY ./public /app/public

# Create the flag file with correct permissions
RUN echo 'NHNC{old_school_"features"_lead_to_tragic}' > /flag_yep_u_get_this && \
    chmod 444 /flag_yep_u_get_this

# Create user `chal` with no password and no shell
RUN adduser -D -H -s /sbin/nologin chal

# Set ownership of /app and switch to chal user
RUN chown -R chal:chal /app

# Set working directory
WORKDIR /app

# Use unprivileged user
USER chal

# Optional: expose port if needed
# EXPOSE 9000

VOLUME ["/app"]
