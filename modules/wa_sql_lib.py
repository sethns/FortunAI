#import data_db_lib as datadb
#import az_llm_lib as llmlib
import util.llm.wa_llamaindex_llm_lib as llmlib
import util.db.wa_data_db_lib as datadb

from llama_index.core.indices.struct_store import SQLTableRetrieverQueryEngine

service_context = llmlib.get_service_context()
#engine, sql_database, obj_index = datadb.get_sql_db(instance="vm")
engine, sql_database, obj_index = datadb.get_sql_db(instance="local")

query_engine = SQLTableRetrieverQueryEngine(
    sql_database,
    obj_index.as_retriever(similarity_top_k=10),
    service_context=service_context
)

def load_df_to_db(df, table_name):
    df.to_sql(name=table_name, con=engine, if_exists='append')

def get_answer(query):
    response = query_engine.query(query)
    print(response.metadata)
    print(response.metadata['sql_query'])
    print(response.metadata['result'])
    print(response.metadata['col_keys'])
    return response

if __name__ == '__main__':
    nlquery="What are the average loan amounts for new home purchases versus refinances in various states?"
    #nlquery="What are the top categories for which we have documents across all entities?"
    get_answer(nlquery)

