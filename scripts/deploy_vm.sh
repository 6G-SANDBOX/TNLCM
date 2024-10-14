#!/usr/bin/env bash

echo "Start TNLCM, mongo and mongo-express installation"

export DEBIAN_FRONTEND=noninteractive

apt-get update

# Install git
echo "--------------- Install git ---------------"
if ! git --version; then
    apt-get install -y git
fi

# Install python
echo "--------------- Install python ---------------"
PYTHON_VERSION="3.13.0"
PYTHON_BIN="python${PYTHON_VERSION}"

apt install -y python${PYTHON_VERSION}-venv

if ! python3 --version | awk '{print $2}' | grep -qE '^3\.1[3-9]|^[4-9]'; then
    wget "https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz"
    tar xvf Python-${PYTHON_VERSION}.tgz
    cd Python-${PYTHON_VERSION}/
    ./configure --enable-optimizations
    make altinstall
    ${PYTHON_BIN} -m ensurepip --default-pip
    ${PYTHON_BIN} -m pip install --upgrade pip setuptools wheel
    cd
    rm -rf Python-${PYTHON_VERSION}*
fi

# Clone and install TNLCM libraries
echo "--------------- Clone TNLCM ---------------"
# TNLCM_VERSION="v0.3.2"
TNLCM_FOLDER="/opt/TNLCM"
TNLCM_ENV_FILE=${TNLCM_FOLDER}/.env

# git clone --depth 1 --branch release/${TNLCM_VERSION} -c advice.detachedHead=false https://github.com/6G-SANDBOX/TNLCM.git ${TNLCM_FOLDER}
git clone https://github.com/6G-SANDBOX/TNLCM ${TNLCM_FOLDER}
cp ${TNLCM_FOLDER}/.env.template ${TNLCM_FOLDER}/.env
${PYTHON_BIN} -m venv ${TNLCM_FOLDER}/venv
source ${TNLCM_FOLDER}/venv/bin/activate
${TNLCM_FOLDER}/venv/bin/pip install -r ${TNLCM_FOLDER}/requirements.txt
deactivate

# TODO: Fill in the environment variables
TNLCM_ADMIN_USER=""
TNLCM_ADMIN_PASSWORD="" 
TNLCM_HOST=""
JENKINS_HOST=""
JENKINS_USERNAME=""
JENKINS_PASSWORD=""
JENKINS_TOKEN=""
SITES_TOKEN=''

sed -i "s/^TNLCM_ADMIN_USER=.*/TNLCM_ADMIN_USER=\"${TNLCM_ADMIN_USER}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^TNLCM_ADMIN_PASSWORD=.*/TNLCM_ADMIN_PASSWORD=\"${TNLCM_ADMIN_PASSWORD}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^TNLCM_HOST=.*/TNLCM_HOST=\"${TNLCM_HOST}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^JENKINS_HOST=.*/JENKINS_HOST=\"${JENKINS_HOST}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^JENKINS_USERNAME=.*/JENKINS_USERNAME=\"${JENKINS_USERNAME}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^JENKINS_PASSWORD=.*/JENKINS_PASSWORD=\"${JENKINS_PASSWORD}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^JENKINS_TOKEN=.*/JENKINS_TOKEN=\"${JENKINS_TOKEN}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^SITES_TOKEN=.*/SITES_TOKEN='${SITES_TOKEN}'/" ${TNLCM_ENV_FILE}

# Install mongo
echo "--------------- Install mongo ---------------"
MONGODB_VERSION="7.0"

apt-get install -y gnupg curl
curl -fsSL https://pgp.mongodb.com/server-${MONGODB_VERSION}.asc |  sudo gpg -o /usr/share/keyrings/mongodb-server-${MONGODB_VERSION}.gpg --dearmor
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-${MONGODB_VERSION}.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/${MONGODB_VERSION} multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-${MONGODB_VERSION}.list
apt-get update
apt-get install -y mongodb-org
systemctl enable --now mongod

# Install yarn
echo "--------------- Install yarn ---------------"
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
apt update
apt install -y yarn

# Install dotenv
echo "--------------- Install dotenv library ---------------"
YARN_GLOBAL_LIBRARIES="/opt/yarn_global"

yarn config set global-folder ${YARN_GLOBAL_LIBRARIES}
yarn global add dotenv

# Load tnlcm database
mongosh --file ${TNLCM_FOLDER}/core/database/tnlcm-structure.js

# Install nodejs
echo "--------------- Install nodejs ---------------"
curl -fsSL https://deb.nodesource.com/setup_lts.x -o nodesource_setup.sh
bash nodesource_setup.sh
apt-get install -y nodejs
rm nodesource_setup.sh

# Install mongo-express
echo "--------------- Install mongo-express ---------------"
MONGO_EXPRESS_VERSION="v1.0.2"
MONGO_EXPRESS_FOLDER=/opt/mongo-express-${MONGO_EXPRESS_VERSION}

git clone --depth 1 --branch release/${MONGO_EXPRESS_VERSION} -c advice.detachedHead=false https://github.com/mongo-express/mongo-express.git ${MONGO_EXPRESS_FOLDER}
yarn --cwd ${MONGO_EXPRESS_FOLDER} install
yarn --cwd ${MONGO_EXPRESS_FOLDER} run build

# Start mongo-express service
cat > /etc/systemd/system/mongo-express.service << EOF
[Unit]
Description=mongo-express

[Service]
Type=simple
WorkingDirectory=${MONGO_EXPRESS_FOLDER}
ExecStart=/bin/bash -c 'source ${TNLCM_ENV_FILE} && yarn start'
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl enable --now mongo-express.service

source ${TNLCM_FOLDER}/venv/bin/activate

echo "TNLCM, mongo and mongo-express installed"