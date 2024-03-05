from sqlalchemy import make_url, create_engine, MetaData

from llama_index.core import VectorStoreIndex
from llama_index.core import SQLDatabase
from llama_index.core.objects import SQLTableNodeMapping, ObjectIndex, SQLTableSchema
from sqlalchemy import create_engine, MetaData

import os
import argparse
from dotenv import load_dotenv

load_dotenv()
parser = argparse.ArgumentParser()
print("###############READING ENV DATA DB LIB ####################")
parser.add_argument('--db', choices=['wealthdb', 'loans.db', 'dev.db'], default='loans.db', help='The DB for SQL QnA')
args = parser.parse_args()
dbname=args.db
os.environ['QNA_DB'] = dbname

def get_sql_db(instance="local"):
    if instance == "local":
        engine = get_engine(os.environ['QNA_DB'])
        metadata_obj = MetaData()        
    else:
        engine = get_vm_db_engine() 
        metadata_obj = MetaData(schema="wa_app")    
    # load all table definitions
    #metadata_obj = MetaData()
    metadata_obj.reflect(engine)

    sql_database = SQLDatabase(engine)

    table_node_mapping = SQLTableNodeMapping(sql_database)

    table_schema_objs = []
    for table_name in metadata_obj.tables.keys():
        print(table_name)
        table_schema_objs.append(SQLTableSchema(table_name=table_name))

    # We dump the table schema information into a vector index. The vector index is stored within the context builder for future use.
    obj_index = ObjectIndex.from_objects(
        table_schema_objs,
        table_node_mapping,
        VectorStoreIndex,
    )
    return engine, sql_database, obj_index


def get_engine(dbname: str):
    scheme = "postgresql+psycopg2" # Database Scheme
    host = "localhost" # Database Host
    port = "5432" # Database Port
    username = "postgres" # Database User
    password = "postgressneha" # Database Password
    dbname = dbname #"wealthdb" # Database Name
    #dbname = "loans.db" # Database Name
    #pg_uri = f"{scheme}://{username}:{password}@{host}:{port}/{dbname}"
    pg_uri = f"{scheme}://{username}:{password}@{host}:{port}/{dbname}"
    print(pg_uri)
    engine = create_engine(pg_uri)
    return engine

def get_vm_db_engine():
    scheme = "postgresql+psycopg2" # Database Scheme
    host = os.environ['VM_POSTGRES_DB_HOST'] # Database Host
    port = "5432" # Database Port
    username = "wa_app" # Database User
    password = os.environ['VM_POSTGRES_DB_PWD'] # Database Password
    dbname = "dev.db" # Database Name
    #dbname = "loans.db" # Database Name
    pg_uri = f"{scheme}://{username}:{password}@{host}:{port}/{dbname}"
    #pg_uri = f"{scheme}://{username}@{host}:{port}/{dbname}"
    print(pg_uri)
    engine = create_engine(pg_uri)
    return engine