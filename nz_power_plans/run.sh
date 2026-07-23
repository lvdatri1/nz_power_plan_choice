#!/usr/bin/env bash

set -e
set +u

CONFIG_PATH=/data/options.json

if [ -f "${CONFIG_PATH}" ]; then
    echo "[startup] Reading options from ${CONFIG_PATH}"
    PLAN_ID=$(jq -r '.plan_id // empty' "${CONFIG_PATH}")
    IMPORT_SENSOR=$(jq -r '.import_sensor // empty' "${CONFIG_PATH}")
    EXPORT_SENSOR=$(jq -r '.export_sensor // empty' "${CONFIG_PATH}")

    [ -n "${PLAN_ID}" ] && export NZ_PLAN_ID="${PLAN_ID}" && echo "[startup] NZ_PLAN_ID=${PLAN_ID}"
    [ -n "${IMPORT_SENSOR}" ] && export NZ_IMPORT_SENSOR="${IMPORT_SENSOR}" && echo "[startup] NZ_IMPORT_SENSOR=${IMPORT_SENSOR}"
    [ -n "${EXPORT_SENSOR}" ] && export NZ_EXPORT_SENSOR="${EXPORT_SENSOR}" && echo "[startup] NZ_EXPORT_SENSOR=${EXPORT_SENSOR}"

    TOKEN="${SUPERVISOR_TOKEN}"
    if [ -z "${TOKEN}" ] && [ -n "${HASSIO_TOKEN}" ]; then
        TOKEN="${HASSIO_TOKEN}"
        echo "[startup] Using HASSIO_TOKEN"
    fi
    if [ -z "${TOKEN}" ] && [ -f /var/run/supervisor/token ]; then
        TOKEN=$(cat /var/run/supervisor/token)
        echo "[startup] Read token from /var/run/supervisor/token"
    fi
    if [ -z "${TOKEN}" ] && [ -f /run/s6/container_environment/SUPERVISOR_TOKEN ]; then
        TOKEN=$(cat /run/s6/container_environment/SUPERVISOR_TOKEN)
        echo "[startup] Read token from s6 env"
    fi

    if [ -n "${TOKEN}" ]; then
        export HA_URL="http://supervisor/core"
        export HA_TOKEN="${TOKEN}"
        echo "[startup] HA configured via supervisor token"
    else
        echo "[startup] WARNING: no supervisor token found"
    fi
else
    echo "[startup] WARNING: ${CONFIG_PATH} not found, using defaults"
fi

cd /app
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --log-level info
