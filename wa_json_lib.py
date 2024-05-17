import json
import os
from llama_index.core import Document
from llama_index.core import download_loader
from llama_index.core import SimpleDirectoryReader, load_index_from_storage, VectorStoreIndex, StorageContext

from llama_index.core.indices.struct_store import JSONQueryEngine
from llama_index.core.indices.struct_store import JSONQueryEngine
import util.llm.wa_llamaindex_llm_lib as llmlib
print("###################################################################")
print(os.getcwd())
print("###################################################################")

with open(os.getcwd()+'/data/json-assist/bank_rates.json') as f:
    json_value = json.load(f)

with open(os.getcwd()+'/data/json-assist/json_schema.json') as f:
    json_schema = json.load(f)

def get_answer_from_json(doc_query):
    print(f"QUERY *********{doc_query}")
    service_context = llmlib.get_service_context()
    # load index from disk
    nl_query_engine = JSONQueryEngine(
        json_value=json_value,
        json_schema=json_schema,
        service_context = service_context,
        #llm=llm,
    )
    raw_query_engine = JSONQueryEngine(
        json_value=json_value,
        json_schema=json_schema,
        service_context = service_context,
        #llm=llm,
        synthesize_response=False,
    )


    response = nl_query_engine.query(doc_query)
    print(response.metadata)
    print(f"RESPONSE::::::::::::::::::{response}")
    
    return str(response)