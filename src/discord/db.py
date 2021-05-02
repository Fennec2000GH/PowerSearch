
import os

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from dotenv import load_dotenv

# .env variables
load_dotenv()
DB_PATH = os.getenv('DB_PATH')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

print(DB_PATH)
print(CLIENT_ID)
print(CLIENT_SECRET)

# other variables
keyspace = 'PowerSearchKS'

cloud_config= {
        'secure_connect_bundle': DB_PATH
}

auth_provider = PlainTextAuthProvider(CLIENT_ID, CLIENT_SECRET)
cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
session = cluster.connect(keyspace=keyspace)

row = session.execute("select release_version from system.local").one()
if row:
    print(row[0])
else:
    print("An error occurred.")


table_query = \
"""
CREATE TABLE IF NOT EXISTS history (
   id int PRIMARY KEY,
   user_id int,
   url text,
   summary text,
   sentiment_score double,
   sentiment_magnitude double,
   entities set<text>
)
"""

session.execute(query=table_query)
