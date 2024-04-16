var dbName = 'tnlcm-database';
var trialNetworks = 'trial_networks';
var trialNetworksTemplates = 'trial_networks_templates';
var users = 'users';
var verificationTokens = 'verification_tokens';

var db = db.getSiblingDB(dbName);

db.createCollection(trialNetworks);
db.createCollection(trialNetworksTemplates);
db.createCollection(users)
db.createCollection(verificationTokens)