#!/usr/bin/env bash

echo "Start TNLCM, mongo and mongo-express installation"

export DEBIAN_FRONTEND=noninteractive

apt-get update

echo "--------------- Install git ---------------"
if ! git --version; then
    apt-get install -y git
fi

echo "--------------- Install python ---------------"
PYTHON_VERSION="3.13"
PYTHON_BIN="python${PYTHON_VERSION}"

if ! python3 --version | awk '{print $2}' | grep -qE '^3\.1[3-9]|^[4-9]'; then
    add-apt-repository ppa:deadsnakes/ppa -y
    apt-get install python${PYTHON_VERSION}-full -y
fi

apt install -y ${PYTHON_BIN}-venv

echo "--------------- Install Poetry ---------------"
POETRY_FOLDER="/opt/poetry"
POETRY_BIN="/opt/poetry/bin/poetry"
curl -sSL https://install.python-poetry.org | POETRY_HOME=${POETRY_FOLDER} python3 -
${POETRY_BIN} config virtualenvs.in-project true

echo "--------------- Clone TNLCM ---------------"
TNLCM_FOLDER="/opt/TNLCM"
TNLCM_ENV_FILE=${TNLCM_FOLDER}/.env

git clone https://github.com/6G-SANDBOX/TNLCM ${TNLCM_FOLDER}
${POETRY_BIN} install --no-root --directory ${TNLCM_FOLDER}

cp ${TNLCM_FOLDER}/.env.template ${TNLCM_FOLDER}/.env

# TODO: Fill in the environment variables
TNLCM_ADMIN_USER=""
TNLCM_ADMIN_PASSWORD="" 
TNLCM_HOST=""
JENKINS_HOST=""
JENKINS_USERNAME=""
JENKINS_PASSWORD=""
JENKINS_TOKEN=""
# Ansible password to decrypt file 6G-Sandbox-Sites (not use \" or \' or \`)
SITES_TOKEN=''

sed -i "s/^TNLCM_ADMIN_USER=.*/TNLCM_ADMIN_USER=\"${TNLCM_ADMIN_USER}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^TNLCM_ADMIN_PASSWORD=.*/TNLCM_ADMIN_PASSWORD=\"${TNLCM_ADMIN_PASSWORD}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^TNLCM_HOST=.*/TNLCM_HOST=\"${TNLCM_HOST}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^JENKINS_HOST=.*/JENKINS_HOST=\"${JENKINS_HOST}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^JENKINS_USERNAME=.*/JENKINS_USERNAME=\"${JENKINS_USERNAME}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^JENKINS_PASSWORD=.*/JENKINS_PASSWORD=\"${JENKINS_PASSWORD}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^JENKINS_TOKEN=.*/JENKINS_TOKEN=\"${JENKINS_TOKEN}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^SITES_TOKEN=.*/SITES_TOKEN='${SITES_TOKEN}'/" ${TNLCM_ENV_FILE}

echo "--------------- Install mongo ---------------"
MONGODB_VERSION="8.0"

apt-get install -y gnupg curl
curl -fsSL https://www.mongodb.org/static/pgp/server-${MONGODB_VERSION}.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-${MONGODB_VERSION}.gpg --dearmor
echo "deb [ arch=amd64 signed-by=/usr/share/keyrings/mongodb-server-${MONGODB_VERSION}.gpg ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -sc 2> /dev/null)/mongodb-org/${MONGODB_VERSION} multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-${MONGODB_VERSION}.list
apt-get update
apt-get install -y mongodb-org
systemctl enable --now mongod

echo "--------------- Install yarn ---------------"
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
apt-get update
apt-get install -y yarn

echo "--------------- Install dotenv library ---------------"
YARN_GLOBAL_LIBRARIES="/opt/yarn_global"

yarn config set global-folder ${YARN_GLOBAL_LIBRARIES}
yarn global add dotenv

echo "--------------- Load TNLCM database ---------------"
mongosh --file ${TNLCM_FOLDER}/core/database/tnlcm-structure.js

echo "--------------- Install nodejs ---------------"
curl -fsSL https://deb.nodesource.com/setup_lts.x -o nodesource_setup.sh
bash nodesource_setup.sh
apt-get install -y nodejs
rm nodesource_setup.sh

echo "--------------- Install mongo-express ---------------"
MONGO_EXPRESS_VERSION="v1.0.2"
MONGO_EXPRESS_FOLDER=/opt/mongo-express-${MONGO_EXPRESS_VERSION}

git clone --depth 1 --branch release/${MONGO_EXPRESS_VERSION} -c advice.detachedHead=false https://github.com/mongo-express/mongo-express.git ${MONGO_EXPRESS_FOLDER}
cd ${MONGO_EXPRESS_FOLDER}
yarn install
yarn build
cd

echo "--------------- Start mongo-express service ---------------"
cat > /etc/systemd/system/mongo-express.service << EOF
[Unit]
Description=mongo-express

[Service]
Type=simple
WorkingDirectory=${MONGO_EXPRESS_FOLDER}
ExecStart=/bin/bash -ac 'source ${TNLCM_ENV_FILE} && yarn start'
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl enable --now mongo-express.service

${POETRY_BIN} shell --directory ${TNLCM_FOLDER}

echo "TNLCM, mongo and mongo-express installed"