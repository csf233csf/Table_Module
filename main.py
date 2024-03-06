from classification import TableProcessor
from tqdm import tqdm
import os
import glob


input_folder = 'Table Data'
output_folder = '表格分类3-6 run1/'

foldertest = 'Table Test Runs'

TableProcessor = TableProcessor()

def Run_One_Folder():
    for filename in tqdm(os.listdir(input_folder), desc=f"Processing HTML File"):
        if filename.endswith('.html'):
            input_html = os.path.join(input_folder, filename)
            TableProcessor.extract_tables(input_html,output_folder, filename)
            TableProcessor.output_statistics(output_folder, filename)
            TableProcessor.output_debug(output_folder,filename)

# 开始跑路径下所有的文件
Run_One_Folder()
