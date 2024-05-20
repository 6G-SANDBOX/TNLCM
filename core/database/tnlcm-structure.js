const fs = require('fs');
const path = require('path');

function loadDatabaseName() {
    const envPath = path.resolve(__dirname, '..', '..', '.env');
    const envContents = fs.readFileSync(envPath, 'utf-8');
    const envVars = envContents.split(/\r?\n/);

    for (const line of envVars) {
        const [key, value] = line.split('=');
        if (key === "MONGO_DATABASE") {
            return value.toString().replace(/"/g, '');
        }
    }
}

var dbName = loadDatabaseName();
var trialNetworks = 'trial_networks';
var trialNetworksTemplates = 'trial_networks_templates';
var users = 'users';
var verificationTokens = 'verification_tokens';

var db = db.getSiblingDB(dbName);

db.createCollection(trialNetworks);
db.createCollection(trialNetworksTemplates);
db.createCollection(users);
db.createCollection(verificationTokens);