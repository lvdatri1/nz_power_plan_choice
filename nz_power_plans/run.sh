#!/usr/bin/env bashio
# shellcheck shell=bash

set -e

CONFIG_PATH=/data/options.json

if bashio::fs.file_exists "${CONFIG_PATH}"; then
    PLAN_ID=$(bashio::config 'plan_id')
    IMPORT_SENSOR=$(bashio::config 'import_sensor')
    EXPORT_SENSOR=$(bashio::config 'export_sensor')

    export NZ_PLAN_ID="${PLAN_ID}"
    export NZ_IMPORT_SENSOR="${IMPORT_SENSOR}"
    export NZ_EXPORT_SENSOR="${EXPORT_SENSOR}"

    if bashio::var.has_value "${SUPERVISOR_TOKEN}"; then
        export HA_URL="${SUPERVISOR_URL}"
        export HA_TOKEN="${SUPERVISOR_TOKEN}"
    fi
fi

cd /app
exec python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --log-level info
