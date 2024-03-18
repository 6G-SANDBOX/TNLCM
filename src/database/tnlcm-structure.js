var dbName = 'tnlcm-database';
var trialNetworkCollection = 'trial_network';

var db = db.getSiblingDB(dbName);

db.createCollection(trialNetworkCollection);