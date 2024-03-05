import os
from langchain.chat_models import AzureChatOpenAI

# from langchain.chat_models import AzureChatOpenAI
# from langchain_community.chat_models import AzureChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# gpt3_api_key = os.environ['OPENAI_API_KEY']
# gpt3_azure_endpoint = os.environ['OPENAI_DEPLOYMENT_ENDPOINT']
# api_version = os.environ['OPENAI_DEPLOYMENT_VERSION']
# gpt4_api_key = os.environ['GPT4_API_KEY']
# gpt4_azure_endpoint = os.environ['GPT4_DEPLOYMENT_ENDPOINT']
# deployment_name = os.environ['DEPLOYMENT_NAME']
# print(f"In LLM INIT, AZURE ENDPOINT from .ENV = {gpt3_azure_endpoint}")

def get_chat_llm():
    
    # os.environ["AZURE_OPENAI_API_KEY"] = gpt4_api_key
    # os.environ["AZURE_OPENAI_ENDPOINT"] = gpt4_azure_endpoint

    llm = AzureChatOpenAI(
        openai_api_version="2023-05-15",
        #azure_deployment="BFSLABAUSGPT4",
        deployment_name="FabricGPT",
        #model_version= "0613",
        openai_api_type= "azure",
        openai_api_base= "https://fabric-demo.openai.azure.com/",
        openai_api_key= "32e4ee8596b54f5cb17cd78bbe66219b"
    )
    
    return llm

    


    
# model = AzureChatOpenAI(
# openai_api_base=OPENAI_API_BASE,
# openai_api_version="2023-07-01-preview",
# azure_deployment=GPT_DEPLOYMENT_NAME,
# openai_api_key=OPENAI_API_KEY,
# openai_api_type="azure",
# )