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
    path = os.getcwd().replace("\\", "/") + "/destination/"

    #Insert row into db
    #file=st.session_state.file_upload_widget
    print(f"Uploading file {file} for category {category} and entity {entity}")

    if file:
        doc_name=file.name
        print(f"File name: {doc_name}")
        with open(path+doc_name, "wb") as filehandle: 
            filehandle.write(file.getbuffer())
            filehandle.close()
        if(entity=="..."):
            entity=None
        
        UnstructuredReader = download_loader("UnstructuredReader")
        loader = UnstructuredReader()
        docs = loader.load_data(path+doc_name)
        #doc_content = docs[0].text
        add_to_faiss(doc_name, docs)

        dbconn = dblib.get_db_connection()
        with dbconn.cursor() as c:
            c.execute("INSERT INTO [wealth_advisor_warehouse].[dbo].[documents] (category, doc_name, entity, doc_source) VALUES (?, ?, ?, ?)", category, doc_name, entity, "Upload")       
        r = slib.generate_sentiment(path+doc_name)
        #generate_embeddings(file.name)
        print(r)
        pos="{:.2f}".format(r["positive"][0])
        neg="{:.2f}".format(r["negative"][0])
        neu="{:.2f}".format(r["neutral"][0])

        c.execute("UPDATE [wealth_advisor_warehouse].[dbo].[documents] SET sentiment_positive = ?, sentiment_negative = ?, sentiment_neutral = ? WHERE doc_name = ?", pos, neg, neu, doc_name)       
        print("File processing completed")
    else:    
        print("No file to Upload")


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
