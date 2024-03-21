var dbName = 'tnlcm-database';
var trialNetworkCollection = 'trial_network';
var trialNetworkTemplates = 'trial_network_templates';
var trialNetworkUser = 'trial_network_user';

var db = db.getSiblingDB(dbName);

db.createCollection(trialNetworkCollection);
db.createCollection(trialNetworkTemplates);
db.createCollection(trialNetworkUser)