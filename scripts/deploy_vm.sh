#!/usr/bin/env bash

echo "========== Starting TNLCM, MongoDB, and Mongo-Express Installation =========="

export DEBIAN_FRONTEND=noninteractive

echo "Updating package lists..."
apt-get update

echo "--------------- Installing Git ---------------"
if git --version &>/dev/null; then
    echo "Git is already installed."
else
    echo "Installing Git..."
    apt-get install -y git
fi

echo "--------------- Installing Python ---------------"
PYTHON_VERSION="3.13"
PYTHON_BIN="python${PYTHON_VERSION}"

if python3 --version | awk '{print $2}' | grep -qE '^3\.1[3-9]|^[4-9]'; then
    echo "Python ${PYTHON_VERSION} is already installed."
else
    echo "Adding deadsnakes PPA and installing Python ${PYTHON_VERSION}..."
    add-apt-repository ppa:deadsnakes/ppa -y
    apt-get install -y ${PYTHON_BIN}-full
fi

echo "Installing Python venv module..."
apt install -y ${PYTHON_BIN}-venv

echo "--------------- Installing Poetry ---------------"
POETRY_FOLDER="/opt/poetry"
POETRY_BIN="/opt/poetry/bin/poetry"

if [[ -f ${POETRY_BIN} ]]; then
    echo "Poetry is already installed."
else
    echo "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | POETRY_HOME=${POETRY_FOLDER} python3 -
    ${POETRY_BIN} config virtualenvs.in-project true
fi

echo "--------------- Cloning TNLCM Repository ---------------"
TNLCM_FOLDER="/opt/TNLCM"
TNLCM_ENV_FILE=${TNLCM_FOLDER}/.env

if [[ -d ${TNLCM_FOLDER} ]]; then
    echo "TNLCM repository already cloned."
else
    echo "Cloning TNLCM repository..."
    git clone https://github.com/6G-SANDBOX/TNLCM ${TNLCM_FOLDER}
fi

echo "Installing TNLCM dependencies using Poetry..."
${POETRY_BIN} install --no-root --directory ${TNLCM_FOLDER}

echo "Copying .env.template to .env..."
cp ${TNLCM_FOLDER}/.env.template ${TNLCM_FOLDER}/.env

echo "Prompting user for configuration details..."
read -p "Enter the TNLCM admin username: " TNLCM_ADMIN_USER
read -sp "Enter the TNLCM admin password: " TNLCM_ADMIN_PASSWORD
echo
read -p "Enter the TNLCM host (example: 10.10.10.10): " TNLCM_HOST
read -p "Enter the Jenkins host (example: 10.10.10.11): " JENKINS_HOST
read -p "Enter the Jenkins username: " JENKINS_USERNAME
read -sp "Enter the Jenkins password: " JENKINS_PASSWORD
echo
read -sp "Enter the Jenkins token: " JENKINS_TOKEN
echo
read -sp "Enter the sites token (not use \" or ' or \`): " SITES_TOKEN
echo
echo "Now configure email credentials necessary for TNLCM to send emails for double authentication."
echo "You can create an email account or use an existing one. It is required to create an app password for the email as indicated in the first section of the following page https://mailtrap.io/blog/flask-send-email-gmail/"
read -p "Enter the mail username: " MAIL_USERNAME
read -sp "Enter the mail password: " MAIL_PASSWORD
echo

echo "Updating the .env file with the provided information..."
sed -i "s/^TNLCM_ADMIN_USER=.*/TNLCM_ADMIN_USER=\"${TNLCM_ADMIN_USER}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^TNLCM_ADMIN_PASSWORD=.*/TNLCM_ADMIN_PASSWORD=\"${TNLCM_ADMIN_PASSWORD}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^TNLCM_HOST=.*/TNLCM_HOST=\"${TNLCM_HOST}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^JENKINS_HOST=.*/JENKINS_HOST=\"${JENKINS_HOST}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^JENKINS_USERNAME=.*/JENKINS_USERNAME=\"${JENKINS_USERNAME}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^JENKINS_PASSWORD=.*/JENKINS_PASSWORD=\"${JENKINS_PASSWORD}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^JENKINS_TOKEN=.*/JENKINS_TOKEN=\"${JENKINS_TOKEN}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^SITES_TOKEN=.*/SITES_TOKEN='${SITES_TOKEN}'/" ${TNLCM_ENV_FILE}
sed -i "s/^MAIL_USERNAME=.*/MAIL_USERNAME='${MAIL_USERNAME}'/" ${TNLCM_ENV_FILE}
sed -i "s/^MAIL_PASSWORD=.*/MAIL_PASSWORD='${MAIL_PASSWORD}'/" ${TNLCM_ENV_FILE}
echo "Environment variables successfully configured!"

echo "--------------- Installing MongoDB ---------------"
MONGODB_VERSION="8.0"

echo "Adding MongoDB repository and installing MongoDB..."
apt-get install -y gnupg curl
curl -fsSL https://www.mongodb.org/static/pgp/server-${MONGODB_VERSION}.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-${MONGODB_VERSION}.gpg --dearmor
echo "deb [ arch=amd64 signed-by=/usr/share/keyrings/mongodb-server-${MONGODB_VERSION}.gpg ] https://repo.mongodb.org/apt/ubuntu $(lsb_release -sc 2> /dev/null)/mongodb-org/${MONGODB_VERSION} multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-${MONGODB_VERSION}.list
apt-get update
apt-get install -y mongodb-org
systemctl enable --now mongod
echo "MongoDB installed and running."

echo "--------------- Installing Yarn ---------------"
curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | sudo apt-key add -
echo "deb https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list
apt-get update
apt-get install -y yarn
echo "Yarn installed successfully."

echo "--------------- Installing dotenv library ---------------"
YARN_GLOBAL_LIBRARIES="/opt/yarn_global"

yarn config set global-folder ${YARN_GLOBAL_LIBRARIES}
yarn global add dotenv
echo "dotenv library installed globally."

echo "--------------- Loading TNLCM Database ---------------"
mongosh --file ${TNLCM_FOLDER}/core/database/tnlcm-structure.js
echo "Database loaded successfully."

echo "--------------- Installing Node.js ---------------"
curl -fsSL https://deb.nodesource.com/setup_lts.x -o nodesource_setup.sh
bash nodesource_setup.sh
apt-get install -y nodejs
rm nodesource_setup.sh
echo "Node.js installed successfully."

echo "--------------- Installing Mongo-Express ---------------"
MONGO_EXPRESS_VERSION="v1.0.2"
MONGO_EXPRESS_FOLDER=/opt/mongo-express-${MONGO_EXPRESS_VERSION}

echo "Cloning and building Mongo-Express..."
git clone --depth 1 --branch release/${MONGO_EXPRESS_VERSION} -c advice.detachedHead=false https://github.com/mongo-express/mongo-express.git ${MONGO_EXPRESS_FOLDER}
cd ${MONGO_EXPRESS_FOLDER}
yarn install
yarn build
cd
echo "Mongo-Express installed successfully."

echo "--------------- Starting Mongo-Express Service ---------------"
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
echo "Mongo-Express service started."

cd ${TNLCM_FOLDER}

echo "Activating Poetry shell..."
${POETRY_BIN} shell

echo "All components installed successfully."
echo "========== TNLCM, MongoDB, and Mongo-Express Installation Complete =========="