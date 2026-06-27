FROM nginx:1.30.3-alpine3.23

COPY ./utility/nginx/nginx.conf /etc/nginx/nginx.conf
COPY ./utility/nginx/default.conf.template /etc/nginx/default.conf.template
COPY ./utility/nginx/default-ssl.conf.template /etc/nginx/default-ssl.conf.template
COPY ./utility/nginx/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
