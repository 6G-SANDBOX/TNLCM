const crypto = require("crypto");
require("/opt/yarn_global/node_modules/dotenv").config({ 
    path: require("path").resolve(__dirname, "../../.env")
});

var dbName = process.env.MONGO_DATABASE;
var dbRootUsername = process.env.ME_CONFIG_MONGODB_ADMINUSERNAME;
var dbRootPassword = process.env.ME_CONFIG_MONGODB_ADMINPASSWORD;
var tnlcmAdminUser = process.env.TNLCM_ADMIN_USER;
var tnlcmAdminPassword = process.env.TNLCM_ADMIN_PASSWORD;
var tnlcmAdminEmail = process.env.TNLCM_ADMIN_EMAIL;

// Create the database if it doesn't exist
var db = db.getSiblingDB(dbName);

// Create collections
db.createCollection("trial_network");
db.createCollection("user");

// Create the root user
db.createUser({
    user: dbRootUsername,
    pwd: dbRootPassword,
    roles: [
        { role: "readWrite", db: `${dbName}` },
        { role: "dbAdmin", db: `${dbName}` }
    ]
});

// Generate password hash for the admin user
const salt = crypto.randomBytes(16).toString("hex");
const iterations = 600000;
const keyLength = 32;
const digest = "sha256";
const hash = crypto.pbkdf2Sync(tnlcmAdminPassword, salt, iterations, keyLength, digest).toString("hex");
const hashedPassword = `pbkdf2:sha256:${iterations}$${salt}$${hash}`;

// Insert administrator user in the user collection
db.user.insertOne({
    username: tnlcmAdminUser,
    password: hashedPassword,
    email: tnlcmAdminEmail,
    role: "admin",
    org: "ADMIN"
});
