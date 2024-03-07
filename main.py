from classification import TableProcessor # 导入TableProcessor
from tqdm import tqdm
import os
import glob


input_folder = 'Table Data'
output_folder = '表格分类3-6 run1/'

TableProcessor = TableProcessor()

def Run_One_Folder():
    for filename in tqdm(os.listdir(input_folder), desc=f"Processing HTML File"):
        if filename.endswith('.html'):
            input_html = os.path.join(input_folder, filename)
            TableProcessor.extract_tables(input_html, output_folder, filename)
            TableProcessor.output_statistics(output_folder, filename)
            TableProcessor.output_debug(output_folder, filename)

Run_One_Folder()

'''
extract_tables(html_file_path, output_folder, filename)
参数: html_file_path: 字符串，代表HTML文件的路径。
     output_folder: 字符串，代表输出文件夹的路径。
     filename: 字符串，代表HTML文件的文件名。

output_statistics(output_folder, filename)
参数: output_folder: 字符串，代表输出文件夹的路径。
     filename: 字符串，代表HTML文件的文件名。

output_debug(output_folder, filename)
参数: output_folder: 字符串，代表输出文件夹的路径。
     filename: 字符串，代表HTML文件的文件名。
'''
