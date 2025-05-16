#!/usr/bin/env bash

export DEBIAN_FRONTEND=noninteractive

echo "============================================="
echo "       🚀 TNLCM UPGRADE SCRIPT 🚀           "
echo "============================================="

echo "============================================="
echo "              GLOBAL VARIABLES               "
echo "============================================="
BACKEND_PATH="/opt/TNLCM_BACKEND"
BACKEND_DOTENV_FILE="${BACKEND_PATH}/.env"
BACKEND_VENV_PATH="${BACKEND_PATH}/.venv"
UV_PATH="/opt/uv"
UV_BIN="${UV_PATH}/uv"
MONGO_DATABASE="tnlcm-database"
TRIAL_NETWORK_COLLECTION="trial_network"
MONGO_EXPRESS_PATH="/opt/mongo-express"
MIN_TNLCM_VERSION="0.4.4"
START_TNLCM_VERSION="v0.4.5"

apt-get update

git -C ${BACKEND_PATH} fetch --tags

echo "Available versions:"

mapfile -t TNLCM_VERSIONS < <(git -C ${BACKEND_PATH} tag | sort -V | awk -v start="${START_TNLCM_VERSION}" '$0 >= start')

if [[ ${#TNLCM_VERSIONS[@]} -eq 0 ]]; then
    echo "No versions available"
    exit 1
fi

PS3="Select the version of TNLCM you want to upgrade to: "
select TARGET_VERSION in "${TNLCM_VERSIONS[@]}"; do
    if [[ -n "${TARGET_VERSION}" ]]; then
        break
    else
        echo "Invalid selection. Please try again"
    fi
done

TARGET_VERSION=${TARGET_VERSION#v}
CURRENT_VERSION=$(grep -oP 'version = "\K[^"]+' ${BACKEND_PATH}/pyproject.toml)

if [[ "$(printf "%s\n%s" "${CURRENT_VERSION}" "${MIN_TNLCM_VERSION}" | sort -V | head -n 1)" == "${CURRENT_VERSION}" && "${CURRENT_VERSION}" != "${MIN_TNLCM_VERSION}" ]]; then
    echo "You are on version ${CURRENT_VERSION}. You can't upgrade to version ${TARGET_VERSION}. Please redownload the latest version from the repository"
    exit 1
fi

if [[ "${CURRENT_VERSION}" == "${TARGET_VERSION}" ]]; then
    echo "You are already on version ${CURRENT_VERSION}"
    exit 1
fi

if [[ "${CURRENT_VERSION}" == "0.4.4" && "${TARGET_VERSION}" == "0.4.5" ]]; then

    echo "Starting upgrade from ${CURRENT_VERSION} to ${TARGET_VERSION}..."
    
    MONGO_EXPRESS_VERSION="v1.1.0-rc-3"
    POETRY_PATH="/opt/poetry"

    rm -r ${BACKEND_VENV_PATH}

    git -C ${BACKEND_PATH} checkout tags/v"${TARGET_VERSION}"

    curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=${UV_PATH} sh
    ${UV_BIN} --directory ${BACKEND_PATH} sync

    sed -i 's/^GITHUB_6G_LIBRARY_HTTPS_URL=/LIBRARY_HTTPS_URL=/' "${BACKEND_DOTENV_FILE}"
    sed -i 's/^GITHUB_6G_LIBRARY_BRANCH=/LIBRARY_BRANCH=/' "${BACKEND_DOTENV_FILE}"
    sed -i 's/^GITHUB_6G_LIBRARY_REPOSITORY_NAME=/LIBRARY_REPOSITORY_NAME=/' "${BACKEND_DOTENV_FILE}"
    sed -i 's/^GITHUB_6G_SANDBOX_SITES_HTTPS_URL=/SITES_HTTPS_URL=/' "${BACKEND_DOTENV_FILE}"
    sed -i 's/^GITHUB_6G_SANDBOX_SITES_REPOSITORY_NAME=/SITES_REPOSITORY_NAME=/' "${BACKEND_DOTENV_FILE}"
    sed -i '/^GITHUB_6G_SANDBOX_SITES_BRANCH=/d' "${BACKEND_DOTENV_FILE}"

    cat <<EOF > /etc/systemd/system/tnlcm-backend.service
[Unit]
Description=TNLCM Backend
After=network.target

[Service]
Type=simple
WorkingDirectory=${BACKEND_PATH}/
ExecStart=/bin/bash -c '${UV_BIN} run gunicorn -c conf/gunicorn_conf.py'
Restart=always
User=root
Group=root

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl restart tnlcm-backend.service

    mongosh --eval "
    db.getSiblingDB('${MONGO_DATABASE}').${TRIAL_NETWORK_COLLECTION}.updateMany({}, {
        \$rename: {
            'github_6g_library_https_url': 'library_https_url',
            'github_6g_library_commit_id': 'library_commit_id',
            'github_6g_sandbox_sites_https_url': 'sites_https_url',
            'github_6g_sandbox_sites_commit_id': 'sites_commit_id'
        }
    });
    "

    rm -r ${MONGO_EXPRESS_PATH}-*
    git clone --depth 1 --branch ${MONGO_EXPRESS_VERSION} -c advice.detachedHead=false https://github.com/mongo-express/mongo-express.git ${MONGO_EXPRESS_PATH}
    cd ${MONGO_EXPRESS_PATH} || exit
    yarn install
    yarn build

    cat <<EOF > /etc/systemd/system/mongo-express.service
[Unit]
Description=Mongo Express

[Service]
Type=simple
WorkingDirectory=${MONGO_EXPRESS_PATH}
ExecStart=/bin/bash -ac 'source ${BACKEND_PATH}/.env && yarn start'
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl restart mongo-express.service

    rm -r ${POETRY_PATH}

    echo "Upgrade to version ${TARGET_VERSION} completed"

fi

CURRENT_VERSION=$(grep -oP 'version = "\K[^"]+' ${BACKEND_PATH}/pyproject.toml)

if [[ "${CURRENT_VERSION}" == "0.4.5" && "${TARGET_VERSION}" == "0.5.0" ]]; then

    echo "Starting upgrade from ${CURRENT_VERSION} to ${TARGET_VERSION}..."

    apt install -y ansible-core

    git -C ${BACKEND_PATH} checkout tags/"v${TARGET_VERSION}"

    echo "Syncing backend dependencies"
    ${UV_BIN} --directory ${BACKEND_PATH} sync

    echo "Remove unnecessary environment variables"
    sed -i '/^TNLCM_LOG_LEVEL=/d' "${BACKEND_DOTENV_FILE}"
    sed -i '/^GUNICORN_WORKERS=/d' "${BACKEND_DOTENV_FILE}"
    sed -i '/^TWO_FACTOR_AUTH=/d' "${BACKEND_DOTENV_FILE}"
    sed -i '/^MAIL_SERVER=/d' "${BACKEND_DOTENV_FILE}"
    sed -i '/^MAIL_PORT=/d' "${BACKEND_DOTENV_FILE}"
    sed -i '/^MAIL_USE_TLS=/d' "${BACKEND_DOTENV_FILE}"
    sed -i '/^MAIL_USE_SSL=/d' "${BACKEND_DOTENV_FILE}"
    sed -i '/^MAIL_USERNAME=/d' "${BACKEND_DOTENV_FILE}"
    sed -i '/^MAIL_PASSWORD=/d' "${BACKEND_DOTENV_FILE}"
    sed -i '/^TNLCM_CALLBACK=/d' "${BACKEND_DOTENV_FILE}"

    echo "Add new environment variables"
    {
        echo 'TNLCM_CONSOLE_LOG_LEVEL="INFO"'
        echo 'TRIAL_NETWORK_LOG_LEVEL="INFO"'
        echo 'JENKINS_TNLCM_DIRECTORY="TNLCM"'
        echo "TNLCM_CALLBACK=\"http://\${TNLCM_HOST}:\${TNLCM_PORT}/api/v1/callback\""
    } >> "${BACKEND_DOTENV_FILE}"

    echo "Insert new values for the next variables in the .env"
    read -r -p "Branch of the sites repository. SITES_BRANCH: " SITES_BRANCH
    read -r -p "Directory inside of the branch of the sites repository. SITES_DEPLOYMENT_SITE: " SITES_DEPLOYMENT_SITE
    read -r -p "Token to decrypt the yaml from the deployment site. SITES_DEPLOYMENT_SITE_TOKEN: " SITES_DEPLOYMENT_SITE_TOKEN
    {
        echo "SITES_BRANCH=${SITES_BRANCH}"
        echo "SITES_DEPLOYMENT_SITE=${SITES_DEPLOYMENT_SITE}"
        echo "SITES_DEPLOYMENT_SITE_TOKEN=${SITES_DEPLOYMENT_SITE_TOKEN}"
    } >> "${BACKEND_DOTENV_FILE}"

    
    echo "Remove verification_token collection"
    mongosh --eval "
        db.getSiblingDB('${MONGO_DATABASE}').verification_token.drop();
    "

    echo "Remove input and output fields from trial_network collection"
    mongosh --eval "
        db.getSiblingDB('${MONGO_DATABASE}').${TRIAL_NETWORK_COLLECTION}.updateMany({}, {
            \$unset: {
                input: '',
                output: ''
            }
        });
    "

    echo "Rename jenkins_deploy_pipeline and jenkins_destroy_pipeline to jenkins_deploy and jenkins_destroy"
    mongosh --eval "
        db.getSiblingDB('${MONGO_DATABASE}').${TRIAL_NETWORK_COLLECTION}.updateMany({}, [
            {
                \$set: {
                    jenkins_deploy: { pipeline_name: '\$jenkins_deploy_pipeline' },
                    jenkins_destroy: { pipeline_name: '\$jenkins_destroy_pipeline' }
                }
            },
            {
                \$unset: ['jenkins_deploy_pipeline', 'jenkins_destroy_pipeline']
            }
        ]);
    "

    echo "Restart TNLCM Backend"
    systemctl restart tnlcm-backend.service

    echo "Upgrade to version ${TARGET_VERSION} completed"

fi

CURRENT_VERSION=$(grep -oP 'version = "\K[^"]+' ${BACKEND_PATH}/pyproject.toml)

if [[ "${CURRENT_VERSION}" == "0.5.0" && "${TARGET_VERSION}" == "0.5.1" ]]; then

    echo "Starting upgrade from ${CURRENT_VERSION} to ${TARGET_VERSION}..."

    git -C ${BACKEND_PATH} checkout tags/"v${TARGET_VERSION}"

    echo "Syncing backend dependencies"
    ${UV_BIN} --directory ${BACKEND_PATH} sync

    echo "Restart TNLCM Backend"
    systemctl restart tnlcm-backend.service

    echo "Upgrade to version ${TARGET_VERSION} completed"
fi

CURRENT_VERSION=$(grep -oP 'version = "\K[^"]+' ${BACKEND_PATH}/pyproject.toml)

if [[ "${CURRENT_VERSION}" == "0.5.1" && "${TARGET_VERSION}" == "0.5.2" ]]; then

    echo "Starting upgrade from ${CURRENT_VERSION} to ${TARGET_VERSION}..."

    git -C ${BACKEND_PATH} checkout tags/"v${TARGET_VERSION}"

    echo "Syncing backend dependencies"
    ${UV_BIN} --directory ${BACKEND_PATH} sync

    echo "Restart TNLCM Backend"
    systemctl restart tnlcm-backend.service

    echo "Upgrade to version ${TARGET_VERSION} completed"
fi
