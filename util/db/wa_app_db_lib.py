import psycopg2
from llama_index.vector_stores.postgres import PGVectorStore
from sqlalchemy import make_url


#importing necessary packages --- NEW
import pandas as pd
from azure.identity import AzureCliCredential
# import structcls
import struct
from itertools import chain, repeat
import pyodbc
import os
from dotenv import load_dotenv
# from notebookutils.mssparkutils.credentials import getSecret

# KEYVAULT_ENDPOINT = "https://aifabric.vault.azure.net/"
# OPENAI_ENDPOINT = "https://fabric-demo.openai.azure.com/"
# OPENAI_SERVICES_KEY = getSecret(KEYVAULT_ENDPOINT, "fabricgptkey")
# OPENAI_SERVICES_LOCATION = "eastus2"

# print("ke read from keyvault is : ",KEYVAULT_ENDPOINT)
load_dotenv()


# db_name = "dev.db"
# db_local_dev = "postgresql://postgres:postgressneha@localhost:5432/dev.db"

# def get_db_connection_postgres():
#     conn = psycopg2.connect(host="localhost", port="5432", dbname=db_name, user="postgres",password = "postgressneha" )
#     conn.autocommit = True
#     return conn

# def get_vector_store(table : str):
#     connection_string = "postgresql://postgres:postgressneha@127.0.0.1:5432"
#     url = make_url(connection_string)
#     vector_store = PGVectorStore.from_params(
#         database=db_name,
#         host=url.host,
#         password=url.password,
#         port=url.port,
#         user=url.username,
#         table_name=table,
#         embed_dim=1536,  # openai embedding dimension
#     )
#     return vector_store


def get_db_connection():
    credential = AzureCliCredential()
    warehouse_connection_string =  os.environ['sql_endpoint']
    warehouse_name = os.environ['database']
    connection_string = f"Driver={{ODBC Driver 18 for SQL Server}};Server={warehouse_connection_string},1433;Database=f{warehouse_name};Encrypt=Yes;TrustServerCertificate=No"

    # prepare the access token
    token_object = credential.get_token("https://database.windows.net//.default") # Retrieve an access token valid to connect to SQL databases
    token_as_bytes = bytes(token_object.token, "UTF-8") # Convert the token to a UTF-8 byte string
    encoded_bytes = bytes(chain.from_iterable(zip(token_as_bytes, repeat(0)))) # Encode the bytes to a Windows byte string
    token_bytes = struct.pack("<i", len(encoded_bytes)) + encoded_bytes # Package the token into a bytes object
    attrs_before = {1256: token_bytes}  # Attribute pointing to SQL_COPT_SS_ACCESS_TOKEN to pass access token to the driver

    conn= pyodbc.connect(connection_string, attrs_before=attrs_before)
    conn.autocommit = True
    print("Connection succesful")
    return conn
