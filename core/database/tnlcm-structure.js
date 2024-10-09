const crypto = require('crypto');

var dbName = process.env.MONGO_DATABASE;
var adminUser = process.env.TNLCM_ADMIN_USER;
var adminPassword = process.env.TNLCM_ADMIN_PASSWORD;
var adminEmail = process.env.TNLCM_ADMIN_EMAIL;

// PBKDF2 parameters
const salt = crypto.randomBytes(16).toString('hex');
const iterations = 600000;
const keyLength = 32;
const digest = 'sha256';

// Generate password hash
const hash = crypto.pbkdf2Sync(adminPassword, salt, iterations, keyLength, digest).toString('hex');
const hashedPassword = `pbkdf2:sha256:${iterations}$${salt}$${hash}`;

var resourceManager = 'resource_manager';
var trialNetworks = 'trial_networks';
var users = 'users';
var verificationTokens = 'verification_tokens';

var db = db.getSiblingDB(dbName);

// Create collections
db.createCollection(resourceManager)
db.createCollection(trialNetworks);
db.createCollection(users);
db.createCollection(verificationTokens);

// Insert administrator user in the users collection
db.users.insertOne({
    username: adminUser,
    password: hashedPassword,
    email: adminEmail,
    role: "admin",
    org: 'ADMIN'
});

// Insert a verification token into the collection verification_tokens
db.verification_tokens.insertOne({
    new_account_email: adminEmail,
    verification_token: Math.floor(Math.random() * 1000000),
    creation_date: new Date()
});