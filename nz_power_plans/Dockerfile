ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk add --no-cache \
    python3 \
    py3-pydantic \
    py3-pydantic-settings \
    py3-fastapi \
    uvicorn \
    py3-sqlalchemy \
    py3-httpx \
    py3-beautifulsoup4 \
    py3-dateutil \
    py3-lxml

WORKDIR /app

COPY backend/app/ ./app/
COPY run.sh /

RUN chmod a+x /run.sh

EXPOSE 8080

CMD ["/run.sh"]
