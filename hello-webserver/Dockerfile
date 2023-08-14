FROM nginx:1.23.4

ENV APPENV="world"

ENV SERVER_NAME="localhost"

COPY templates /etc/nginx/templates

EXPOSE 11888

ENTRYPOINT ["/docker-entrypoint.sh", "nginx", "-g", "daemon off;"]
