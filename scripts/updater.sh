#!/usr/bin/env bash

export DEBIAN_FRONTEND=noninteractive

BACKEND_PATH="/opt/TNLCM_BACKEND"
TNLCM_ENV_FILE=${BACKEND_PATH}/.env

TNLCM_VERSION=$(grep -oP 'version = "\K[^"]+' ${BACKEND_PATH}/pyproject.toml)

if [[ $(echo "${TNLCM_VERSION} <= 0.4.4" | bc) -eq 1 ]]; then
    echo "TNLCM version is ${TNLCM_VERSION}"
    echo "TNLCM version must be greater than 0.4.4"
    exit 1
fi

echo "TNLCM version is ${TNLCM_VERSION}"