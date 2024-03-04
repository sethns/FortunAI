import psycopg2
from sqlalchemy import make_url


#importing necessary packages --- NEW
import pandas as pd
from azure.identity import AzureCliCredential
import struct
from itertools import chain, repeat
import pyodbc
import os

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
