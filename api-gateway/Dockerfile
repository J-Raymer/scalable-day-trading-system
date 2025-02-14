FROM nginx:alpine

# Cache and routing dependencies
RUN apk add --no-cache \
    lua5.1 \
    lua5.1-cjson \
    lua-resty-http \
    nginx-mod-http-lua \
    && rm -rf /var/cache/apk/*


COPY nginx.conf /etc/nginx/nginx.conf
CMD ["nginx", "-g", "daemon off;"]

