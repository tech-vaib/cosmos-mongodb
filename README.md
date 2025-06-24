# comos-mongodb
./create_cosmos_env.sh dev
./create_cosmos_env.sh stage
./create_cosmos_env.sh prod

############################################################################## OR  PYTHON AND CLI  WAY ##############################################################################
## Create Azure Cosmos DB Account (MongoDB API)
# Variables
RESOURCE_GROUP="rg-rag-dev"
ACCOUNT_NAME="cosmos-rag-dev"
LOCATION="eastus"

# Create resource group (if needed)
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Cosmos DB account with Mongo API
az cosmosdb create \
  --name $ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --kind MongoDB \
  --locations regionName=$LOCATION failoverPriority=0 \
  --default-consistency-level Eventual \
  --enable-automatic-failover true

## Get the Connection String
az cosmosdb keys list \
  --name $ACCOUNT_NAME \
  --resource-group $RESOURCE_GROUP \
  --type connection-strings \
  --query "connectionStrings[0].connectionString" \
  --output tsv

## Run It
pip install pymongo
python create_collections.py

## Create TTL Index in Mongo Shell

// Switch to your database (will be created if it doesn't exist)
use rag-db

// Create a new collection (basic)
db.createCollection("embeddings")

// Optional: Create a TTL index
db.embeddings.createIndex(
  { created_at: 1 },
  { expireAfterSeconds: 172800, name: "ttl_created_at" }
)


## To Modify TTL for Existing Collection
db.runCommand({
  collMod: "embeddings",
  expireAfterSeconds: 172800
})

Or via pymongo: python code

db.command("collMod", "embeddings", expireAfterSeconds=172800)

#####################################################################

## Export Collections from Cosmos Mongo DB (dev)
# Cosmos MongoDB connection string (from Azure Portal)
SRC_URI="mongodb://<user>:<pass>@<cosmos-dev-uri>/?ssl=true"
DATABASE="rag-db"

# Dump to local folder
mongodump --uri="$SRC_URI" --db="$DATABASE" --out="./backup"
#This exports all collections and data in rag-db to ./backup/rag-db/


## Import Collections to Another Cosmos DB (prod)
DEST_URI="mongodb://<user>:<pass>@<cosmos-prod-uri>/?ssl=true"
DATABASE="rag-db"

mongorestore --uri="$DEST_URI" --db="$DATABASE" ./backup/rag-db
#This imports the dumped collections into the target Cosmos DB database.



## Export/Import a Single Collection (JSON)
# Export from dev
mongoexport --uri="$SRC_URI" --db="$DATABASE" --collection=embeddings --out=embeddings.json

# Import to prod
mongoimport --uri="$DEST_URI" --db="$DATABASE" --collection=embeddings --file=embeddings.json --jsonArray

### Run the following to get indexes on all collections:
use rag-db;

const collections = db.getCollectionNames();

collections.forEach((collName) => {
  print(`Indexes for collection: ${collName}`);
  const indexes = db.getCollection(collName).getIndexes();
  indexes.forEach(index => printjson(index));
  print("\n");
});

## This prints all indexes for every collection in JSON format.

db.collection.getIndexes()

##################
## Granting cosmos DB read/write role - contributor - all CURD operations allowed

# Assign the "Cosmos DB Built-in Data Contributor" role at Cosmos DB account level

az role assignment create \
  --assignee <user-object-id-or-service-principal-id> \
  --role "Cosmos DB Built-in Data Contributor" \
  --scope /subscriptions/<subscription-id>/resourceGroups/<rg-name>/providers/Microsoft.DocumentDB/databaseAccounts/<account-name>

## Read only role

az role assignment create \
  --assignee <user-or-service-principal-object-id> \
  --role "Cosmos DB Built-in Data Reader" \
  --scope /subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.DocumentDB/databaseAccounts/<account-name>

### TO FIND ALL ACCESS LIST:
Find the Role Assignment ID or Details

az role assignment list \
  --assignee <user-or-sp-object-id> \
  --scope /subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.DocumentDB/databaseAccounts/<account-name> \
  --output table

## Delete the Role Assignment -Using the role assignment ID (or by specifying the role and assignee):
az role assignment delete \
  --assignee <user-or-sp-object-id> \
  --role "<role-name>" \
  --scope /subscriptions/<subscription-id>/resourceGroups/<resource-group>/providers/Microsoft.DocumentDB/databaseAccounts/<account-name>


## To connect, your connection string includes:
mongodb://<account>.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@<account>@