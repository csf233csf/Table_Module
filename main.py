from classification import TableProcessor
from splitter import SplitAnswerTable
from tqdm import tqdm
import os
import glob
from bs4 import BeautifulSoup

input_folder = 'Table Data'
output_folder = '表格分类3-6 run1/'

TableProcessor = TableProcessor()


def gather_tables(input_html, filename):
     with open(input_html, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'lxml')
     tables = soup.find_all('table')
     all_tables = []
     for table in tqdm(tables, desc=f"Gathering Tables from: {filename}"):
        if table.find('img') or table.find('table'):
            continue
        else:
            all_tables.append(table)
     
     return all_tables
            
def write_table(output,list):
    with open(output, 'w') as f:
        for table in list:
            f.write(str(table))
            f.write('\n\n')


def Run_One_Folder():
    for filename in tqdm(os.listdir(input_folder), desc=f"Processing HTML File"):
        if filename.endswith('.html'):
            input_html = os.path.join(input_folder, filename)
            TableProcessor.extract_tables(input_html, output_folder, filename)
            TableProcessor.output_statistics(output_folder, filename)
            TableProcessor.output_debug(output_folder, filename)


def SingleTypeTable(input, output, table_type):
     for filename in tqdm(os.listdir(input), desc=f"Processing HTML File"):
          table_ele = []
          if filename.endswith('.html'):
               input_html = os.path.join(input, filename)
               table_ele = gather_tables(input_html, filename)
               if table_type == 'Long':
                    for table in tqdm(table_ele, desc=f"Filtering {table_type} Tables from: {filename}"):
                         long_tables = [table for table in table_ele if TableProcessor.is_long_table(table)]
                    write_table(os.path.join(output, filename.replace('.html','processed.html')), long_tables)


if __name__ == '__main__':
     Run_One_Folder()

     #SingleTypeTable(input_folder,output_folder, 'Long')

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
