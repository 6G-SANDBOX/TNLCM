var dbName = 'tnlcm-database';
var trialNetworkCollection = 'trial_network';
var trialNetworkTemplates = 'trial_networks_templates';
var users = 'users';

var db = db.getSiblingDB(dbName);

db.createCollection(trialNetworkCollection);
db.createCollection(trialNetworkTemplates);
db.createCollection(users)