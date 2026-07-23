ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk add --no-cache python3 py3-pip py3-lxml

WORKDIR /app

COPY backend/requirements.txt .
RUN python3 -m venv /venv && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt

COPY backend/app/ ./app/
COPY run.sh /

RUN chmod a+x /run.sh

EXPOSE 8080

CMD ["/run.sh"]
