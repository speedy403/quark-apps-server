# Get the latest NGINX image
FROM nginx:latest

# Install Python and necessary packages
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y python3 python3-pip && \
    apt-get install -y python3-flask python3-flask-cors && \
    apt-get install -y python3-pymysql && \
    apt-get install -y gunicorn

# Expose port 3306 for MySQL
EXPOSE 3306

# Set the working directory to the flask app
WORKDIR /app

# Copy the flask app
COPY python /app

# Copy the flask templates
COPY admin/templates /app/templates

# Copy the website content
COPY html /usr/share/nginx/html
COPY admin /usr/share/nginx/admin
COPY css /usr/share/nginx/html/css
COPY js /usr/share/nginx/html/js

# Copy the favicon
COPY assets/favicon.ico /usr/share/nginx/html/favicon.ico
COPY assets/favicon.ico /usr/share/nginx/admin/favicon.ico

# Copy the NGINX configuration files
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Run the entrypoint script
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]

# Start the NGINX and Gunicorn services
CMD ["sh", "-c", "gunicorn -w 4 -b 0.0.0.0:5000 db_reader:app --timeout 3600 \
        & gunicorn -w 4 -b 0.0.0.0:5001: hash_api:app --timeout 3600 \
        & gunicorn -w 4 -b 0.0.0.0:5002: db_admin:app --timeout 3600 \
        & python3 /app/db_init.py \
        & python3 /app/db_cleaner.py \
        & nginx -g 'daemon off;'"]