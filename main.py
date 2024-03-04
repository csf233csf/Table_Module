from classification import TableProcessor
from tqdm import tqdm
from bs4 import BeautifulSoup
import re
import os
import glob


input_folder = 'exam type table/ALL'
output_folder = 'output'

foldertest = 'Table Test Runs'
# Passing the classes
classify = TableProcessor(input_folder,output_folder)

def Run_One_Folder():
    for filename in tqdm(os.listdir(input_folder), desc=f"Processing HTML File"):
        if filename.endswith('.html'):
            input_html = os.path.join(input_folder, filename)
            classify.extract_tables(input_html,filename)
            classify.output_statistics(filename)
'''
def run_multi_folder(input_folder):
    for dirpath, dirnames, filenames in tqdm(os.walk(input_folder), desc="Walking through folders"):
        for filename in filenames:
            if filename.endswith('.docx.out.aspose_res.html'):
                input_html = os.path.join(dirpath, filename)
                print(dirpath)
                output_folder = dirpath
                # 假设 classify.extract_tables 和 classify.output_statistics 是你要执行的操作
                classify.extract_tables(input_html, filename)
                classify.output_statistics(filename)
run_multi_folder(foldertest) # Processes
'''

Run_One_Folder()