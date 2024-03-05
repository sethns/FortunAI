from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding

from llama_index.core import set_global_service_context
from llama_index.core import ServiceContext

import os
from dotenv import load_dotenv

load_dotenv()

gpt3_api_key = os.environ['OPENAI_API_KEY']
gpt3_azure_endpoint = os.environ['OPENAI_DEPLOYMENT_ENDPOINT']
gpt4_api_key = os.environ['GPT4_DEPLOYMENT_ENDPOINT']
gpt4_azure_endpoint = os.environ['GPT4_DEPLOYMENT_ENDPOINT']
deployment_name = os.environ['DEPLOYMENT_NAME']


api_version = os.environ['OPENAI_DEPLOYMENT_VERSION']
print(f"In LLM INIT, AZURE ENDPOINT from .ENV = {gpt3_azure_endpoint}")


def get_embedding_model():
    return AzureOpenAIEmbedding(
    model="text-embedding-ada-002",
    deployment_name="AdaEmbedding",
    api_key=gpt3_api_key,
    azure_endpoint=gpt3_azure_endpoint,
    api_version=api_version,
)


def get_embedding_model_old():
    return AzureOpenAIEmbedding(
        model="text-embedding-ada-002",
        deployment_name="FabricGPT",
        api_key=gpt3_api_key,
        azure_endpoint=gpt3_azure_endpoint,
        api_version=api_version,
    )

def get_completion_llm(model="GPT4"):
    if model == "GPT4":
        llm = AzureOpenAI(
            model="gpt-4",
            deployment_name=deployment_name,
            api_key=os.environ['GPT4_API_KEY'],
            azure_endpoint=os.environ['GPT4_DEPLOYMENT_ENDPOINT'],
            api_version="2023-05-15",
            temperature=0.0
        )
    elif model == "GPT35":  #text-embedding-ada-002
        llm = AzureOpenAI(
            model="gpt-35-turbo",     #AdaEmbedding
            deployment_name="GPT35",
            api_key=gpt3_api_key,
            azure_endpoint=gpt3_azure_endpoint,
            api_version=api_version,
            temperature=0.0
        )
    return llm

def get_service_context():
    print("Getting Service Context")
    llm = get_completion_llm("GPT35")
    embed_model = get_embedding_model()

    service_context = ServiceContext.from_defaults(
        #chunk_size=1024,
        llm=llm,
        embed_model=embed_model
    )
    print("Setting Global Service Context")

    set_global_service_context(service_context)
    return service_context
