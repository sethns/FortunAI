import util.llm.wa_llamaindex_llm_lib as llmlib
import util.db.wa_app_db_lib as dblib

import email
import faiss
import datetime
import extract_msg as email_parser
import pandas as pd

from typing import Any, List
from llama_index.core import Document
from llama_index.core import Document

from llama_index.core import download_loader
from llama_index.core import SimpleDirectoryReader, load_index_from_storage, VectorStoreIndex, StorageContext
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.readers.file import UnstructuredReader

import cs50

mydb = cs50.SQL(dblib.db_local_dev)  # For PostgreSQL
pdf_path = "uploaded_file.msg"

def upload_email(name: str, file_bytes):
    path="upload/email/"
    with open(path+name, "wb") as f: 
        f.write(file_bytes)
        f.close()
    
    UnstructuredReader = download_loader("UnstructuredReader")
    loader = UnstructuredReader()

    # For Outlook msg
    #msg_documents = loader.load_data("./data/eml/GenAI.msg")
    msg_documents = loader.load_data(path+name)
    #print(msg_documents[0])
    msg_content = msg_documents[0].text
    #print(msg_content)
    
    add_to_faiss(msg_documents)
    #add_to_pg_vector_store(msg_documents)
    #msg = email.message_from_bytes(file_bytes)
    save_email(path+name)
    return msg_content

def get_emails():
    conn = dblib.get_db_connection()
    sql= "SELECT sender, subject, date_sent as received_on, recipients, summary FROM EMAILS order by date_sent desc"
    with conn.cursor() as c:
        c.execute(sql)
        rows = c.fetchall()
        columns = [column[0] for column in c.description]
        df = pd.DataFrame(rows, columns=columns)
        return df
    
def get_users():
    conn = dblib.get_db_connection()
    with conn.cursor() as c:
        c.execute("SELECT * from AUTHORS")
        results = c.fetchall()
        print(results)
        return results

def get_answer_from_email_faiss(email_query):
    print(f"QUERY *********{email_query}")
    # load index from disk
    vector_store = FaissVectorStore.from_persist_dir("./storage/email")
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store, persist_dir="./storage/email"
    )
    index = load_index_from_storage(storage_context=storage_context)

    # set Logging to DEBUG for more detailed outputs
    query_engine = index.as_query_engine()
    response = query_engine.query(email_query)
    print(f"RESPONSE::::::::::::::::::{response}")
    return str(response)

def get_email_summary(email_query):
    # load index from DB
    vector_store = dblib.get_vector_store("wa_email_vs")
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    query_engine = index.as_query_engine()
    response = query_engine.query(email_query)
    return str(response)

def get_answer_from_email_pg(email_query):
    # load index from DB
    vector_store = dblib.get_vector_store("wa_email_vs")
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    query_engine = index.as_query_engine()
    response = query_engine.query(email_query)
    return response

def add_to_faiss(msg_documents : List[Document]):
    # dimensions of text-ada-embedding-002
    d = 1536
    faiss_index = faiss.IndexFlatL2(d)

    try:
        vector_store = FaissVectorStore.from_persist_dir("./storage/email")
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store, persist_dir="./storage/email"
        )
        index = load_index_from_storage(storage_context=storage_context)
        index_loaded = True
    except:
        index_loaded = False

    if index_loaded:
        for doc in msg_documents:
            index.insert(doc) # for doc in msg_documents )
        index.storage_context.persist(persist_dir="./storage/email")
    else:
        print("###################Index does not exist - to be created now")
        vector_store = FaissVectorStore(faiss_index=faiss_index)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_documents(
            msg_documents, storage_context=storage_context
        )
        #print(index.summary)
        #print(index)
        index.storage_context.persist(persist_dir="./storage/email")

def add_to_pg_vector_store(msg_documents : List[Document]):
    print("ADDING TO PGVECTOR")
    vector_store = dblib.get_vector_store("wa_email_vs")
    print(vector_store)
    #storage_context = StorageContext.from_defaults(vector_store=vector_store)
    #index = load_index_from_storage(storage_context)
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    for doc in msg_documents:
        index.insert(doc) # for doc in msg_documents )
    # index = VectorStoreIndex.from_documents(
    #     msg_documents, storage_context=storage_context
    # )
    print(index.summary)
    print(index)
    #index.storage_context.persist() - No need to call automatically persisted

    # index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    # query_engine = index.as_query_engine()


def save_email(eml_file):

    f = r'GenAI.msg'  # Replace
    msg = email_parser.Message(eml_file)
    sender = msg.sender
    date_sent = msg.date
    subject = msg.subject
    msg_body = msg.body
    recipients = msg.to
    #msg.close()

    summary = get_answer_from_email_faiss(f"Summarize this email from {sender} on subject {subject}")
    print(f"***************SUMMARY::::::{summary}")
    dbconn = dblib.get_db_connection()

    with dbconn.cursor() as c:
        id = c.execute("""
            INSERT INTO EMAILS (sender, recipients, subject, date_sent, summary)
            VALUES (%(sender)s, %(recipients)s, %(subject)s, %(date_sent)s, %(summary)s);
            """,
            {"sender": sender, "recipients": recipients,  "subject": subject,  "date_sent": date_sent, "summary": summary})
        print("*****************************************************************************") 
        print(f"######################ID ::::: {id}")  
         

#  CREATE TABLE EMAILS (
#    id SERIAL PRIMARY KEY,
#    sender varchar(100) DEFAULT NULL,
#    recipients varchar(500) DEFAULT NULL,
#    subject varchar(250) DEFAULT NULL,
#    date_sent TIMESTAMP DEFAULT NULL,
#    summary varchar(4000) DEFAULT NULL
#  );

    # llmlib.get_service_context()
    # conn = db.get_db_connection()
    # with conn.cursor() as c:
    #     #c.execute(f"CREATE DATABASE {db_name}")
    #     #c.execute("INSERT INTO DOCUMENTS (doc_id, category, doc_name, entity, doc_source) VALUES (?, ?, ?, ?, ?)", doc_id, category, file.name, entity, "Upload")       
    #     #c.execute("INSERT INTO authors (first_name, last_name) VALUES (?, ?)", "Bivas", "Nath")   
    #     c.execute("""
    #             INSERT INTO authors (first_name, last_name)
    #             VALUES (%(first)s, %(last)s);
    #             """,
    #             {"first": "Bivas", "last": "Nath"})    
