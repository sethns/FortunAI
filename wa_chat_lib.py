import json
import os
import pandas as pd
import cs50 as cs50

import util.llm.wa_llamaindex_llm_lib as llmlib
import util.db.wa_app_db_lib as dblib
import modules.wa_sentiment_lib as slib


from typing import Any, List

import faiss
from llama_index.core import Document
from llama_index.core import download_loader
from llama_index.core import SimpleDirectoryReader, load_index_from_storage, VectorStoreIndex, StorageContext
from llama_index.vector_stores.faiss import FaissVectorStore
from llama_index.core.indices.struct_store import JSONQueryEngine

from llama_index.core.tools import QueryEngineTool

from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector, LLMMultiSelector
#from llama_index.core.selectors import PydanticMultiSelector, PydanticSingleSelector

from llama_index.core.chat_engine import CondenseQuestionChatEngine

def get_faiss_index():
    vector_store = FaissVectorStore.from_persist_dir("./storage/doc")
    storage_context = StorageContext.from_defaults(
        vector_store=vector_store, persist_dir="./storage/doc"
    )
    index = load_index_from_storage(storage_context=storage_context)
    return index

def get_json_query_engine():
    with open(os.getcwd()+'/data/json-assist/bank_rates.json') as f:
        json_value = json.load(f)

    with open(os.getcwd()+'/data/json-assist/json_schema.json') as f:
        json_schema = json.load(f)    

    service_context = llmlib.get_service_context(model="GPT4")
    nl_query_engine = JSONQueryEngine(
        json_value=json_value,
        json_schema=json_schema,
        service_context = service_context,
        #llm=llm,
    )
    return nl_query_engine

json_tool = QueryEngineTool.from_defaults(
    query_engine=get_json_query_engine(),
    description=(
        "Useful for questions related to rates of products and terms like CD for different terms offered by Ally Bank"
    ),
)

vector_tool = QueryEngineTool.from_defaults(
    query_engine=get_faiss_index().as_query_engine(),
    description=(
        "Useful for retrieving any other information related to economy and banking sector"
    ),
)

def get_chat_engine():
    service_context = llmlib.get_service_context(model="GPT4")

    router_query_engine = RouterQueryEngine(
        selector=LLMSingleSelector.from_defaults(),
        service_context = service_context,
        query_engine_tools=[
            json_tool,
            vector_tool,
        ],
    )

    chat_engine = CondenseQuestionChatEngine.from_defaults(
        query_engine=router_query_engine,
        service_context = service_context,
        llm=llmlib.get_completion_llm("GPT4"),
        #condense_question_prompt=custom_prompt,
        #chat_history=custom_chat_history,
        verbose=True,
    )

    return chat_engine;

def get_answer_from_tool(query):
    service_context = llmlib.get_service_context(model="GPT4")
    # LLM selectors use text completion endpoints
    # single selector (LLM)
    selector = LLMSingleSelector.from_defaults()
    query_engine = RouterQueryEngine(
        selector=selector, #PydanticSingleSelector.from_defaults(),
        #service_context = service_context,
        #llm = llmlib.get_completion_llm(),
        query_engine_tools=[
            json_tool,
            vector_tool,
        ],
    )

    response = query_engine.query(query)
    print(response)
    print(response.metadata)
    print(print(str(response.metadata["selector_result"])))
    return response