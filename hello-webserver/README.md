# hello-webserver

This image can run a simple webserver that returns with the word defined by the variable `APPENV` to requests on the resource `/hello`.
The default value for this variable is "world"

The image is based on nginx, and it includes configuration files templates inside [`templates`](./templates). Those files are then processed by nginx and placed inside `/etc/nginx/conf.d`.

## Building image

```bash
docker build -t hello-webserver .
```

## Running image

```bash
docker run -d --name hello-webserver -p 11888:11888 hello-webserver .
```

Overriding default values for environmental variables:

```bash
docker run -d \
    --name hello-webserver \
    -p 11888:11888 \
    -e SERVER_NAME=myserver.com \
    -e APPENV="There" \
    hello-webserver
```
