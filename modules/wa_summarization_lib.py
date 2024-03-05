import os
from langchain.prompts import PromptTemplate
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader

from util.llm.wa_langchain_llm_lib import get_chat_llm

pdf_path = "uploaded_file.pdf"

def save_file_old(file_bytes): #save the uploaded file to disk to summarize later
    with open(pdf_path, "wb") as f: 
        f.write(file_bytes)
    
    return f"Saved {pdf_path}"

def save_file_reports(name : str, file_bytes: bytes): #save the uploaded file to disk to summarize later
    with open(name, "wb") as f: 
        f.write(file_bytes)
    
    return f"{name}"


def save_file(name : str, file_bytes: bytes): #save the uploaded file to disk to summarize later
    with open(pdf_path, "wb") as f: 
        f.write(file_bytes)   
    return f"{name}"

def get_docs():    
    loader = PyPDFLoader(file_path=pdf_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ".", " "], chunk_size=4000, chunk_overlap=100 
    )
    docs = text_splitter.split_documents(documents=documents)
    
    return docs

def get_summary(return_intermediate_steps=False):
    
     map_prompt_template = "{text}\n\nWrite a few sentences summarizing the above:"
    map_prompt = PromptTemplate(template=map_prompt_template, input_variables=["text"])
    
    combine_prompt_template = "{text}\n\nWrite a detailed analysis of the above:"
    combine_prompt = PromptTemplate(template=combine_prompt_template, input_variables=["text"])
    
    
    llm = get_chat_llm()
    docs = get_docs()
    
    chain = load_summarize_chain(llm, chain_type="map_reduce", map_prompt=map_prompt, combine_prompt=combine_prompt, return_intermediate_steps=return_intermediate_steps)
    #chain = load_summarize_chain(llm, chain_type="stuff")

    if return_intermediate_steps:
        return chain({"input_documents": docs}, return_only_outputs=True) #make return structure consistent with chain.run(docs)
    else:
        return chain.run(docs)


def get_refined_summary():
    question_prompt_template = """
                Please provide a summary of the following text.
                TEXT: {text}
                SUMMARY:
                """

    question_prompt = PromptTemplate(
        template=question_prompt_template, input_variables=["text"]
    )

    refine_prompt_template = """
                Write a concise summary of the following text delimited by triple backquotes.
                Return your response in bullet points which covers the key points of the text.
                ```{text}```
                BULLET POINT SUMMARY:
                """

    refine_prompt = PromptTemplate(
        template=refine_prompt_template, input_variables=["text"]
    )

    llm = get_chat_llm()
    docs = get_docs()

    refine_chain = load_summarize_chain(
        llm,
        chain_type="refine",
        question_prompt=question_prompt,
        refine_prompt=refine_prompt,
        return_intermediate_steps=True,
    )
    print("the refin chain ")
    refine_outputs = refine_chain({"input_documents": docs})
    return refine_outputs
