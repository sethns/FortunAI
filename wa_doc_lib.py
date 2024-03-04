import util.db.wa_app_db_lib as dblib
import modules.wa_sentiment_lib as slib

import os
import pandas as pd
import cs50 as cs50
from typing import Any, List

import faiss
from llama_index.core import Document
from llama_index.core import download_loader
from llama_index.core import SimpleDirectoryReader, load_index_from_storage, VectorStoreIndex, StorageContext
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.readers.file import UnstructuredReader

mydb = cs50.SQL(dblib.db_local_dev)  # For PostgreSQL

def get_docs_postgres():
    conn = dblib.get_db_connection_postgres()
    sql= "SELECT category, entity, doc_name, doc_source FROM DOCUMENTS"
    with conn.cursor() as c:
        c.execute(sql)
        rows = c.fetchall()
        #print(results)
        columns = [column[0] for column in c.description]
        df = pd.DataFrame(rows, columns=columns)
        return df


def get_docs():
    conn = dblib.get_db_connection()
    sql= "SELECT category, entity, doc_name, doc_source FROM [wealth_advisor_warehouse].[dbo].[documents]"
    with conn.cursor() as c:
        c.execute(sql)
        rows_list = c.fetchall()
        rows = [list(t) for t in rows_list]
        #print(results)
        columns = [column[0] for column in c.description]
        df = pd.DataFrame(rows, columns=columns)
        return df
    


def add_to_faiss(doc_name: str, msg_documents : List[Document]):
    # dimensions of text-ada-embedding-002
    d = 1536
    faiss_index = faiss.IndexFlatL2(d)

    try:
        vector_store = FaissVectorStore.from_persist_dir("./storage/doc")
        # vector_store = FaissVectorStore.from_persist_dir("./storage/doc")
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store, persist_dir="./storage/doc"
        )
        index = load_index_from_storage(storage_context=storage_context)
        index_loaded = True
    except:
        index_loaded = False

    if index_loaded:
        for doc in msg_documents:
            doc.extra_info["filename"] = doc_name
            doc.metadata = {"filename": doc_name}
            index.insert(doc) # for doc in msg_documents )
        index.storage_context.persist(persist_dir="./storage/doc")
    else:
        print("###################Index does not exist - to be created now")
        vector_store = FaissVectorStore(faiss_index=faiss_index)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_documents(
            msg_documents, storage_context=storage_context
        )
        index.storage_context.persist(persist_dir="./storage/doc")


def upload_file(file, category, entity, doc_source):

    # path="../upload/doc/"
    path = "C:/Users/sneha/Desktop/wealth_assistant/destination/"

    #Insert row into db
    #file=st.session_state.file_upload_widget
    print(f"Uploading file {file} for category {category} and entity {entity}")
    if file:
        doc_name=file.name
        print(f"File name: {doc_name}")
        #with open(os.path.join(path,doc_name), 'wb') as filehandle:
        with open(path+doc_name, "wb") as filehandle: 
            filehandle.write(file.getbuffer())
            filehandle.close()
            #filebuffer = ["a line of text", "another line of text", "a third line"]
            #filehandle.writelines(f"{line for line in filebuffer}\n")
        if(entity=="..."):
            entity=None
        
        UnstructuredReader = download_loader("UnstructuredReader")
        loader = UnstructuredReader()
        docs = loader.load_data(path+doc_name)
        #doc_content = docs[0].text
        add_to_faiss(doc_name, docs)

        dbconn = dblib.get_db_connection()
        with dbconn.cursor() as c:
            # val = (category, doc_name, entity, doc_source)
            # sql = "INSERT INTO [dbo].[documents] (category, doc_name, entity, doc_source) VALUES (%s , %s, %s, %s)"
            # c.execute(sql, val)
            c.execute("INSERT INTO [wealth_advisor_warehouse].[dbo].[documents] (category, doc_name, entity, doc_source) VALUES (?, ?, ?, ?)", category, doc_name, entity, "Upload")       
            # c.execute("""INSERT INTO [dbo].[documents] (category, doc_name, entity, doc_source)
            #     VALUES (%(category)s, %(doc_name)s, %(entity)s, %(doc_source)s);""",
            #     {"category": category, "doc_name": doc_name,  "entity": entity,  "doc_source": "Upload"})   

        r = slib.generate_sentiment(path+doc_name)
        #generate_embeddings(file.name)
        print(r)
        pos="{:.2f}".format(r["positive"][0])
        neg="{:.2f}".format(r["negative"][0])
        neu="{:.2f}".format(r["neutral"][0])

        #db = cs50.SQL("sqlite:///file.db")  # For SQLite, file.db must exist
        #db = cs50.SQL("mysql://username:password@host:port/database")  # For MySQL
        # pos = 0.2
        # neg = 0.3
        # neu = 0.8
        c.execute("UPDATE [wealth_advisor_warehouse].[dbo].[documents] SET sentiment_positive = ?, sentiment_negative = ?, sentiment_neutral = ? WHERE doc_name = ?", pos, neg, neu, doc_name)       
        # mydb.execute("UPDATE [wealth_advisor_warehouse].[dbo].[documents] SET sentiment_positive = ?, sentiment_negative = ?, sentiment_neutral = ? WHERE doc_name = ?", pos, neg, neu, doc_name)
        print("File processing completed")
    else:    
        print("No file to Upload")


def upload_file_fabric(base_path, category, entity):
    """
    Traverses a directory to find files, uploads them, processes them,
    and adds their content to a Faiss index.
    """
    print("UPLOAD FUNCTION LOADING")
    
    # base_path = r"C:/Users/sethn/Downloads/wealth_assistant/upload/"
    # base_path = r"C:/Users/sneha/Desktop/wealth_assistant/upload"
    d_path = r"C:/Users/sneha/Desktop/wealth_assistant/destination"

    for root, _, files in os.walk(base_path):
        print("going to read files in the location")
        print("Files present in the location : ",files)
        for file_name in files:
            print("step2 in reading files")
            source_file_path = os.path.join(root, file_name)  # Correctly specify the file path
            d_file_path = os.path.join(d_path, file_name)
            #dt_file_path = os.path.join(dt_path, file_name)

            # Correctly open the source file to read its content
            with open(source_file_path, 'rb') as source_file:  # Use source_file_path, not base_path
                file_content = source_file.read()

            # 'file' object simulation
            file = BytesIO(file_content)
            doc_name  = file_name  # Simulate the 'name' attribute of file-like objects

            print(f"Uploading file {doc_name} for category {category} and entity {entity}")

            if file:
                # Since 'file' is a BytesIO object, use 'getvalue()' to write its content
                with open(d_file_path, "wb") as filehandle:
                    filehandle.write(file.getvalue())  # Write the file content to the destination

                if entity == "...":
                    entity = None

                # Assuming download_loader and UnstructuredReader are properly defined and imported
                UnstructuredReader = download_loader("UnstructuredReader")
                loader = UnstructuredReader()
                docs = loader.load_data(dt_file_path)

                # Assuming add_to_faiss is properly defined and imported
                add_to_faiss(file.name, docs)
                    
                print(f"File {doc_name} uploaded and processed successfully.")

                dbconn = get_db_connection()
                with dbconn.cursor() as c:
                    sql = """INSERT INTO [wealth_advisor_lakehouse].[dbo].[documents] (category, doc_name, entity, doc_source) VALUES (?, ?, ?, ?);"""
                    params = (category, doc_name, entity, "Upload")
                    c.execute(sql, params)
                    dbconn.commit() 

                r = slib.generate_sentiment(d_path+doc_name)
                #generate_embeddings(file.name)
                print(r)
                pos="{:.2f}".format(r["positive"][0])
                neg="{:.2f}".format(r["negative"][0])
                neu="{:.2f}".format(r["neutral"][0])

                conn1 = get_db_connection()
                sql1 = "UPDATE [wealth_advisor_lakehouse].[dbo].[documents] SET sentiment_positive = ?, sentiment_negative = ?, sentiment_neutral = ? WHERE doc_name = ?"
                params = (pos, neg, neu, doc_name)
                with conn1.cursor() as c1:
                    c1.execute(sql1, params)
                    conn1.commit()

                #db = cs50.SQL("sqlite:///file.db")  # For SQLite, file.db must exist
                #db = cs50.SQL("mysql://username:password@host:port/database")  # For MySQL
                #mydb.execute("UPDATE DOCUMENTS SET sentiment_positive = ?, sentiment_negative = ?, sentiment_neutral = ? WHERE doc_name = ?", pos, neg, neu, doc_name)
                print("File processing completed")
            else:    
                print("No file to Upload")
                



def get_faiss_index():
    vector_store = FaissVectorStore.from_persist_dir("./storage/doc")
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store, persist_dir="./storage/doc"
    )
    index = load_index_from_storage(storage_context=storage_context)
    return index

def get_answer_from_docs_faiss(doc_query):
    print(f"QUERY *********{doc_query}")
    # load index from disk
    vector_store = FaissVectorStore.from_persist_dir("./storage/doc")
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store, persist_dir="./storage/doc"
    )
    index = load_index_from_storage(storage_context=storage_context)

    # set Logging to DEBUG for more detailed outputs
    query_engine = index.as_query_engine()
    response = query_engine.query(doc_query+". Please cite sources along with your answer.")
    print(response.metadata)
    print(response.source_nodes)
    print(f"RESPONSE::::::::::::::::::{response}")

    pdf_names = set()  
    for doc in response.metadata.values(): 
        try:  
            pdf_name = doc["filename"]  
        except KeyError:  
            pdf_name = 'Unknown'  
    pdf_names.add(pdf_name)  
    pdf_names = sorted(list(pdf_names)) 
    print(pdf_names)
    
    return str(response),  pdf_names

def add_to_faiss(doc_name: str, msg_documents : List[Document]):
    # dimensions of text-ada-embedding-002
    d = 1536
    faiss_index = faiss.IndexFlatL2(d)

    try:
        vector_store = FaissVectorStore.from_persist_dir("./storage/doc")
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store, persist_dir="./storage/doc"
        )
        index = load_index_from_storage(storage_context=storage_context)
        index_loaded = True
    except:
        index_loaded = False

    if index_loaded:
        for doc in msg_documents:
            doc.extra_info["filename"] = doc_name
            doc.metadata = {"filename": doc_name}
            index.insert(doc) # for doc in msg_documents )
        index.storage_context.persist(persist_dir="./storage/doc")
    else:
        print("###################Index does not exist - to be created now")
        vector_store = FaissVectorStore(faiss_index=faiss_index)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_documents(
            msg_documents, storage_context=storage_context
        )
        index.storage_context.persist(persist_dir="./storage/doc")

# CREATE TABLE DOCUMENTS (
#   doc_id SERIAL PRIMARY KEY,
#   category varchar(100) DEFAULT NULL,
#   entity varchar(50) DEFAULT NULL,
#   doc_name varchar(150) DEFAULT NULL,
#   doc_source varchar(50) DEFAULT NULL,
#   sentiment_positive float DEFAULT NULL,
#   sentiment_negative float DEFAULT NULL,
#   sentiment_neutral float DEFAULT NULL
# );    
    
# with conn.session as s:
#     s.execute(
#         'INSERT INTO DOCUMENTS (doc_id, category, doc_name, entity, doc_source) VALUES (:doc_id, :category, :doc_name, :entity, :doc_source);',
#         params=dict(doc_id=doc_id, category=category, doc_name=file.name, entity=entity, doc_source="Upload")
#     )
#     s.commit()