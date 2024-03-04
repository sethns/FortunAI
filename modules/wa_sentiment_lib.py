import util.db.wa_app_db_lib as dblib

#from ..filters import equalizer

import fitz
import pandas as pd
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

import cs50 as cs50

import altair as alt
import logging

mydb = cs50.SQL(dblib.db_local_dev)  # For PostgreSQL
logger = logging.getLogger(__name__)
fh = logging.FileHandler('wa-fh-spam.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)

logger.addHandler(fh)
logger.setLevel(logging.DEBUG)

def analyze_chunk(chunk):
    # # Split the chunk into smaller parts to fit within the model's token limit
    # max_chunk_size = 512  # Maximum token limit for your model
    # chunk_parts = [chunk[i:i + max_chunk_size] for i in range(0, len(chunk), max_chunk_size)]
    model_name = "ProsusAI/finbert"
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    inputs = tokenizer(chunk, return_tensors="pt", truncation=True, padding=True)
    outputs = model(**inputs)
    logits = outputs.logits
    probabilities = torch.softmax(logits, dim=-1)

    # Convert the probabilities to a DataFrame
    probabilities = probabilities.detach().numpy()  # Detach the tensor
    df = pd.DataFrame(probabilities, columns=["positive", "neutral", "negative"])
    print(df)
    return df

def generate_sentiment(file_name):
    text = None
    if file_name.endswith(".pdf"):
        print("***************FITZ NEEDED*************")
        with fitz.open(f"{file_name}") as doc:
            text = chr(12).join([page.get_text() for page in doc])
    elif file_name.endswith(".txt"):
        with open(f"{file_name}") as doc:
            text = doc.read()
            doc.read

    r = analyze_chunk(text[:500])
    print(r)
    return r


def get_all_sentiments():
    # sqlite_sql = '''select category as Category, 
    #     entity as Entity, 
    #     count(doc_name) as Count, 
    #     ROUND(avg(sentiment_positive),2) as Positive,  
    #     ROUND(avg(sentiment_neutral),2) as Neutral, 
    #     ROUND(avg(sentiment_negative),2) as Negative 
    #     from DOCUMENTS
    #     group by category, entity order by category, entity'''

    # 'application' code
    logger.debug('debug message')
    logger.info('info message')
    logger.warning('warn message')
    logger.error('error message')
    logger.critical('critical message')

    sql = '''select category as Category, 
        entity as Entity, 
        count(doc_name) as Count, 
        ROUND(CAST (AVG(sentiment_positive) as NUMERIC), 2) as Positive, 
        ROUND(CAST (avg(sentiment_neutral) as NUMERIC), 2) as Neutral, 
        ROUND(CAST (avg(sentiment_negative) as NUMERIC), 2) as Negative 
        from DOCUMENTS
        group by category, entity order by category, entity'''
    sentiment_list = mydb.execute(sql)
    print(sentiment_list)
    return sentiment_list

# def fetch_sentiment_data():
#     import sqlite3
#     conn = sqlite3.connect("documents.db")
#     query = '''select category,entity,avg(sentiment_positive),avg(sentiment_negative),avg(sentiment_neutral),count(DocumentName) from documents
# group by category,entity'''
#     cursor = conn.cursor()
#     result = cursor.execute(query)
#     rows = result.fetchall()
#     columns = [column[0] for column in cursor.description]
#     df = pd.DataFrame(rows, columns=columns)
#     with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
#         print(df)
#     conn.close()
#     return df

def generate_chart(df):
    # Melt the dataframe  
    df3 = pd.melt(df, id_vars=['category'], var_name='Sentiment', value_name='Value')  
    
    # Set the color scheme for the chart  
    color_scale = alt.Scale(domain=['positive', 'neutral', 'negative'], range=['green', 'orange', 'red'])  
    
    # Create the chart  
    chart = alt.Chart(df3).mark_bar().encode(  
        x=alt.X('Value:Q', axis=alt.Axis(format='%')),  
        y=alt.Y('category:N', sort='-x'),  
        color=alt.Color('Sentiment:N', scale=color_scale),  
        tooltip=[alt.Tooltip('category:N'), alt.Tooltip('Sentiment:N'), alt.Tooltip('Value:Q', format='.2%')]  
    ).properties(  
        width=200,  
        height=200  
    )#.interactive() 

    return chart