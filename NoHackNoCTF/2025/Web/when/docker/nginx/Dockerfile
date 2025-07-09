FROM nginx:1.17.8-alpine

# Copy the public directory
COPY ./public/ /app/public/
COPY ./file /app/file
COPY ./index.php~ /app
COPY ./socket-test-8cb09a.php~ /app
COPY ./nginx.conf /app

# Copy the nginx config file
COPY ./docker/nginx/nginx.conf /etc/nginx/conf.d/default.conf
