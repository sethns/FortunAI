import streamlit as st
import numpy as np
import pandas as pd

from dotenv import load_dotenv
from typing import List, Tuple, Dict

from transformers import pipeline
from streamlit_option_menu import option_menu

import altair as alt

#https://docs.python.org/3/tutorial/modules.html
import util.my_demo_portfolio as portfolio
import modules.wa_email_lib as elib
import modules.wa_reports_lib as rlib
import modules.wa_doc_lib as dlib
import modules.wa_sentiment_lib as slib
import modules.wa_sql_lib as sqllib
# import modules.wa_json_lib as jlib
# import modules.wa_chat_lib as clib
import util.wa_util as utils

import logging
import base64

TEXT2TEXT_MODEL_LIST: List[str] = ["Bert", "Titan", "flan-t5-xxl"]
EMBEDDINGS_MODEL_LIST: List[str] = ["gpt-j-6b"]
DOC_CATEGORY_LIST: List[str] = ["Macroeconomic","Banking Sector", "Company Financial Statements", "Compay Market News", "Company Earning Call Transcripts"]
DOC_ENTITY_LIST: List[str] = ["HSBC", "SCB", "Barclays", "..."]

#db = SQL("sqlite:///wealth.db")

#openai.api_type = "azure"
#openai.api_base = "https://bfslabopenai.openai.azure.com/"
#openai.api_version = "2023-05-15"
#openai.api_key = os.getenv("OPENAI_API_KEY")


#filemode='w'
#format='%(levelname)s:%(message)s'
#format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p'

def main():
    #load_dotenv()
    #conn = st.connection("wealth_db", type='sql')
    #lite_conn = sqlite3.connect("wealth.db")
    #pg_conn = st.connection("postgresql", type="sql")

    logging.basicConfig(filename='wa.log', encoding='utf-8', level=logging.INFO)
    fh = logging.FileHandler('wa-fh-spam.log')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger = logging.getLogger(__name__)

    logger.info("#######################################")
    logging.debug('This message should appear on the console')
    logging.info('So should this')
    logging.warning('And this, too')

    # Page title
    st.set_page_config(page_title="Wealth Advisor Assist", page_icon="🦜", layout='wide')
    st.title("👩‍💻 Wealth Advisor Assist")
    st.caption(f"🚀 Powered by :blue[Gen AI]")

    ##Display Header Tabs and Client Portfolio
    # active_tab = option_menu(None, ["Document Assist", "Sentiment Assist", "Query Assist", "Report Assist", "SQL Assist", "Email Assist", "JSON Assist", "Chat Assist"], 
    active_tab = option_menu(None, ["Document Assist", "Search Assist", "Sentiment Assist","Query Assist", "Report Assist", "Email Assist"], 
        icons=['house', 'cloud-upload', "list-task", 'gear', 'bank', 'box', 'cloud', 'chat'], 
        menu_icon="cast", default_index=0, orientation="horizontal")

    col1, col2 = st.columns([3,1])
    with col2:
        client = st.selectbox(label='Client Portfolio', options=portfolio.CLIENT_LIST)
        st.pyplot(portfolio.show_portfolio(client))
    
    with col1:

        if active_tab == "Document Assist":
            st.subheader("Document Feeds for the day")
            if 'key' not in st.session_state:
                st.session_state['rerun_counter'] = 0

            #df=pd.read_csv("data/Feeds.csv")
            ###conn.query('''CREATE TABLE IF NOT EXISTS documents (doc_id TEXT PRIMARY KEY, category TEXT, entity TEXT, doc_name TEXT, doc_source TEXT, sentiment_positive REAL, sentiment_negative REAL, sentiment_neutral REAL)''')
            #df = conn.query(sql)

            df = dlib.get_docs()
            #df = pd.DataFrame(docs, columns=["Category", "Entity", "File Name", "Source"])
            st.dataframe(df, use_container_width=True)

            with st.form("my_form"):
                uploaded_doc_category = st.selectbox('Document Category', DOC_CATEGORY_LIST)
                uploaded_doc_entity = st.selectbox('Entity', DOC_ENTITY_LIST)
                uploaded_doc = st.file_uploader("Upload Document", key='file_upload_widget', type=("txt", "pdf"), accept_multiple_files=False)
                #bytes_data = uploaded_doc.read()
                # st.form_submit_button('Upload New', type="primary", on_click=upload_file(conn, uploaded_doc_category, uploaded_doc_entity))
                if st.form_submit_button('Upload New', type="primary"):
                    with st.spinner("Uploading doc..."):
                        dlib.upload_file(st.session_state.file_upload_widget, uploaded_doc_category, uploaded_doc_entity, "upload") 
                        st.success("File uploaded successfully")

            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
            col1.empty()
            col2.empty()
            col3.empty()
            col7.button("Enable Feed", type="primary") 
            col8.button("Add Link", type="primary") 

        elif active_tab == "Sentiment Assist":

            logging.debug('SA -- This message should appear on the console')
            logging.info('SA ---So should this')
            logging.warning('SA ---And this, too')

            st.subheader("Sentiment Analysis Dashboard")

            st.caption(f":blue[Macroeconomic and Sector Outlook]")

            sentiment_list = slib.get_all_sentiments()
            df=pd.DataFrame(sentiment_list)
            print(df)
            generic_df = df[df.entity.isnull()].drop(columns=["entity", "count"])
            entity_specific_df = df[df["entity"].notnull()].drop(columns=["count"])
            print(entity_specific_df.entity.unique())
            #st.dataframe(sentiment_list, use_container_width=True)
            #list0 = [generic_df.columns.values.tolist()] + generic_df.values.tolist()
            st.dataframe(generic_df) #, use_container_width=True)
            # Show the chart  
            st.altair_chart(slib.generate_chart(generic_df), use_container_width=True) 

            st.caption(f":blue[Company Specific Outlook]")

            st.dataframe(entity_specific_df) # use_container_width=True)
            company = st.selectbox('Select a company', 
                                    entity_specific_df.entity.unique(), # ['Barclays', 'HSBC', 'SCB'],
                                    index=None,
                                     placeholder="Select Entity..") 

            if company is not None:
                #st.write('You selected:', company)
                df4 = entity_specific_df[entity_specific_df["entity"] == company].drop(columns=["entity"])
                # Show the chart with the filtered data  
                st.altair_chart(slib.generate_chart(df4), use_container_width=True) 
            
            st.subheader("Generate Sentiment")
            # Allow the user to upload a text file
            uploaded_files = st.file_uploader("Upload Your Files", type=("txt", "pdf"), accept_multiple_files=True) 

            if st.button("Process"):
                with st.spinner("Processing"):
                    raw_text=""
                    if uploaded_files:
                        for uploaded_file in uploaded_files:
                            st.write("Filename: ", uploaded_file.name)
                            #check if uploaded file type is pdf
                            if uploaded_file.name.endswith(".pdf"):
                                raw_text += utils.load_pdf_text(uploaded_file)
                            elif uploaded_file.name.endswith(".txt"):
                                raw_text += uploaded_file.read().decode("utf-8")

                    classifier=pipeline(task="sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
                    preds=classifier(raw_text[:500])
                    print(preds)
                    preds2=[{"score": round(pred["score"], 4), "label": pred["label"]} for pred in preds]
                    print(*preds2, sep="\n")
                    st.info(f'Sentiment: {preds2}')

        elif active_tab == "Query Assist":
            st.subheader("Common Queries")   
            
            # Retrieve questions and answers from DB  
            #c.execute("SELECT question, answer FROM queries")  
            #rows = c.fetchall()
            #rows = conn.query("SELECT question, answer FROM queries")
            #questions, answers = zip(*rows)  
            
            questions = [  
                "What is the outlook for GDP growth in the UK?",  
                "What are the main factors contributing to the slowdown in economic activity?",  
                "What is the outlook for business investment?",  
                "What was the trend in global financial wealth over the past few years?",  
                "What was the impact of rising costs on wealth managers' profitability?",  
            ]  
            answers = [  
                "According to the KPMG economic outlook report from September 2023, the outlook for UK GDP growth is sluggish. KPMG expects growth to slow over the remainder of the year and into 2024, with real GDP growth slowing from 4.1% in 2022 to just 0.4% in 2023 and 0.3% in 2024. The report notes that weakening global economic conditions, coupled with the lagged impact of higher interest rates, could make it difficult for the UK economy to keep its head above water in the second half of the year. Risks to the forecast are skewed to the downside due to uncertainty around the upcoming general election, strength of demand, and the future trajectory of interest rates.",  
                "According to the context, the main factors contributing to the slowdown in economic activity are the weakening global economy, higher interest rates across the world's largest economies, sustained weakness in Germany's manufacturing sector, lacklustre growth in the Eurozone, and a sharp slowdown in activity in the US. There are also concerns about a potential slowdown in China and the impact on global trade volumes, which have already contracted for the third consecutive month. Additionally, trade conditions may worsen further in the second half of the year due to Brexit and non-tariff barriers faced by businesses.",  
                "The outlook for business investment is subdued against the backdrop of higher borrowing costs and uncertainty. Corporate bond yields remain close to the peak reached in the aftermath of the mini budget last year, while the Bank of England’s Decision Maker Panel survey found that interest rates were expected to reduce business investment by 8% over the coming year. In addition, 17% of businesses surveyed by the ONS attribute the current headwinds to capex to uncertainty about demand or business prospects. Looking ahead, KPMG expects next year to also be partially influenced by uncertainty around the upcoming general election, with investment decisions potentially postponed until there is more clarity on future policy direction. Combined with the weak outlook for residential investment, KPMG's forecast envisages total investment growth slowing to 2.7% in 2023 and just 0.5% next year.",  
                "Global financial wealth experienced steady expansion for nearly 15 years following the 2007-2008 financial crisis. However, in 2022, it declined by 4% to $255 trillion due to factors such as rampant inflation, poor equity market performance, fluctuating investor confidence, and geopolitical uncertainty. Despite this, global financial wealth is expected to rebound in 2023 by roughly 5% to reach $267 trillion. The five-year CAGR forecast for financial wealth is positive, at 5.3%, a rate that would enable growth to reach $329 trillion by the end of 2027.",  
                "Rising costs had a negative impact on the profitability of wealth managers globally. Pretax profit margins for wealth managers decreased by an average of 2.3 bps in 2022, driven mainly by players in the Asia-Pacific region (-5.5 bps) and North America (-3.1 bps). This decline in profitability can be attributed to the rising costs, including personnel, tech, and operations spending. However, certain players in Western Europe and Latin America were able to increase their profit margins.",  
            ]  

            for question, answer in zip(questions, answers):  
                with st.expander(question):  
                    st.write(answer)

            form_input = st.text_input('Enter Query')
            submit = st.button("Submit")

            if submit:
                result, refs = dlib.get_answer_from_docs_faiss(form_input)
                #result = qa({"question": form_input})  
                print(result)
                #answer = result['answer']  
                #source_documents = result['pdf_names']  

                st.info(result) 
                st.warning(refs)
        
        elif active_tab == "Report Assist":
            st.subheader("Generate Portfolio Reports")
            st.caption(f"Populate Report Data utilising GenAI")

            form_input = st.text_input('Enter Report ID')
            submit = st.button("Generate report", type="primary")

            if submit:  
                rlib.generate_report() 
                with open("report.docx", "rb") as f:  
                    docx_file = f.read()  
                b64 = base64.b64encode(docx_file).decode("utf-8")  
                href = f"<a href='data:application/octet-stream;base64,{b64}' download='report.docx'>Download file</a>"  
                st.markdown(href, unsafe_allow_html=True) 

            st.subheader("Generate Summary Reports")

            uploaded_file = st.file_uploader("Select a PDF", type=['pdf'])
            upload_button = st.button("Upload", type="primary")
            if upload_button:
                with st.spinner("Uploading..."):
                    upload_response = rlib.save_file(name=uploaded_file.name, file_bytes=uploaded_file.getvalue())
                    st.success(f"Uploaded {uploaded_file.name} as {upload_response}")
                    st.session_state.has_document = True
                    st.session_state.file_name = upload_response
                        
            if 'has_document' in st.session_state: #see if document has been uploaded
                return_intermediate_steps = st.checkbox("Return intermediate steps", value=True)
                summarize_button = st.button("Summarize", type="primary")
                if summarize_button:
                    st.subheader("Combined summary")
                    with st.spinner("Running..."):
                        response_content = rlib.get_summary(name=st.session_state.file_name, return_intermediate_steps=return_intermediate_steps)
                    if return_intermediate_steps:
                        st.write(response_content["output_text"])
                        st.subheader("Section summaries")
                        for step in response_content["intermediate_steps"]:
                            st.write(step)
                            st.markdown("---")
                    else:
                        st.write(response_content)

            # report_data = pd.DataFrame(
            #     np.array([[20,15,15], [20,10,25], [20,25,15], [0,20,0]]), columns=['Virat Sharma','Sachin Ganguly','Rohit Kohli'],
            #     index=["SCB","HSBC","Barclays","GS", "Morgan Stanley", "DBS"]
            # )

            # scrip = 'SCB', 'HSBC', 'Barclays', 'GS', 'Morgan Stanley', 'DBS'
            # exposure = [15, 10, 25, 20, 10, 20]

            # chart_data = pd.DataFrame(
            #     {
            #         "scrip": scrip,
            #         "exposure": exposure
            #     }
            # )

            # dfchart=alt.Chart(chart_data).mark_bar().encode(
            #     x='scrip:O',
            #     y='exposure:Q',

            # )
            # st.altair_chart(dfchart, use_container_width=False)

            # my_chart_data = pd.DataFrame(
            #     np.array([[90,5,5], [80,10,10], [10,20,70], [5,10,85]]), columns=['Positive','Neutral','Negative'],
            #     index=["SCB-Market","SCB-Internal","SCB-Analyst","Generic"]
            # )
            # print(my_chart_data)
            # mydata = pd.melt(my_chart_data.reset_index(), id_vars=["index"], var_name="Sentiment")
            # print(mydata['Sentiment'].unique())

            # sentu_chart = alt.Chart(mydata).mark_bar().encode(
            #     x=alt.X("value", type="quantitative", title="Sentiment"),
            #     y=alt.Y("index", type="nominal", title="category"),
            #     color=alt.Color("Sentiment", 
            #                     scale=alt.Scale(
            #                         domain=mydata['Sentiment'].unique(), 
            #                         range=['green', 'orange', 'red']) )
            # )

            # st.altair_chart(sentu_chart, use_container_width=True)
        elif active_tab == "SQL Assist":
            st.subheader("QnA Over Structured Data")
            st.caption(f"NL to SQL using LLM")
            form_input = st.text_input('Enter Query')
            submit = st.button("Submit")

            if submit:
                result = sqllib.get_answer(form_input)  
                print(result)
                answer = result  
                source_documents = result.metadata['sql_query']  
                data_df=result.metadata['result']
                cols=result.metadata['col_keys']
                st.info(answer) 
                st.warning(source_documents)
                #st.error(data_df)

                data = pd.DataFrame(data_df,  columns=cols)
                print(data)

                try:

                    #mi_data = data[data.state_code == "MI"].drop(columns=["activity_year"])
                    #oh_data = data[data.state_code == "OH"].drop(columns=["activity_year"])
                    if "activity_year" in list(data.columns):
                        df = pd.DataFrame(data, columns=['activity_year','state_code','description', 'count'])
                        dfchart=alt.Chart(df).mark_bar().encode(
                            x='description:O',
                            y='count:Q',
                            color='state_code:N',
                            xOffset='state_code',
                            column='activity_year'
                        )
                        st.altair_chart(dfchart, use_container_width=False)

                    # mychart=alt.Chart(data).mark_bar().encode(
                    #     x='description:O',
                    #     y='count:Q',
                    #     color='state_code',
                    #     column='state_code'
                    # )
                    #st.altair_chart(mychart, use_container_width=False)

                    #st.bar_chart(mi_data, x="description", y="count", use_container_width=False)
                    #st.bar_chart(oh_data, x="description", y="count", use_container_width=False)
                except Exception as e:
                    print("Exception encountered: ",e,)

                st.dataframe(data)
                # data = pd.DataFrame(data_df)
                # print(data)
                # mi_data = data[data.state_code == "MI"].drop(columns=["activity_year"])
                # oh_data = data[data.state_code == "OH"].drop(columns=["activity_year"])
                # print(oh_data)

                # try:
                #     st.bar_chart(mi_data, x="action_taken", y="count", use_container_width=False)
                #     st.bar_chart(oh_data, x="action_taken", y="count", use_container_width=False)
                # except:
                #     print("Error in Graph")
        elif active_tab == "Email Assist":
            st.subheader("QnA over Email Messages")
            df = elib.get_emails()
            #st.dataframe(df)

            # loop through the rows using iterrows()
            #for question, answer in zip(questions, answers):  
            for index, row in df.iterrows():
                subject = row['subject']
                sender = row['sender'] 
                with st.expander(f"{sender} - :orange[{subject}]", expanded=False):  
                    st.write(row['summary'])
                    #st.write(elib.get_answer_from_email_faiss(f"Summarize the email from {sender} on the subject {subject}"))

            st.subheader("Upload Email")
            with st.form("email_form"):
                uploaded_mail = st.file_uploader("Upload Email Message", key='email_upload_widget',  accept_multiple_files=False)
                if st.form_submit_button('Upload', type="primary"):
                    with st.spinner("Uploading email..."):
                        data = elib.upload_email(name=uploaded_mail.name, file_bytes=uploaded_mail.getvalue())
                        #st.success(data)
                        st.warning("Upload successful. You can query your email now")

            st.subheader(f"Get Insights")

            email_query = st.text_input('Enter your query')
            submit = st.button("Submit", type="primary")

            if submit:
                with st.spinner("Running..."):
                    result = elib.get_answer_from_email_faiss(email_query)  
                    #result = elib.get_answer_from_email_pg(email_query)  
                    print(result)
                    answer = result  
                    st.info(answer) 
        # elif active_tab == "JSON Assist":
        #     st.subheader("QnA over JSON")

        #     form_input = st.text_input('Enter Query')
        #     submit = st.button("Submit")

        #     if submit:
        #         #result = jlib.get_answer_from_json(form_input)
        #         result = clib.get_answer_from_tool(form_input)

        #         #result = qa({"question": form_input})  
        #         print(result)
        #         #answer = result['answer']  
        #         #source_documents = result['pdf_names']  

        #         st.info(result) 
        # else:
        #     st.subheader("Chat Bot")
        #     #chat_index = dlib.get_faiss_index()
        #     if "messages" not in st.session_state.keys(): # Initialize the chat messages history
        #         st.session_state.messages = [
        #             {"role": "assistant", "content": "Ask me a question about Streamlit's open-source Python library!"}
        #         ]

        #     if "chat_engine" not in st.session_state.keys(): # Initialize the chat engine
        #             st.session_state.chat_engine = clib.get_chat_engine()
        #             #chat_index.as_chat_engine(chat_mode="condense_question", verbose=True)

        #     if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
        #         st.session_state.messages.append({"role": "user", "content": prompt})

        #     for message in st.session_state.messages: # Display the prior chat messages
        #         with st.chat_message(message["role"]):
        #             st.write(message["content"])

        #     # If last message is not from assistant, generate a new response
        #     if st.session_state.messages[-1]["role"] != "assistant":
        #         with st.chat_message("assistant"):
        #             with st.spinner("Thinking..."):
        #                 response = st.session_state.chat_engine.chat(prompt)
        #                 st.write(response.response)
        #                 message = {"role": "assistant", "content": response.response}
        #                 st.session_state.messages.append(message) # Add response to message history

if __name__ == '__main__':
    main()