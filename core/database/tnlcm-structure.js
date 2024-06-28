var dbName = process.env.MONGO_DATABASE;
var resourceManager = 'resource_manager';
var trialNetworks = 'trial_networks';
var trialNetworksTemplates = 'trial_networks_templates';
var users = 'users';
var verificationTokens = 'verification_tokens';

var db = db.getSiblingDB(dbName);

db.createCollection(resourceManager)
db.createCollection(trialNetworks);
db.createCollection(trialNetworksTemplates);
db.createCollection(users);
db.createCollection(verificationTokens);