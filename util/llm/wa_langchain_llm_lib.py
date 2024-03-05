import os
from langchain.chat_models import AzureChatOpenAI

from dotenv import load_dotenv

load_dotenv()
def get_chat_llm():

    llm = AzureChatOpenAI(
        openai_api_version="2023-05-15",
        deployment_name="FabricGPT",
        openai_api_type= "azure",
        openai_api_base= "https://fabric-demo.openai.azure.com/",
        openai_api_key= "xxx"
    )
    
    return llm
  


    
# model = AzureChatOpenAI(
# openai_api_base=OPENAI_API_BASE,
# openai_api_version="2023-07-01-preview",
# azure_deployment=GPT_DEPLOYMENT_NAME,
# openai_api_key=OPENAI_API_KEY,
# openai_api_type="azure",
# )
