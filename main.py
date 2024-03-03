from classification import TableProcessor
from tqdm import tqdm
from bs4 import BeautifulSoup
import re
import os

input_folder = 'exam type table/ALL'
output_folder = 'exam type table/ALL'

classify = TableProcessor(input_folder,output_folder)


def Run_Files():
    for filename in tqdm(os.listdir(input_folder), desc=f"Processing HTML File"):
        if filename.endswith('.html'):
            input_html = os.path.join(input_folder, filename)
            classify.extract_tables(input_html,filename)
            classify.output_statistics(filename)
            
Run_Files()