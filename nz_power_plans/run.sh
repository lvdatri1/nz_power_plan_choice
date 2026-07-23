#!/usr/bin/env bashio
# shellcheck shell=bash

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

    if [ -n "${SUPERVISOR_TOKEN}" ]; then
        export HA_URL="http://supervisor/core"
        export HA_TOKEN="${SUPERVISOR_TOKEN}"
        echo "[startup] HA configured via supervisor token"
    else
        echo "[startup] WARNING: SUPERVISOR_TOKEN not set"
    fi
else
    echo "[startup] WARNING: ${CONFIG_PATH} not found, using defaults"
fi

cd /app
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --log-level info
