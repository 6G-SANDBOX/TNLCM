var dbName = 'tnlcm-database';
var trialNetworkCollection = 'trial_network';
var trialNetworksTemplates = 'trial_networks_templates';

var db = db.getSiblingDB(dbName);

db.createCollection(trialNetworkCollection);
db.createCollection(trialNetworksTemplates);