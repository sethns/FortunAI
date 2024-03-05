import os

from PyPDF2 import PdfReader

import pandas as pd
import vanna as vn

def load_excel_data(file_name: str) -> pd.DataFrame:
  return pd.read_excel(file_name)

#for pdf in pdf_docs:
def load_pdf_text(file_name: str):  
    text = ""
    pdf_reader = PdfReader(file_name)
    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if(page_text) :
            text += page_text
    return text

def read_all_files_in_folder(folder_path):
  """Reads all files in a folder.

  Args:
    folder_path: The path to the folder.

  Returns:
    A list of all files in the folder.
  """

  files = []
  for file in os.listdir(folder_path):
    file_path = os.path.join(folder_path, file)
    files.append(file_path)
    print(file_path)
  return files

def dbfunction(conn, sql, rerun_counter):

    vn.train(question="Compare revenue numbers from for 2022 for different airline companies", sql="""
        SELECT i.cik, i.company_name, r.period_start_date, r.period_end_date, r.measure_description, TO_NUMERIC(r.value) AS value
        FROM cybersyn.sec_cik_index AS i
        JOIN cybersyn.sec_report_attributes AS r ON (r.cik = i.cik)
        WHERE i.sic_code_description = 'AIR TRANSPORTATION, SCHEDULED'
        AND r.statement = 'Income Statement'
        AND r.period_end_date = '2022-12-31'
        AND r.covered_qtrs = 4
        AND r.metadata IS NULL
        AND r.measure_description IN ('Total operating revenues', 'Total operating revenue');
        """)
    
    df = conn.query(sql)
    return df