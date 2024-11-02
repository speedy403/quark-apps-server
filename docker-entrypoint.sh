#!/bin/sh

# Substitute environment variables in the nginx configuration file
envsubst '$PORT $ADMIN_PORT $HOST' < /etc/nginx/nginx.conf > /etc/nginx/nginx.conf.tmp
mv /etc/nginx/nginx.conf.tmp /etc/nginx/nginx.conf
rm -f /etc/nginx/nginx.conf.tmp

# Continue with the CMD
exec "$@"