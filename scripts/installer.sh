#!/usr/bin/env bash

export DEBIAN_FRONTEND=noninteractive

echo "============================================="
echo "     🚀 TNLCM INSTALLATION SCRIPT 🚀          "
echo "============================================="

echo "============================================="
echo "               GLOBAL VARIABLES                "
echo "============================================="
UBUNTU_VERSION=$(lsb_release -rs)
PYTHON_VERSION="3.13"
PYTHON_BIN="python${PYTHON_VERSION}"
UV_PATH="/opt/uv"
UV_BIN="${UV_PATH}/uv"
BACKEND_PATH="/opt/TNLCM_BACKEND"
TNLCM_ENV_FILE=${BACKEND_PATH}/.env
MONGODB_VERSION="8.0"
YARN_GLOBAL_LIBRARIES="/opt/yarn_global"
MONGO_EXPRESS_VERSION="v1.0.3"
MONGO_EXPRESS_FOLDER=/opt/mongo-express-${MONGO_EXPRESS_VERSION}

echo "========== Starting Pre-Checks for Script Execution =========="

echo "Checking if the script is being executed as root..."
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root. Please use 'sudo' or switch to the root user."
    exit 1
else
    echo "Script is running as root."
fi

echo "Detecting Ubuntu version..."
echo "Detected Ubuntu version: ${UBUNTU_VERSION}"
if [[ "${UBUNTU_VERSION}" != "22.04" && "${UBUNTU_VERSION}" != "24.04" ]]; then
    echo "Unsupported Ubuntu version: ${UBUNTU_VERSION}. This script only supports Ubuntu 22.04 LTS and 24.04 LTS."
    exit 1
else
    echo "Ubuntu version ${UBUNTU_VERSION} is supported."
fi

echo "Running as root. Ubuntu version detected: ${UBUNTU_VERSION}."

echo "========== Pre-Checks Completed Successfully =========="

echo "========== Starting TNLCM, MongoDB, and Mongo-Express Installation =========="

echo "Updating package lists..."
apt-get update

echo "--------------- Installing weasyprint ---------------"
apt install -y weasyprint

echo "--------------- Installing Git ---------------"
if git --version &>/dev/null; then
    echo "Git is already installed."
else
    echo "Installing Git..."
    apt-get install -y git
fi

echo "--------------- Installing Python ---------------"
if python3 --version | awk '{print $2}' | grep -qE '^3\.1[3-9]|^[4-9]'; then
    echo "Python ${PYTHON_VERSION} is already installed."
else
    echo "Adding deadsnakes PPA and installing Python ${PYTHON_VERSION}..."
    add-apt-repository ppa:deadsnakes/ppa -y
    apt-get install -y ${PYTHON_BIN}-full
fi

echo "Installing Python venv module..."
apt install -y ${PYTHON_BIN}-venv

echo "--------------- Installing uv ---------------"
curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=${UV_PATH} sh

echo "--------------- Cloning TNLCM Repository ---------------"
if [[ -d ${BACKEND_PATH} ]]; then
    echo "TNLCM repository already cloned."
else
    echo "Cloning TNLCM repository..."
    git clone https://github.com/6G-SANDBOX/TNLCM ${BACKEND_PATH}
fi

echo "Copying .env.template to .env..."
cp ${BACKEND_PATH}/.env.template ${BACKEND_PATH}/.env

echo "Prompting user for configuration details..."
read -p "Enter the TNLCM admin username: " TNLCM_ADMIN_USER
read -sp "Enter the TNLCM admin password: " TNLCM_ADMIN_PASSWORD
echo
HOST_IP=$(hostname -I | awk '{print $1}')
read -e -i ${HOST_IP} -p "Enter the TNLCM host IP (format example: 10.10.10.10): " TNLCM_HOST
read -p "Enter the Jenkins host IP (format example: 10.10.10.11): " JENKINS_HOST
read -p "Enter the Jenkins username: " JENKINS_USERNAME
read -sp "Enter the Jenkins password: " JENKINS_PASSWORD
echo
read -sp "Enter the Jenkins token: " JENKINS_TOKEN
echo
read -sp "Enter the sites token (not use \" or ' or \`): " SITES_TOKEN
echo
# echo "Now configure two-factor authentication for TNLCM."
# read -p "Enter if you want to enable two-factor authentication (true/false): " TWO_FACTOR_AUTH
# if [ "$TWO_FACTOR_AUTH" = "true" ]; then
    # echo "Now configure email credentials necessary for TNLCM to send emails for double authentication."
    # echo "You can create an email account or use an existing one. It is required to create an app password for the email as indicated in the first section of the following page https://mailtrap.io/blog/flask-send-email-gmail/"
    # read -p "Enter the mail username (format example: noreplay@domain.com): " MAIL_USERNAME
    # read -sp "Enter the mail password: " MAIL_PASSWORD
    # echo
# fi

echo "Updating the .env file with the provided information..."
sed -i "s/^TNLCM_ADMIN_USER=.*/TNLCM_ADMIN_USER=\"${TNLCM_ADMIN_USER}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^TNLCM_ADMIN_PASSWORD=.*/TNLCM_ADMIN_PASSWORD=\"${TNLCM_ADMIN_PASSWORD}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^TNLCM_HOST=.*/TNLCM_HOST=\"${TNLCM_HOST}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^JENKINS_HOST=.*/JENKINS_HOST=\"${JENKINS_HOST}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^JENKINS_USERNAME=.*/JENKINS_USERNAME=\"${JENKINS_USERNAME}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^JENKINS_PASSWORD=.*/JENKINS_PASSWORD=\"${JENKINS_PASSWORD}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^JENKINS_TOKEN=.*/JENKINS_TOKEN=\"${JENKINS_TOKEN}\"/" ${TNLCM_ENV_FILE}
sed -i "s/^SITES_TOKEN=.*/SITES_TOKEN='${SITES_TOKEN}'/" ${TNLCM_ENV_FILE}
# sed -i "s/^TWO_FACTOR_AUTH=.*/TWO_FACTOR_AUTH='${TWO_FACTOR_AUTH}'/" ${TNLCM_ENV_FILE}
# sed -i "s/^MAIL_USERNAME=.*/MAIL_USERNAME='${MAIL_USERNAME}'/" ${TNLCM_ENV_FILE}
# sed -i "s/^MAIL_PASSWORD=.*/MAIL_PASSWORD='${MAIL_PASSWORD}'/" ${TNLCM_ENV_FILE}
echo "Environment variables successfully configured!"

echo "--------------- Installing MongoDB ---------------"
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
yarn config set global-folder ${YARN_GLOBAL_LIBRARIES}
yarn global add dotenv
echo "dotenv library installed globally."

echo "--------------- Loading TNLCM Database ---------------"
mongosh --file ${BACKEND_PATH}/core/database/tnlcm-structure.js
echo "Database loaded successfully."

echo "--------------- Installing Node.js ---------------"
curl -fsSL https://deb.nodesource.com/setup_lts.x -o nodesource_setup.sh
bash nodesource_setup.sh
apt-get install -y nodejs
rm nodesource_setup.sh
echo "Node.js installed successfully."

echo "--------------- Installing Mongo-Express ---------------"
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

# echo "--------------- Installing nginx ---------------"
# apt-get install -y nginx
# sudo mkdir -p /etc/nginx/ssl
# sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/ssl/tnlcm.key -out /etc/nginx/ssl/tnlcm.crt -subj "/CN=${HOST_IP}"
# cat > /etc/nginx/sites-enabled/tnlcm << EOF
# server {
#     listen 80;
#     server_name ${HOST_IP};
#     return 301 https://\$host\$request_uri;
# }
# server {
#     listen 443 ssl;
#     server_name ${HOST_IP};
#     ssl_certificate /etc/nginx/ssl/tnlcm.crt;
#     ssl_certificate_key /etc/nginx/ssl/tnlcm.key;
#     location / {
#         proxy_pass http://127.0.0.1:5000;
#         proxy_http_version 1.1;
#         proxy_set_header Upgrade \$http_upgrade;
#         proxy_set_header Connection 'upgrade';
#         proxy_set_header Host \$host;
#         proxy_cache_bypass \$http_upgrade;
#     }
# }
# EOF

# systemctl restart nginx

echo "Installing TNLCM dependencies using uv..."
${UV_BIN} --directory ${BACKEND_PATH} sync
cd ${BACKEND_PATH}
${UV_BIN} run gunicorn -c conf/gunicorn_conf.py

echo "All components installed successfully."
echo "========== TNLCM, MongoDB, and Mongo-Express Installation Complete =========="