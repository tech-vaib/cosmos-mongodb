from sshtunnel import SSHTunnelForwarder
from pymongo import MongoClient, ASCENDING
import ssl


class CosmosMongoClient:
    def __init__(
        self,
        jump_host,
        jump_user,
        pem_file,
        cosmos_host,
        cosmos_user,
        cosmos_password,
        db_name,
        collection_name,
        remote_port=10255,
        local_port=27017
    ):
        self.jump_host = jump_host
        self.jump_user = jump_user
        self.pem_file = pem_file
        self.cosmos_host = cosmos_host
        self.remote_port = remote_port
        self.local_port = local_port
        self.cosmos_user = cosmos_user
        self.cosmos_password = cosmos_password
        self.db_name = db_name
        self.collection_name = collection_name
        self.tunnel = None
        self.client = None
        self.db = None
        self.collection = None

    def connect(self):
        self.tunnel = SSHTunnelForwarder(
            (self.jump_host, 22),
            ssh_username=self.jump_user,
            ssh_pkey=self.pem_file,
            remote_bind_address=(self.cosmos_host, self.remote_port),
            local_bind_address=('localhost', self.local_port)
        )
        self.tunnel.start()
        print("SSH tunnel established.")

        mongo_uri = f"mongodb://{self.cosmos_user}:{self.cosmos_password}@localhost:{self.local_port}/?ssl=true&retryWrites=false"
        self.client = MongoClient(
            mongo_uri,
            ssl=True,
            ssl_cert_reqs=ssl.CERT_NONE
        )

        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]
        print("MongoDB client connected.")

    def close(self):
        if self.client:
            self.client.close()
        if self.tunnel:
            self.tunnel.stop()
        print("Connection closed.")

    # ==== Basic Operations ====

    def create_index(self, field_name, unique=False):
        return self.collection.create_index([(field_name, ASCENDING)], unique=unique)

    def list_indexes(self):
        return list(self.collection.list_indexes())

    def delete_index(self, index_name):
        self.collection.drop_index(index_name)

    def find(self, query={}, projection=None, limit=0):
        return list(self.collection.find(query, projection).limit(limit))

    def count_documents(self, query={}):
        return self.collection.count_documents(query)

    # ==== Write Operations ====

    def insert_one(self, document):
        return self.collection.insert_one(document)

    def insert_many(self, documents):
        return self.collection.insert_many(documents)

    def update_one(self, filter_query, update_data, upsert=False):
        return self.collection.update_one(filter_query, update_data, upsert=upsert)

    def update_many(self, filter_query, update_data, upsert=False):
        return self.collection.update_many(filter_query, update_data, upsert=upsert)

    def delete_one(self, filter_query):
        return self.collection.delete_one(filter_query)

    def delete_many(self, filter_query):
        return self.collection.delete_many(filter_query)

    # ==== Aggregation ====

    def aggregate(self, pipeline):
        return list(self.collection.aggregate(pipeline))

    # ==== Change Streams (if supported — Cosmos MongoDB v4.0+ only) ====

    def watch_changes(self):
        try:
            with self.collection.watch() as stream:
                for change in stream:
                    print("Change detected:", change)
        except Exception as e:
            print("Change stream not supported or failed:", str(e))
   def apply_index_script_file(self, file_path):
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Script file not found: {file_path}")

        with open(file_path, 'r') as f:
            script_code = f.read()

        print(f"Running index script: {file_path}")
        try:
            # Provide `collection` as local variable for script
            exec(script_code, {"collection": self.collection})
            print("Index script executed successfully.")
        except Exception as e:
            raise RuntimeError(f"Failed to execute index script: {e}")
def main():
client = CosmosMongoClient(
    jump_host='jump.example.com',
    jump_user='azureuser',
    pem_file='/path/to/jump.pem',
    cosmos_host='your-cosmos.mongo.cosmos.azure.com',
    cosmos_user='your-username',
    cosmos_password='your-password',
    db_name='your-db',
    collection_name='your-collection'
)

try:
    client.connect()

    # Insert
    client.insert_one({"name": "Alice", "age": 30})

    # Find
    docs = client.find({"age": {"$gt": 25}}, limit=5)
    print(docs)

    # Update
    client.update_one({"name": "Alice"}, {"$set": {"age": 31}})

    # Aggregate
    pipeline = [{"$group": {"_id": "$age", "count": {"$sum": 1}}}]
    result = client.aggregate(pipeline)
    print(result)
   client.apply_index_script_file("indexes.py")

finally:
    client.close()

#pip install pymongo sshtunnel python-dotenv

if __name__ == "__main__":
    main()
  
  
