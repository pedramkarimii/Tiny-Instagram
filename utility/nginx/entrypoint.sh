#!/bin/sh
set -eu

domain="${DOMAIN_NAME:-localhost}"

if [ -f "/etc/letsencrypt/live/${domain}/fullchain.pem" ]; then
    sed "s/__DOMAIN_NAME__/${domain}/g" /etc/nginx/default-ssl.conf.template > /etc/nginx/conf.d/default.conf
else
    cp /etc/nginx/default.conf.template /etc/nginx/conf.d/default.conf
fi

exec nginx -g "daemon off;"
