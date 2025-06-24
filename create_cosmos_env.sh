#!/bin/bash
ENV=$1  # dev, stage, prod
LOCATION="eastus"
RG="rg-rag-${ENV}"
COSMOS_ACCOUNT="cosmos-rag-${ENV}"
DB_NAME="rag-db"

# 1. Create resource group
az group create --name $RG --location $LOCATION

# 2. Create Cosmos DB account with Mongo API
az cosmosdb create \
  --name $COSMOS_ACCOUNT \
  --resource-group $RG \
  --kind MongoDB \
  --locations regionName=$LOCATION failoverPriority=0 \
  --default-consistency-level Eventual \
  --enable-automatic-failover true

# 3. Create database
az cosmosdb mongodb database create \
  --account-name $COSMOS_ACCOUNT \
  --resource-group $RG \
  --name $DB_NAME

# 4. Create containers
for container in embeddings metadata; do
  az cosmosdb mongodb collection create \
    --account-name $COSMOS_ACCOUNT \
    --resource-group $RG \
    --database-name $DB_NAME \
    --name $container \
    --shard key="doc_id"
done
