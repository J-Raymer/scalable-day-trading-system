FROM openresty/openresty:alpine

# Cache and routing dependencies
RUN apk add --no-cache \
    lua5.1 \
    lua5.1-cjson \
    lua-resty-http \
    nginx-mod-http-lua \
    && rm -rf /var/cache/apk/*

RUN apk info

COPY api-gateway/nginx.conf /usr/local/openresty/nginx/conf/nginx.conf
CMD ["openresty", "-g", "daemon off;"]

